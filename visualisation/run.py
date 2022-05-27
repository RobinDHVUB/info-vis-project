from turtle import update
import panel
import logging
import enum

from functools import partial

from bokehplots import avg_plots, window_plots, psd_plots
from plotlyplots import electrode_plot, update_electrode_plot
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
        f"Subject {subject['id']}: {sex_to_string(subject['sex'])}; {subject['age']}": subject[
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
panel.extension(
    "plotly",
    raw_css=[
        f"""
        html {{
            width: 100%;
        }}
        body {{
            margin:0;
            width:100%;
            background: #E8FCFF;
        }}
        .bk.pn-loading:before {{
            background-color: rgb(232,252,255,0.50);
        }}
        .bk-root > .bk {{
            margin: 0 !important;
        }}
        .bk.panel-widget-box {{
          background: #f0f0f0;
          border-radius: 5px;
        
          -webkit-box-shadow: 0 0 10px rgba(46, 84, 129, .3);
          -moz-box-shadow: 0 0 10px rgba(46, 84, 129, .3);
          box-shadow: 0 0 10px rgba(46, 84, 129, .3);
          border: solid 1px #839bb7;
          outline: none;
          -webkit-transition: border linear .2s,
          box-shadow linear .2s;
          -moz-transition: border linear .2s,
          box-shadow linear .2s;
          transition: border linear .2s, box-shadow linear .2s;
        }}
        .bk-root .bk.title-button .bk-btn {{
          width: 100%;
          background: #000000;
          text-align: left;
          border: 0px black solid;
          color: white;
          font-size: 14pt;
          font-family: arial;
        }}
        .bk-root .bk.top-bar {{
          -webkit-box-shadow: 0 2px 4px 1px rgba(0,0,0,0.25);
          -moz-box-shadow: 0 2px 4px 1px rgba(0,0,0,0.25);
          box-shadow: 0 2px 4px 1px rgba(0,0,0,0.25);
        }}
        .bk-root .bk.famous-button .bk-btn {{
          border: 1px {data_access.event_colors["Famous"]} solid;
          color: {data_access.event_colors["Famous"]};
          font-family: arial;
        }}
        .bk-root .bk.scrambled-button .bk-btn {{
          border: 1px {data_access.event_colors["Scrambled"]} solid;
          color: {data_access.event_colors["Scrambled"]};
          font-family: arial;
        }}
        .bk-root .bk.unfamiliar-button .bk-btn {{
          border: 1px {data_access.event_colors["Unfamiliar"]} solid;
          color: {data_access.event_colors["Unfamiliar"]};
          font-family: arial;
        }}
        .bk-root .bk.temporalL-button .bk-btn {{
          border: 1px {data_access.group_colors["Temporal lobe (L)"]} solid;
          color: {data_access.group_colors["Temporal lobe (L)"]};
          font-family: arial;
        }}
        .bk-root .bk.temporalR-button .bk-btn {{
          border: 1px {data_access.group_colors["Temporal lobe (R)"]} solid;
          color: {data_access.group_colors["Temporal lobe (R)"]};
          font-family: arial;
        }}
        .bk-root .bk.parietal-button .bk-btn {{
          border: 1px {data_access.group_colors["Parietal lobe"]} solid;
          color: {data_access.group_colors["Parietal lobe"]};
          font-family: arial;
        }}
        .bk-root .bk.occipital-button .bk-btn {{
          border: 1px {data_access.group_colors["Occipital lobe"]} solid;
          color: {data_access.group_colors["Occipital lobe"]};
          font-family: arial;
        }}
        .bk-root .bk.frontal-button .bk-btn {{
          border: 1px {data_access.group_colors["Frontal lobe"]} solid;
          color: {data_access.group_colors["Frontal lobe"]};
          font-family: arial;
        }}
        """
    ],
)


# ----
# Top bar
# ----
change_subject_button = panel.widgets.Button(
    name="Change subject",
    button_type="success",
    # sizing_mode="stretch_height",
    align="center",
    css_classes=["main-button"],
)
main_title = panel.widgets.Button(
    name="A multi-subject multi-modal human neuroimaging dataset",
    sizing_mode="stretch_width",
    # align="center",
    margin=(0, 0, 0, 0),
    css_classes=["title-button"],
)
topbar = panel.Row(
    main_title, align="center", sizing_mode="stretch_width", background="#000000",
    css_classes=["top-bar"]
)

link_code = """
window.open("https://www.nature.com/articles/sdata20151", "_blank")
"""
main_title.js_on_click(code=link_code)


# Whole
def first_page(event):
    global topbar
    global grid

    grid.objects = {}
    new_grid = panel.GridSpec(sizing_mode="stretch_both")

    # Add topbar
    topbar.objects = [main_title]
    new_grid[0, :] = topbar

    # Add subject selection pane
    new_grid[1:5, 0:5] = panel.Spacer(sizing_mode="stretch_both")
    new_grid[5:16, 5:10] = subject_selection
    new_grid[16:20, 11:15] = panel.Spacer(sizing_mode="stretch_both")

    # Show
    grid.objects = new_grid.objects


change_subject_button.on_click(first_page)


# ----
# First stage
# ----
title = panel.pane.Markdown(
    "Subject selection",
    align="center",
    style={"font-size": "12pt", "font-family": "arial", "font-weight": "bold"},
    margin=(-15, 0, 0, 0),
)

# Sex select
sex_select_title = panel.pane.Markdown("Sex:", align="center", margin=0, style={'font-family': "arial", "font-weight": "bold"})
sex_select = panel.widgets.CheckButtonGroup(
    value=["f", "m"],
    options={"Female": "f", "Male": "m"},
)


def change_sex_select(event):
    subject_select.options = filter_subjects(event.new, age_select.value)
    if len(subject_select.options) == 0:
        subject_select.disabled = True
        start_analysis_button.disabled = True
    else:
        subject_select.disabled = False
        start_analysis_button.disabled = False


sex_select.param.watch(change_sex_select, ["value"], onlychanged=True)

# Age select
age_select_title = panel.pane.Markdown("Age:", align="center", margin=0, style={'font-family': "arial", 'font-weight': "bold"})
age_select_value = panel.pane.Markdown(f"{min_age}...{max_age}", align="center", margin=-20, style={'font-family': "arial"})
age_select = panel.widgets.IntRangeSlider(
    start=min_age, end=max_age, value=(min_age, max_age), step=1, show_value=False, style={'font-family': "arial"}
)


def change_age_select(event):
    age_select_value.object = f"{event.new[0]}...{event.new[1]}"
    subject_select.options = filter_subjects(sex_select.value, event.new)
    if len(subject_select.options) == 0:
        subject_select.disabled = True
        start_analysis_button.disabled = True
    else:
        subject_select.disabled = False
        start_analysis_button.disabled = False


age_select.param.watch(change_age_select, ["value"], onlychanged=True)

# Subject select
subject_select_title = panel.pane.Markdown("Subject:", align="center", margin=0,
                                           style={'font-family': "arial", 'font-weight': "bold"})
initial_subject_select_options = filter_subjects(sex_select.value, age_select.value)
initial_subject_select_values = {
    id: description for description, id in initial_subject_select_options.items()
}
subject_select = panel.widgets.Select(
    options=initial_subject_select_options, style={'font-family': "arial"}
)

# Start analysis button
start_analysis_button = panel.widgets.Button(
    name="Start analysis",
    button_type="success",
    margin=(10, 10),
    css_classes=["main-button"],
)


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


class DataMode(enum.Enum):
    TIME = 1
    FREQUENCY = 2


current_view_mode = ViewMode.TOTAL
current_data_mode = DataMode.TIME


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
    global runs
    global downsampled_runs
    global EEG_group_avgs
    global EEG_group_psds
    global MEG_group_avgs
    global MEG_group_psds
    global downsampled_events

    # Clear previous
    runs = []
    downsampled_runs = []

    # Runs
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


# Run select
run_select = panel.widgets.Select(
    options={"Run " + str(i): i - 1 for i in range(1, 7)}, value=0, align="center", style={"font-family":"arial"}
)


def change_run(event):
    global current_data_mode
    global EEG_pane
    global EEG_lines
    global MEG_pane
    global MEG_lines
    run_idx = run_select.value

    if current_data_mode is not None:

        # Loading
        EEG_pane.loading = True
        MEG_pane.loading = True

        if current_data_mode == DataMode.TIME:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                EEG_group_avgs[run_idx],
                EEG_group_visible(),
                MEG_group_avgs[run_idx],
                MEG_group_visible(),
                downsampled_events[run_idx],
                logger,
            )
        else:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                EEG_group_psds[run_idx],
                EEG_group_visible(),
                MEG_group_psds[run_idx],
                MEG_group_visible(),
                logger,
            )

        EEG_pane.object = new_EEG_p
        MEG_pane.object = new_MEG_p

        # Stop loading
        EEG_pane.loading = False
        MEG_pane.loading = False


