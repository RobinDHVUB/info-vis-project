import panel
import logging
import enum

from functools import partial

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
panel.extension(
    "plotly",
    raw_css=[
        f"""
        .bk.panel-widget-box {{
          background: #f0f0f0;
          border-radius: 5px;
          border: 1px black solid;
        }}
        .bk-root .bk.title-button .bk-btn {{
          background: #000000;
          text-align: left;
          border: 0px black solid;
          color: white;
          font-size: 16pt;
          font-family: monospace;
        }}
        .bk-root .bk.main-button .bk-btn {{
          color: white;
          font-size: 12pt;
          font-family: monospace;
        }}
        .bk-root .bk.famous-button .bk-btn {{
          border: 1px {data_access.event_colors["Famous"]} solid;
          color: {data_access.event_colors["Famous"]};
        }}
        .bk-root .bk.scrambled-button .bk-btn {{
          border: 1px {data_access.event_colors["Scrambled"]} solid;
          color: {data_access.event_colors["Scrambled"]};
        }}
        .bk-root .bk.unfamiliar-button .bk-btn {{
          border: 1px {data_access.event_colors["Unfamiliar"]} solid;
          color: {data_access.event_colors["Unfamiliar"]};
        }}
        .bk-root .bk.temporalL-button .bk-btn {{
          border: 1px {data_access.group_colors["Temporal lobe (L)"]} solid;
          color: {data_access.group_colors["Temporal lobe (L)"]};
        }}
        .bk-root .bk.temporalR-button .bk-btn {{
          border: 1px {data_access.group_colors["Temporal lobe (R)"]} solid;
          color: {data_access.group_colors["Temporal lobe (R)"]};
        }}
        .bk-root .bk.parietal-button .bk-btn {{
          border: 1px {data_access.group_colors["Parietal lobe"]} solid;
          color: {data_access.group_colors["Parietal lobe"]};
        }}
        .bk-root .bk.occipital-button .bk-btn {{
          border: 1px {data_access.group_colors["Occipital lobe"]} solid;
          color: {data_access.group_colors["Occipital lobe"]};
        }}
        .bk-root .bk.frontal-button .bk-btn {{
          border: 1px {data_access.group_colors["Frontal lobe"]} solid;
          color: {data_access.group_colors["Frontal lobe"]};
        }}
        """
    ],
)


# ----
# Plotly
# ----
import plotly.graph_objects as go


# Helper function to create a prettier mesh for the 3D MEG/EEG cap visualization.
# We initially created a more dynamic computation of which additional triangles should be drawn,
# but this seemed to be too variable and would take a lot of time.
# Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
def missing_mesh_idx(plot_type, el_names):

    if plot_type.lower() == "meg":
        # list of MEG signals that should be connected to fill up some gaps
        els_to_connect = [
            "MEG1211",
            "MEG1221",
            "MEG1321",
            "MEG1331",
            "MEG2421",
            "MEG2431",
            "MEG1411",
            "MEG1441",
            "MEG2611",
            "MEG2641",
            "MEG2521",
            "MEG1731",
            "MEG1931",
            "MEG2121",
            "MEG2331",
            "MEG2511",
            "MEG1421",
            "MEG1431",
            "MEG2621",
            "MEG2631",
            "MEG2531",
            "MEG2541",
            "MEG2131",
            "MEG2141",
            "MEG1741",
            "MEG1711",
        ]
    else:
        # list of EEG signals that should be connected to fill up some gaps
        els_to_connect = [
            "EEG007",
            "EEG008",
            "EEG002",
            "EEG005",
            "EEG004",
            "EEG038",
            "EEG039",
            "EEG050",
            "EEG003",
            "EEG074",
            "EEG069",
            "EEG029",
            "EEG030",
            "EEG041",
            "EEG040",
            "EEG052",
            "EEG051",
            "EEG001",
            "EEG070",
            "EEG018",
            "EEG060",
            "EEG049",
            "EEG028",
            "EEG027",
            "EEG017",
            "EEG026",
            "EEG016",
            "EEG009",
            "EEG010",
            "EEG059",
            "EEG071",
            "EEG072",
            "EEG073",
            "EEG015",
            "EEG011",
        ]

    # list of indices of the electrode signals in the original list of electrode names/coordinates
    indices = []
    for index, el_name in enumerate(els_to_connect):
        indices.append(el_names.index(el_name))

    # original coordinate indices that should be connected
    i = [
        indices[0],
        indices[6],
        indices[2],
        indices[17],
        indices[18],
        indices[5],
        indices[20],
        indices[21],
        indices[22],
        indices[24],
    ]
    j = [
        indices[1],
        indices[7],
        indices[16],
        indices[18],
        indices[19],
        indices[19],
        indices[21],
        indices[22],
        indices[13],
        indices[25],
    ]
    k = [
        indices[6],
        indices[2],
        indices[17],
        indices[3],
        indices[4],
        indices[20],
        indices[15],
        indices[14],
        indices[23],
        indices[11],
    ]

    return i, j, k


