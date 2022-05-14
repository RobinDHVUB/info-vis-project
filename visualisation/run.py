import panel
import logging
import enum

from bokehplots import avg_plots, window_plots, psd_plots
import data_access

# ----
# Logging
# ----
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# ----
# Metadata
# ----
metadata = data_access.parse_metadata()
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


# ----
# CSS
# ----
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


# ----
# Plotly
# ----
import plotly.express as px

fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])


# ----
# Top bar
# ----
change_subject_button = panel.widgets.Button(
    name="Change subject",
    button_type="success",
    sizing_mode="scale_height",
    css_classes=["main-button"],
)
main_title = panel.widgets.Button(
    name="A multi-subject multi-modal human neuroimaging dataset",
    sizing_mode="scale_width",
    css_classes=["title-button"],
)
topbar = panel.Row(
    main_title,
    sizing_mode="scale_width",
    background="#000000",
)

link_code = """
window.open("https://www.nature.com/articles/sdata20151", "_blank")
"""
main_title.js_on_click(code=link_code)


# Whole
def first_page(event):
    grid.objects = {}
    topbar.visible = False
    subject_selection.visible = False

    # Add topbar
    if len(topbar) > 1:
        topbar.pop(1)
        topbar.pop(1)
    grid[0, :] = topbar

    # Add subject selection pane
    grid[1:2, 0:5] = panel.Spacer()
    subject_selection.sizing_mode = "stretch_both"
    grid[3:12, 5:10] = subject_selection
    grid[9:12, 11:15] = panel.Spacer()

    subject_selection.visible = True
    topbar.visible = True


change_subject_button.on_click(first_page)


# ----
# First stage
# ----
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
initial_subject_select_options = filter_subjects(sex_select.value, age_select.value)
initial_subject_select_values = {
    id: description for description, id in initial_subject_select_options.items()
}
subject_select = panel.widgets.Select(
    options=initial_subject_select_options,
)

# Start analysis button
start_analysis_button = panel.widgets.Button(
    name="Start analysis", button_type="success", margin=25, css_classes=["main-button"]
)


def start_analysis(event):

    # Add selected subject as subtitle
    topbar.append(
        panel.pane.Str(
            initial_subject_select_values[subject_select.value],
            align="center",
            sizing_mode="scale_height",
            style={"color": "white"},
        )
    )

    # Add change subject button
    topbar.append(change_subject_button)

    # Change page
    second_page()


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
    css_classes=["panel-widget-box"],
    sizing_mode="stretch_height",
)


# ----
# Second stage
# ----

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
EEG_window_group_avgs = None
EEG_window_group_psds = None
MEG_window_group_avgs = None
MEG_window_group_psds = None


def get_subject_data():
    global EEG_group_avgs
    global EEG_group_psds
    global MEG_group_avgs
    global MEG_group_psds
    global downsampled_events

    # Runs
    logger.info(subject_select.value)
    for i in range(1, 7):
        run, downsampled_run = data_access.parse_run(subject_select.value, i)
        runs.append(run)
        downsampled_runs.append(downsampled_run)

    # Averages
    (
        EEG_group_avgs,
        EEG_group_psds,
        MEG_group_avgs,
        MEG_group_psds,
        downsampled_events,
    ) = data_access.group_averages(
        downsampled_runs, EEG_groups_assignment, MEG_groups_assignment
    )


current_data_mode = DataMode.TIME

# Run select
run_select = panel.widgets.Select(
    options={"Run " + str(i): i - 1 for i in range(1, 7)}, value=0, align="center"
)


def change_run(event):
    global current_data_mode
    global EEG_pane
    global EEG_lines
    global MEG_pane
    global MEG_lines
    run_idx = run_select.value

    # Loading
    EEG_pane.loading = True
    MEG_pane.loading = True

    if current_data_mode == DataMode.TIME:
        new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
            EEG_group_avgs[run_idx],
            MEG_group_avgs[run_idx],
            downsampled_events[run_idx],
            logger,
        )
    else:
        new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
            EEG_group_psds[run_idx], MEG_group_psds[run_idx], logger
        )

    EEG_pane.object = new_EEG_p
    MEG_pane.object = new_MEG_p

    # Stop loading
    EEG_pane.loading = False
    MEG_pane.loading = False