run_select.param.watch(change_run, ["value"], onlychanged=True)


# PSD toggle
psd_button = panel.widgets.Toggle(
    name="PSD", align="center", sizing_mode="stretch_width", style={"font-family":"arial"}
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

    if current_data_mode is not None:

        # Loading
        EEG_pane.loading = True
        MEG_pane.loading = True

        if current_data_mode == DataMode.TIME:
            current_data_mode = DataMode.FREQUENCY

            if current_view_mode == ViewMode.TOTAL:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                    EEG_group_psds[run_idx],
                    EEG_group_visible(),
                    MEG_group_psds[run_idx],
                    MEG_group_visible(),
                    logger,
                )
                avg_button.disabled = True
                tmin_slider.disabled = True
                tplus_slider.disabled = True
                for toggle in event_toggles:
                    toggle.disabled = True
            else:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                    EEG_window_group_psds,
                    EEG_group_visible(),
                    MEG_window_group_psds,
                    MEG_group_visible(),
                    logger,
                )
        else:
            current_data_mode = DataMode.TIME
            enable_avg(0)
            if current_view_mode == ViewMode.TOTAL:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                    EEG_group_avgs[run_idx],
                    EEG_group_visible(),
                    MEG_group_avgs[run_idx],
                    MEG_group_visible(),
                    downsampled_events[run_idx],
                    logger,
                )
                tmin_slider.disabled = False
                tplus_slider.disabled = False
                for toggle in event_toggles:
                    toggle.disabled = False
            else:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = window_plots(
                    EEG_window_group_avgs,
                    EEG_group_visible(),
                    MEG_window_group_avgs,
                    MEG_group_visible(),
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
avg_text = panel.pane.Markdown("Windowing:", align="center", style={"font-family":"arial", "font-weight": "bold"}
)
avg_button = panel.widgets.Toggle(
    name="AVG",
    align="center",
    sizing_mode="stretch_width",
    disabled=True,
    margin=(0, 0, 0, 20), 
    style={"font-family":"arial"}
)


def change_view(event):
    global current_view_mode
    global current_data_mode
    global EEG_lines
    global MEG_lines
    global EEG_head
    global MEG_head
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds
    run_idx = run_select.value

    if current_data_mode is not None:

        # Loading
        EEG_pane.loading = True
        MEG_pane.loading = True

        # Event selection
        selected_events = [
            idx + 1
            for idx, value in enumerate([toggle.value for toggle in event_toggles])
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
            if current_data_mode == DataMode.TIME:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = window_plots(
                    EEG_window_group_avgs,
                    EEG_group_visible(),
                    MEG_window_group_avgs,
                    MEG_group_visible(),
                    tmin_slider.value,
                    tplus_slider.value,
                    logger,
                )
            else:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                    EEG_window_group_psds,
                    EEG_group_visible(),
                    MEG_window_group_psds,
                    MEG_group_visible(),
                    logger,
                )

            run_select.disabled = True
            tmin_slider.disabled = True
            tplus_slider.disabled = True
            for toggle in event_toggles:
                toggle.disabled = True
        else:
            current_view_mode = ViewMode.TOTAL
            if current_data_mode == DataMode.TIME:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                    EEG_group_avgs[run_idx],
                    EEG_group_visible(),
                    MEG_group_avgs[run_idx],
                    MEG_group_visible(),
                    downsampled_events[run_idx],
                    logger,
                )
                tmin_slider.disabled = False
                tplus_slider.disabled = False
                for toggle in event_toggles:
                    toggle.disabled = False
            else:
                new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                    EEG_group_psds[run_idx],
                    EEG_group_visible(),
                    MEG_group_psds[run_idx],
                    MEG_group_visible(),
                    logger,
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
    name="-t",
    start=-1.5,
    end=-0.1,
    step=0.01,
    value=-0.5,
    align="center",
    sizing_mode="stretch_width",
    style={"font-family":"arial", "font-weight":"bold"}
)
tplus_slider = panel.widgets.FloatSlider(
    name="+t",
    start=0.1,
    end=1.5,
    step=0.01,
    value=0.5,
    align="center",
    sizing_mode="stretch_width",
    style={"font-family":"arial"}
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
event_toggles = [
    panel.widgets.Toggle(
        name=event_name,
        align="center",
        width=100,
        margin=(0, 2),
        css_classes=[event_name.lower() + "-button"],
    )
    for event_name in data_access.event_names
]


def enable_avg(event):
    if any([toggle.value for toggle in event_toggles]):
        avg_button.disabled = False
    else:
        avg_button.disabled = True


for toggle in event_toggles:
    toggle.param.watch(enable_avg, ["value"], onlychanged=True)
    toggle.param.watch(reset_windows, ["value"], onlychanged=True)

# Whole UI bar
UI_bar = panel.Row(
    run_select,
    psd_button,
    panel.layout.HSpacer(),
    avg_text,
    tmin_slider,
    tplus_slider,
    *event_toggles,
    avg_button,
)

# Group select toggles
def show_EEG_group(group_name, event):
    global EEG_lines
    global EEG_head

    # Lines
    if EEG_lines is not None:
        for line in EEG_lines[group_name]:
            line.visible = event.new

    # Balls
    if EEG_head is not None:
        EEG_head_pane.objects[0].object = update_electrode_plot(EEG_head, {group_name: event.new})


def EEG_group_visible():
    return {
        group_name: group_toggle.value for group_name, group_toggle in EEG_group_toggles
    }


def show_MEG_group(group_name, event):
    global MEG_lines
    global MEG_head

    # Lines
    if MEG_lines is not None:
        for line in MEG_lines[group_name]:
            line.visible = event.new

    # Balls
    if MEG_head is not None:
        MEG_head_pane.objects[0].object = update_electrode_plot(MEG_head, {group_name: event.new})


def MEG_group_visible():
    return {
        group_name: group_toggle.value for group_name, group_toggle in MEG_group_toggles
    }


EEG_group_toggles = [
    (
        group_name,
        panel.widgets.Toggle(
            name=group_name.replace("lobe", ""),
            width_policy="max",
            margin=(2, 10, 0, 0),
            css_classes=[
                group_name.split(" ")[0].lower() + "-button"
                if len(group_name.split(" ")) == 2
                else group_name.split(" ")[0].lower()
                + group_name.split(" ")[2].strip(")").strip("(")
                + "-button"
            ],
        ),
    )
    for group_name in data_access.group_names
]
EEG_group_toggles_col = panel.Column(
    *[toggle for group_name, toggle in EEG_group_toggles], margin=(0, 0, 0, 30), align="center"
)

MEG_group_toggles = [
    (
        group_name,
        panel.widgets.Toggle(
            name=group_name.replace("lobe", ""),
            width_policy="max",
            margin=(2, 10, 0, 0),
            css_classes=[
                group_name.split(" ")[0].lower() + "-button"
                if len(group_name.split(" ")) == 2
                else group_name.split(" ")[0].lower()
                + group_name.split(" ")[2].strip(")").strip("(")
                + "-button"
            ],
        ),
    )
    for group_name in data_access.group_names
]
MEG_group_toggles_col = panel.Column(
    *[toggle for group_name, toggle in MEG_group_toggles],
    align="center",
    margin=(30, 0, 0, 30),
)


# Whole
EEG_pane = None
EEG_lines = None
EEG_head = None
MEG_pane = None
MEG_lines = None
MEG_head = None

for group_name, group_toggle in EEG_group_toggles:
    group_toggle.param.watch(
        partial(show_EEG_group, group_name), ["value"], onlychanged=True
    )
for group_name, group_toggle in MEG_group_toggles:
    group_toggle.param.watch(
        partial(show_MEG_group, group_name), ["value"], onlychanged=True
    )


def second_page(event):
    global EEG_pane
    global EEG_lines
    global EEG_head
    global MEG_pane
    global EEG_head_pane
    global MEG_lines
    global MEG_head
    global MEG_head_pane
    global current_data_mode
    global current_view_mode

    # Clear first page
    grid.objects = {}
    grid[13:14, 7:10] = panel.Spacer()
    new_grid = panel.GridSpec(sizing_mode="stretch_both")

    # Start loading animation
    grid.loading = True

    # Add selected subject as subtitle
    topbar.pop(0)
    topbar.append(
        panel.pane.Markdown(
            initial_subject_select_values[subject_select.value],
            margin=(0,0,-18,20), 
            sizing_mode="stretch_width",
            align="center",
            style={"color": "white", 'font-size':"14pt", 'font-family':"arial", 'font-weight': 'bold'},
        )
    )

    # Add change subject button
    topbar.append(change_subject_button)


    # (Re)set state
    current_data_mode = None
    psd_button.value = False
    avg_button.value = False
    event_toggles[0].value = True
    event_toggles[0].disabled = False
    for toggle in event_toggles[1:]:
        toggle.value = False
        toggle.disabled = False
    for group_name, toggle in EEG_group_toggles + MEG_group_toggles:
        toggle.value = True
        toggle.disabled = False
    tmin_slider.value = -0.5
    tmin_slider.disabled = False
    tplus_slider.value = 0.5
    tplus_slider.disabled = False
    run_select.value = 0
    run_select.disabled = False
    current_data_mode = DataMode.TIME
    current_view_mode = ViewMode.TOTAL

    # Re-add topbar
    new_grid[0, :] = topbar

    # Add second page UI bar
    new_grid[1, :11] = UI_bar

    # Load data
    get_subject_data()

    # Create Bokeh plots
    EEG_p, EEG_lines, MEG_p, MEG_lines = avg_plots(
        EEG_group_avgs[0],
        EEG_group_visible(),
        MEG_group_avgs[0],
        MEG_group_visible(),
        downsampled_events[0],
        logger,
    )

    # Set layout
    EEG_pane = panel.pane.Bokeh(EEG_p, margin=(0, 0, 10, 0))
    EEG_head = electrode_plot(
        metadata["eeg_names"],
        metadata["eeg_types"],
        metadata["subjects"][subject_select.value - 1]["eeg_coords"],
        metadata["subjects"][subject_select.value - 1]["mesh_coords"],
        "eeg",
        EEG_group_visible(),
    )
    EEG_head_pane = panel.Row(
        panel.pane.Plotly(
            EEG_head,
            config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
            margin=0,
        ),
        align="center",
        margin=0,
    )
    MEG_pane = panel.pane.Bokeh(MEG_p, margin=(0, 0, 10, 0))
    MEG_head = electrode_plot(
        metadata["meg_names"],
        metadata["meg_types"],
        metadata["meg_coords"],
        metadata["meg_mesh_coords"],
        "meg",
        MEG_group_visible(),
    )
    MEG_head_pane = panel.Row(
        panel.pane.Plotly(
            MEG_head,
            config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
            margin=0,
        ),
        align="center",
        margin=(30, 0, 0, 0),
        sizing_mode="stretch_both",
    )

    # Plotly panes need to be nested in a Panel pane in order to get correct scaling,
    # since Plotly panes default to 100% height and width instead of explicitly computing
    # a height and width that fits the grid
    new_grid[2:8, :7] = EEG_pane
    new_grid[2:8, 7] = EEG_group_toggles_col
    new_grid[2:8, 8:11] = EEG_head_pane
    new_grid[8:15, :7] = MEG_pane
    new_grid[8:14, 7] = MEG_group_toggles_col
    new_grid[8:14, 8:11] = MEG_head_pane

    # Stop loading animation and swap grid contents
    grid.objects = new_grid.objects
    grid.loading = False

start_analysis_button.on_click(second_page)

# ----
# WHOLE
# ----
grid = panel.GridSpec(sizing_mode="stretch_both", background="#E8FCFF")
first_page(0)
grid.servable("InfoVis")
