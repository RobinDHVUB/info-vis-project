import panel
import logging
import enum

from data import access
from bokehplots import avg_plots

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
EEG_groups_assignment = {}
for EEG_channel, EEG_type in zip(metadata["eeg_names"], metadata["eeg_types"]):
    current = (
        EEG_groups_assignment[EEG_type] if EEG_type in EEG_groups_assignment else []
    )
    EEG_groups_assignment[EEG_type] = current + [EEG_channel]
MEG_groups_assignment = {}
for MEG_channel, MEG_type in zip(metadata["meg_names"], metadata["meg_types"]):
    current = (
        MEG_groups_assignment[MEG_type] if MEG_type in MEG_groups_assignment else []
    )
    MEG_groups_assignment[MEG_type] = current + [MEG_channel]


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
  border: 1px #ff0000 solid;
  color: #ff0000;
}
.bk-root .bk.scrambled-button .bk-btn {
  border: 1px #00BFFF solid;
  color: #00BFFF;
}
.bk-root .bk.unfamiliar-button .bk-btn {
  border: 1px #0000FF solid;
  color: #0000FF;
}
"""

panel.extension("plotly", raw_css=[css])

"""
PLOTLY
"""
import plotly.express as px

fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])

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
            list(subject_select.options.keys())[subject_select.value-1],
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
# Modes
class ViewMode(enum.Enum):
    TOTAL = 1
    WINDOW = 2


current_view_mode = ViewMode.TOTAL


class DataMode(enum.Enum):
    TIME = 1
    FREQUENCY = 2


# Data
runs = []
downsampled_runs = []
EEG_group_avgs = None
EEG_group_psds = None
MEG_group_avgs = None
MEG_group_psds = None
downsampled_events = None


def get_subject_data(subject_id):
    global EEG_group_avgs
    global EEG_group_psds
    global MEG_group_avgs
    global MEG_group_psds
    global downsampled_events

    # Runs
    for i in range(1, 7):
        run, downsampled_run = access.parse_run(subject_id, i)
        runs.append(run)
        downsampled_runs.append(downsampled_run)

    # Averages
    (
        EEG_group_avgs,
        EEG_group_psds,
        MEG_group_avgs,
        MEG_group_psds,
        downsampled_events,
    ) = access.group_averages(
        downsampled_runs, EEG_groups_assignment, MEG_groups_assignment
    )


current_data_mode = DataMode.TIME

# Run select
run_select = panel.widgets.Select(
    options={"Run " + str(i): i - 1 for i in range(1, 7)}, value=0, align="center"
)

# PSD toggle
psd_button = panel.widgets.Toggle(name="PSD", width_policy="min", align="center")

# AVG toggle
avg_text = panel.widgets.StaticText(
    name="", value="Averaging over events:", align="center"
)
avg_button = panel.widgets.Toggle(name="AVG", width_policy="max", align="center")

# AVG sliders
tmin_slider = panel.widgets.FloatSlider(
    name="tmin", start=-1.5, end=0, step=0.01, value=-0.5, align="center"
)
tplus_slider = panel.widgets.FloatSlider(
    name="tplus", start=0, end=1.5, step=0.01, value=0.5, align="center"
)

# Event select toggles
famous_toggle = panel.widgets.Toggle(
    name="Famous", css_classes=["famous-button"], width=100, align="center"
)
scrambled_toggle = panel.widgets.Toggle(
    name="Scrambled",
    css_classes=["scrambled-button"],
    width=100,
    align="center",
    margin=(5, -20, 5, 10),
)
unfamiliar_toggle = panel.widgets.Toggle(
    name="Unfamiliar", css_classes=["unfamiliar-button"], width=100, align="center"
)


# Whole
def second_page(subject_id):

    # Clear first page
    layout.clear()

    # Re-add topbar
    layout.append(topbar)

    # Start loading animation
    layout.append(panel.layout.VSpacer())
    layout.loading = True

    # Load data
    get_subject_data(subject_select.value)

    # Create Bokeh plots
    EEG_p, MEG_p = avg_plots(
        EEG_group_avgs[0], MEG_group_avgs[0], downsampled_events[0], logger
    )

    # Create Bokeh plots

    # Set layout
    layout.append(
        panel.Column(
            panel.Row(
                run_select,
                psd_button,
                panel.layout.HSpacer(),
                avg_text,
                tmin_slider,
                tplus_slider,
                famous_toggle,
                scrambled_toggle,
                unfamiliar_toggle,
                avg_button,
            ),
            panel.Row(panel.pane.Bokeh(EEG_p, sizing_mode="stretch_both"), panel.pane.Plotly(fig), sizing_mode="stretch_both"),
            panel.Row(panel.pane.Bokeh(MEG_p, sizing_mode="stretch_both"), panel.pane.Plotly(fig), sizing_mode="stretch_both"),
            sizing_mode = "stretch_both"
        )
    )

    # Stop loading animation
    layout.pop(1)
    layout.loading = False


"""
LAYOUT
"""
layout = panel.Column(
    sizing_mode="stretch_both",
)
first_page(0)
layout.servable()