run_select.param.watch(change_run, ["value"], onlychanged=True)


# PSD toggle
psd_button = panel.widgets.Toggle(
    name="PSD", align="center", sizing_mode="stretch_width"
)


def change_data(event):
    global current_data_mode
    global current_view_mode
    global EEG_lines
    global MEG_lines
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds
    run_idx = run_select.value

    # Loading
    EEG_pane.loading = True
    MEG_pane.loading = True

    if current_data_mode == DataMode.TIME:
        current_data_mode = DataMode.FREQUENCY

        if current_view_mode == ViewMode.TOTAL:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                EEG_group_psds[run_idx], MEG_group_psds[run_idx], logger
            )
            avg_button.disabled = True
            tmin_slider.disabled = True
            tplus_slider.disabled = True
            famous_toggle.disabled = True
            scrambled_toggle.disabled = True
            unfamiliar_toggle.disabled = True
        else:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                EEG_window_group_psds, MEG_window_group_psds, logger
            )
    else:
        current_data_mode = DataMode.TIME
        enable_avg(0)
        if current_view_mode == ViewMode.TOTAL:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                EEG_group_avgs[run_idx],
                MEG_group_avgs[run_idx],
                downsampled_events[run_idx],
                logger,
            )
            tmin_slider.disabled = False
            tplus_slider.disabled = False
            famous_toggle.disabled = False
            scrambled_toggle.disabled = False
            unfamiliar_toggle.disabled = False
        else:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = window_plots(
                EEG_window_group_avgs,
                MEG_window_group_avgs,
                tmin_slider.value,
                tplus_slider.value,
                logger,
            )

    EEG_pane.object = new_EEG_p
    MEG_pane.object = new_MEG_p

    # Stop loading
    EEG_pane.loading = False
    MEG_pane.loading = False


psd_button.param.watch(change_data, ["value"], onlychanged=True)


# AVG toggle
avg_text = panel.widgets.StaticText(
    name="", value="Averaging over events:", align="center", sizing_mode="stretch_width"
)
avg_button = panel.widgets.Toggle(
    name="AVG", align="center", sizing_mode="stretch_width", disabled=True
)


def change_view(event):
    global current_view_mode
    global current_data_mode
    global EEG_lines
    global MEG_lines
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds
    run_idx = run_select.value

    # Loading
    EEG_pane.loading = True
    MEG_pane.loading = True

    # Event selection
    selected_events = [
        idx + 1
        for idx, value in enumerate(
            [
                famous_toggle.value,
                scrambled_toggle.value,
                unfamiliar_toggle.value,
            ]
        )
        if value
    ]

    # Re-calculate windows if needed
    if EEG_window_group_avgs is None:
        (
            EEG_window_group_avgs,
            EEG_window_group_psds,
            MEG_window_group_avgs,
            MEG_window_group_psds,
        ) = data_access.avg_windows(
            runs,
            selected_events,
            tmin_slider.value,
            tplus_slider.value,
            EEG_groups_assignment,
            MEG_groups_assignment,
        )

    if current_view_mode == ViewMode.TOTAL:
        current_view_mode = ViewMode.WINDOW
        new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = window_plots(
            EEG_window_group_avgs,
            MEG_window_group_avgs,
            tmin_slider.value,
            tplus_slider.value,
            logger,
        )
        run_select.disabled = True
        tmin_slider.disabled = True
        tplus_slider.disabled = True
        famous_toggle.disabled = True
        scrambled_toggle.disabled = True
        unfamiliar_toggle.disabled = True
    else:
        current_view_mode = ViewMode.TOTAL
        if current_data_mode == DataMode.TIME:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                EEG_group_avgs[run_idx],
                MEG_group_avgs[run_idx],
                downsampled_events[run_idx],
                logger,
            )
            tmin_slider.disabled = False
            tplus_slider.disabled = False
            famous_toggle.disabled = False
            scrambled_toggle.disabled = False
            unfamiliar_toggle.disabled = False
        else:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                EEG_group_psds[run_idx], MEG_group_psds[run_idx], logger
            )
        run_select.disabled = False

    EEG_pane.object = new_EEG_p
    MEG_pane.object = new_MEG_p

    # Stop loading
    EEG_pane.loading = False
    MEG_pane.loading = False


