import panel
import logging
import time

from bokehplots import EEG_p
from data import access

"""
LOGGING
"""
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

"""
METADATA
"""
metadata = access.parse_subject_data()
min_age = min([int(subject["age"]) for subject in metadata["subjects"]])
max_age = max([int(subject["age"]) for subject in metadata["subjects"]])


def sex_to_string(sex):
    if sex == "m":
        return "Male"
    else:
        return "Female"


def filter_subjects(sex, age):
    return {
        f"Subject {subject['id']}; {sex_to_string(subject['sex'])}; {subject['age']}": subject[
            "id"
        ]
        for subject in metadata["subjects"]
        if int(subject["age"]) >= age[0]
        and int(subject["age"]) <= age[1]
        and subject["sex"] in sex
    }


"""
CSS
"""
css = """
.bk.panel-widget-box {
  background: #f0f0f0;
  border-radius: 5px;
  border: 1px black solid;
}
.bk-root .bk.title-button .bk-btn {
  background: #000000;
  text-align: left;
  border: 0px black solid;
  color: white;
  font-size: 16pt;
  font-family: monospace;
}
.bk-root .bk.main-button .bk-btn {
  color: white;
  font-size: 12pt;
  font-family: monospace;
}
.bk-root .bk.famous-button .bk-btn {
  border: 1px #0900ff solid;
  color: #0900ff;
}
.bk-root .bk.scrambled-button .bk-btn {
  border: 1px #930791 solid;
  color: #930791;
}
.bk-root .bk.unfamiliar-button .bk-btn {
  border: 1px #03f0d3 solid;
  color: #03f0d3;
}
"""

panel.extension(raw_css=[css])

"""
BOKEH
"""
bokeh_pane = panel.pane.Bokeh(EEG_p)


"""
PLOTLY
"""
import numpy as np
import plotly.graph_objs as go

xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-((x - 1) ** 2) - y**2) - (x**3 + y**4 - x / 5) * np.exp(
    -(x**2 + y**2)
)

surface = go.Surface(z=z)
layout = go.Layout(
    title="Plotly 3D Plot",
    autosize=False,
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50),
)
fig = dict(data=[surface], layout=layout)

plotly_pane = panel.pane.Plotly(fig)

"""
TOP BAR
"""
change_subject_button = panel.widgets.Button(
    name="Change subject",
    button_type="success",
    sizing_mode="stretch_height",
    css_classes=["main-button"],
)
title = panel.widgets.Button(
    name="A multi-subject multi-modal human neuroimaging dataset",
    sizing_mode="stretch_both",
    css_classes=["title-button"],
)
topbar = panel.Row(
    title,
    width_policy="max",
    background="#000000",
)

link_code = """
window.location.href="https://www.nature.com/articles/sdata20151"
"""
title.js_on_click(code=link_code)


# Whole
def first_page(event):

    # Clear previous page
    layout.clear()

    # Remove select subject button
    if len(topbar) > 1:
        topbar.pop(1)
        topbar.pop(1)

    # Add topbar
    layout.append(topbar)

    # Add subject select with spacing
    layout.append(panel.layout.VSpacer())
    layout.append(subject_selection)
    layout.append(panel.layout.VSpacer())

change_subject_button.on_click(first_page)

"""
UI FIRST PAGE
"""
title = panel.pane.Str(
    "Subject selection",
    align="center",
    style={"font-size": "12pt"},
)

# Sex select
sex_select_title = panel.pane.Str(
    "Sex:",
    align="center",
)
sex_select = panel.widgets.CheckButtonGroup(
    value=["f", "m"],
    options={"Female": "f", "Male": "m"},
)


def change_sex_select(event):
    subject_select.options = filter_subjects(event.new, age_select.value)


sex_select.param.watch(change_sex_select, ["value"], onlychanged=True)

# Age select
age_select_title = panel.pane.Str("Age:", align="center", margin=25)
age_select_value = panel.pane.Str(f"{min_age}...{max_age}", align="center", margin=-20)
age_select = panel.widgets.IntRangeSlider(
    start=min_age, end=max_age, value=(min_age, max_age), step=1, show_value=False
)


def change_age_select(event):
    age_select_value.object = f"{event.new[0]}...{event.new[1]}"
    subject_select.options = filter_subjects(sex_select.value, event.new)


age_select.param.watch(change_age_select, ["value"], onlychanged=True)

# Subject select
subject_select_title = panel.pane.Str("Subject:", align="center", margin=25)
subject_select = panel.widgets.Select(
    options=filter_subjects(sex_select.value, age_select.value),
)

# Start analysis button
start_analysis_button = panel.widgets.Button(
    name="Start analysis", button_type="success", margin=25, css_classes=["main-button"]
)


def start_analysis(event):

    # Add selected subject as subtitle
    topbar.append(
        panel.pane.Str(
            list(subject_select.options.keys())[subject_select.value],
            style={"color": "white", "font-size": "15pt"},
        )
    )

    # Add change subject button
    topbar.append(change_subject_button)

    # Change page
    second_page(subject_select.value)


start_analysis_button.on_click(start_analysis)

# Whole
subject_selection = panel.Column(
    title,
    sex_select_title,
    sex_select,
    age_select_title,
    age_select_value,
    age_select,
    subject_select_title,
    subject_select,
    start_analysis_button,
    align="center",
    width=500,
    height=500,
    css_classes=["panel-widget-box"],
)

"""
UI SECOND PAGE
"""

# Run select
run_select = panel.widgets.Select(
    options={"Run " + str(i): i - 1 for i in range(1, 7)}, value=0, align="center"
)

# PSD toggle
psd_button = panel.widgets.Toggle(name="PSD", width_policy="min", align="center")

# AVG toggle
avg_text = panel.widgets.StaticText(name="", value='Averaging over events:', align="center")
avg_button = panel.widgets.Toggle(name="AVG", width_policy="max", align="center")

# AVG sliders
tmin_slider = panel.widgets.FloatSlider(
    name="tmin", start=-1.5, end=0, step=0.01, value=-0.5, align="center"
)
tplus_slider = panel.widgets.FloatSlider(
    name="tplus", start=0, end=1.5, step=0.01, value=0.5, align="center"
)

# Event select toggles
famous_toggle = panel.widgets.Toggle(name="Famous", css_classes=["famous-button"], width=100, align="center")
scrambled_toggle = panel.widgets.Toggle(name="Scrambled", css_classes=["scrambled-button"], width=100, align="center", margin=(5, -20, 5, 10))
unfamiliar_toggle = panel.widgets.Toggle(name="Unfamiliar", css_classes=["unfamiliar-button"], width=100, align="center")


# Whole
def second_page(subject_id):
    
    # Clear first page
    layout.clear()

    # Re-add topbar
    layout.append(topbar)

    # Start loading animation
    layout.append(panel.layout.VSpacer())
    layout.loading=True

    # Create Plotly plots

    # Create Bokeh plots

    # Set layout
    time.sleep(2)
    layout.loading=False
    layout.pop(1)
    layout.append(panel.Row(run_select, psd_button, panel.layout.HSpacer(), avg_text, tmin_slider, tplus_slider, famous_toggle, scrambled_toggle, unfamiliar_toggle, avg_button))

"""
LAYOUT
"""
layout = panel.Column(
    sizing_mode="stretch_both",
)
first_page(0)
layout.servable()