# convert a list of electrode types to a list of colors
def types_to_colors(el_types):
    return [data_access.group_colors[el_type] for el_type in el_types]


# generate a 3D visualization of an EEG or MEG "electrode cap"
# plot_type is expected be either "eeg" or "meg" and is used to fill up "gaps" in the mesh
def visualize_electrodes_3d(el_names, el_types, el_coords, mesh_coords, plot_type):

    # get the coordinates of all electrodes
    el_x = el_coords[0]
    el_y = el_coords[1]
    el_z = el_coords[2]

    # get the coordinates for the mesh beneath the electrodes (mesh is added to have a clearer view)
    mesh_x = mesh_coords[0]
    mesh_y = mesh_coords[1]
    mesh_z = mesh_coords[2]

    # get the non-selected elements
    el_colors = types_to_colors(el_types)

    # trace for the non-selected electrodes
    trace_non = go.Scatter3d(
        x=el_x,
        y=el_y,
        z=el_z,
        mode="markers",
        hovertemplate="%{text}<extra></extra>",
        text=el_names,
        marker=dict(
            symbol="circle",
            size=12,
            color=el_colors,
            opacity=0.6,
            line=dict(color="white", width=1),
        ),
    )

    # trace for the mesh
    trace_mesh = go.Mesh3d(
        hoverinfo="skip",
        opacity=1,
        color="#C0C0C0",
        x=mesh_x,
        y=mesh_y,
        z=mesh_z,
    )

    # add missing Mesh connections for a prettier mesh
    missing_i, missing_j, missing_k = missing_mesh_idx(plot_type, el_names)
    trace_missing_mesh = go.Mesh3d(
        hoverinfo="skip",
        opacity=1,
        color="#C0C0C0",
        type="mesh3d",
        x=mesh_x,
        y=mesh_y,
        z=mesh_z,
        i=missing_i,
        j=missing_j,
        k=missing_k,
    )

    # include all traces
    data = [trace_non, trace_mesh, trace_missing_mesh]

    # don't include any grids, axes, etc. (since we just want the 3D figure)
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            # camera?
            bgcolor="#fff",
            xaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
            zaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


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
                EEG_group_psds[run_idx],
                EEG_group_line_visible(),
                MEG_group_psds[run_idx],
                MEG_group_line_visible(),
                logger,
            )
            avg_button.disabled = True
            tmin_slider.disabled = True
            tplus_slider.disabled = True
            famous_toggle.disabled = True
            scrambled_toggle.disabled = True
            unfamiliar_toggle.disabled = True
        else:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = psd_plots(
                EEG_window_group_psds,
                EEG_group_line_visible(),
                MEG_window_group_psds,
                MEG_group_line_visible(),
                logger,
            )
    else:
        current_data_mode = DataMode.TIME
        enable_avg(0)
        if current_view_mode == ViewMode.TOTAL:
            new_EEG_p, EEG_lines, new_MEG_p, MEG_lines = avg_plots(
                EEG_group_avgs[run_idx],
                EEG_group_line_visible(),
                MEG_group_avgs[run_idx],
                MEG_group_line_visible(),
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
                EEG_group_line_visible(),
                MEG_window_group_avgs,
                MEG_group_line_visible(),
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
            EEG_group_line_visible(),
            MEG_window_group_avgs,
            MEG_group_line_visible(),
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
                EEG_group_line_visible(),
                MEG_group_avgs[run_idx],
                MEG_group_line_visible(),
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
                EEG_group_psds[run_idx],
                EEG_group_line_visible(),
                MEG_group_psds[run_idx],
                MEG_group_line_visible(),
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

# Group select toggles
def show_EEG_lines(group_name, event):
    global EEG_lines
    for line in EEG_lines[group_name]:
        line.visible = event.new


def EEG_group_line_visible():
    return {
        group_name: group_toggle.value for group_name, group_toggle in EEG_group_toggles
    }


def show_MEG_lines(group_name, event):
    global MEG_lines
    for line in MEG_lines[group_name]:
        line.visible = event.new


def MEG_group_line_visible():
    return {
        group_name: group_toggle.value for group_name, group_toggle in MEG_group_toggles
    }


EEG_group_toggles = [
    (
        group_name,
        panel.widgets.Toggle(
            name=group_name.replace("lobe", ""),
            align="center",
            width_policy="min",
            margin=(0, 1, 0, 0),
            value=True,
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
EEG_group_toggles_row = panel.Row(
    *[toggle for group_name, toggle in EEG_group_toggles], aling="center", visible=False
)

MEG_group_toggles = [
    (
        group_name,
        panel.widgets.Toggle(
            name=group_name.replace("lobe", ""),
            align="center",
            width_policy="min",
            margin=(0, 1, 0, 0),
            value=True,
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
MEG_group_toggles_row = panel.Row(
    *[toggle for group_name, toggle in MEG_group_toggles], aling="center", visible=False
)


# Whole
EEG_pane = None
EEG_lines = None
MEG_pane = None
MEG_lines = None

for group_name, group_toggle in EEG_group_toggles:
    group_toggle.param.watch(
        partial(show_EEG_lines, group_name), ["value"], onlychanged=True
    )
for group_name, group_toggle in MEG_group_toggles:
    group_toggle.param.watch(
        partial(show_MEG_lines, group_name), ["value"], onlychanged=True
    )


def second_page():
    global EEG_pane
    global EEG_lines
    global MEG_pane
    global MEG_lines

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
        EEG_group_avgs[0],
        EEG_group_line_visible(),
        MEG_group_avgs[0],
        MEG_group_line_visible(),
        downsampled_events[0],
        logger,
    )

    # Set layout
    EEG_pane = panel.pane.Bokeh(EEG_p, visible=False)
    EEG_head = visualize_electrodes_3d(
        metadata["meg_names"],
        metadata["meg_types"],
        metadata["meg_coords"],
        metadata["meg_mesh_coords"],
        "meg",
    )
    EEG_head_pane = panel.pane.Plotly(
        EEG_head,
        config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
        visible=False,
    )
    MEG_pane = panel.pane.Bokeh(MEG_p, visible=False)
    MEG_head = visualize_electrodes_3d(
        metadata["meg_names"],
        metadata["meg_types"],
        metadata["meg_coords"],
        metadata["meg_mesh_coords"],
        "meg",
    )
    MEG_head_pane = panel.pane.Plotly(
        MEG_head,
        config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
        visible=False,
    )
    grid[2:8, 0:7] = EEG_pane
    grid[2:7, 7:10] = EEG_head_pane
    grid[7:8, 7:10] = EEG_group_toggles_row
    grid[8:14, 0:7] = MEG_pane
    grid[8:13, 7:10] = MEG_head_pane
    grid[13:14, 7:10] = MEG_group_toggles_row

    # Make everything visible
    topbar.visible = True
    UI_bar.visible = True
    EEG_pane.visible = True
    MEG_pane.visible = True
    EEG_group_toggles_row.visible = True
    MEG_group_toggles_row.visible = True
    EEG_head_pane.visible = True
    MEG_head_pane.visible = True

    # Stop loading animation
    grid.loading = False


# ----
# WHOLE
# ----
grid = panel.GridSpec(sizing_mode="stretch_both")
first_page(0)
grid.servable()