avg_button.param.watch(change_view, ["value"], onlychanged=True)


# AVG sliders
tmin_slider = panel.widgets.FloatSlider(
    name="tmin",
    start=-1.5,
    end=0,
    step=0.01,
    value=-0.5,
    align="center",
    sizing_mode="stretch_width",
)
tplus_slider = panel.widgets.FloatSlider(
    name="tplus",
    start=0,
    end=1.5,
    step=0.01,
    value=0.5,
    align="center",
    sizing_mode="stretch_width",
)


def reset_windows(event):
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds
    EEG_window_group_avgs = None
    EEG_window_group_psds = None
    MEG_window_group_avgs = None
    MEG_window_group_psds = None


tmin_slider.param.watch(reset_windows, ["value"], onlychanged=True)
tplus_slider.param.watch(reset_windows, ["value"], onlychanged=True)

# Event select toggles
famous_toggle = panel.widgets.Toggle(
    name="Famous",
    css_classes=["famous-button"],
    width=100,
    align="center",
)
scrambled_toggle = panel.widgets.Toggle(
    name="Scrambled",
    css_classes=["scrambled-button"],
    width=100,
    align="center",
    margin=(5, -20, 5, 10),
)
unfamiliar_toggle = panel.widgets.Toggle(
    name="Unfamiliar",
    css_classes=["unfamiliar-button"],
    width=100,
    align="center",
)


def enable_avg(event):
    if any([famous_toggle.value, scrambled_toggle.value, unfamiliar_toggle.value]):
        avg_button.disabled = False
    else:
        avg_button.disabled = True


famous_toggle.param.watch(enable_avg, ["value"], onlychanged=True)
famous_toggle.param.watch(reset_windows, ["value"], onlychanged=True)
scrambled_toggle.param.watch(enable_avg, ["value"], onlychanged=True)
scrambled_toggle.param.watch(reset_windows, ["value"], onlychanged=True)
unfamiliar_toggle.param.watch(enable_avg, ["value"], onlychanged=True)
unfamiliar_toggle.param.watch(reset_windows, ["value"], onlychanged=True)

# Whole
EEG_pane = None
EEG_lines = None
MEG_pane = None
MEG_lines = None


def second_page():
    global EEG_pane
    global MEG_pane

    # Clear first page
    grid.objects = {}
    grid[8:14, :] = panel.Spacer()

    # Re-add topbar
    topbar.visible = False
    grid[0, :] = topbar

    # Add second page UI
    UI_bar = panel.Row(
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
        visible=False,
    )
    grid[1, :] = UI_bar

    # Start loading animation
    grid.loading = True

    # Load data
    get_subject_data()

    # Create Bokeh plots
    EEG_p, EEG_lines, MEG_p, MEG_lines = avg_plots(
        EEG_group_avgs[0], MEG_group_avgs[0], downsampled_events[0], logger
    )

    # Set layout
    EEG_pane = panel.pane.Bokeh(EEG_p, visible=False)
    MEG_pane = panel.pane.Bokeh(MEG_p, visible=False)
    grid[2:8, 0:7] = EEG_pane
    grid[2:8, 7:10] = panel.Spacer(color="green")
    grid[8:14, 0:7] = MEG_pane
    grid[8:14, 7:10] = panel.Spacer(color="red")

    # Make everything visible
    topbar.visible = True
    UI_bar.visible = True
    EEG_pane.visible = True
    MEG_pane.visible = True

    # Stop loading animation
    grid.loading = False


# ----
# WHOLE
# ----
grid = panel.GridSpec(sizing_mode="stretch_both")
first_page(0)
grid.servable()
