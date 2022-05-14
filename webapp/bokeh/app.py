import logging
import math
import streamlit
import numpy
import json

from bokeh.layouts import column, row
from bokeh.models import (
    Range1d,
    ColumnDataSource,
    CheckboxButtonGroup,
    Spinner,
    Rect,
    Span,
    Select,
    MultiSelect,
    PanTool,
    ResetTool,
    WheelZoomTool,
    HoverTool,
    Legend,
    LegendItem,
)
from bokeh.plotting import figure, curdoc
from enum import Enum
from urllib.parse import unquote

import data.access as access

# Document
doc = curdoc()

# Logging
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get session arguments
args = doc.session_context.request.arguments
subject_id = int(args.get("id")[0].decode("UTF-8").split(",")[0])
EEG_groups = json.loads(unquote(args.get("EEG")[0]))
MEG_groups = json.loads(unquote(args.get("MEG")[0]))

# Modes
class ViewMode(Enum):
    TOTAL = 1
    WINDOW = 2


current_view_mode = ViewMode.TOTAL


class DataMode(Enum):
    TIME = 1
    FREQUENCY = 2


current_data_mode = DataMode.TIME

# Parse required data
runs = []
downsampled_runs = []
for i in range(1, 7):
    run, downsampled_run = access.parse_run(subject_id, i, logger)
    runs.append(run)
    downsampled_runs.append(downsampled_run)

# Calculate downsampled group averages, group psds, and downsampled events
(
    EEG_group_avgs,
    EEG_group_psds,
    MEG_group_avgs,
    MEG_group_psds,
    downsampled_events,
) = access.group_averages(downsampled_runs, EEG_groups, MEG_groups)

# Window averages
EEG_window_group_avgs = None
EEG_window_group_psds = None
MEG_window_group_avgs = None
MEG_window_group_psds = None

# View
view_size = 10 * 145

# Average plots
def create_avg_plots(run_idx):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # Ticks
    run_lengths = [
        len(group_avg) for group_avg in list(EEG_group_avgs[run_idx].values())
    ]
    x_ticks = {
        i * access.avg_sfreq: str(i)
        for i in range(round(max(run_lengths) / access.avg_sfreq) + 1)
    }

    # EEG
    run_EEG = EEG_group_avgs[run_idx]
    EEG_p = figure(
        title="EEG",
        output_backend="webgl",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        lod_threshold=None,
        width=1000,
        height=200
    )
    EEG_p.x_range = Range1d(0, 10 * access.avg_sfreq)
    EEG_p.xaxis.axis_label = "Time (s)"
    EEG_p.yaxis.axis_label = "µV"
    EEG_p.toolbar.logo = None
    EEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    EEG_p.xaxis.major_label_overrides = x_ticks

    EEG_lines = []
    legend_items = []
    for group_name, group_data in run_EEG.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data), 1),
                y=group_data,
            )
        )
        line = EEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=access.group_colors[group_name],
        )
        EEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    EEG_p.add_layout(legend, "right")
    EEG_p.y_range.renderers = EEG_lines

    # MEG plot
    run_MEG = MEG_group_avgs[run_idx]
    MEG_p = figure(
        title="MEG",
        output_backend="webgl",
        tools=tools,
        toolbar_location=None,
        lod_threshold=None,
        width=1000,
        height=200
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    MEG_p.xaxis.major_label_overrides = x_ticks
    MEG_p.xaxis.axis_label = "Time (s)"
    MEG_p.yaxis.axis_label = "fT"
    MEG_p.toolbar.logo = None

    MEG_lines = []
    legend_items = []
    for group_name, group_data in run_MEG.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data), 1),
                y=group_data,
            )
        )
        line = MEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=access.group_colors[group_name],
        )
        MEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    MEG_p.add_layout(legend, "right")
    MEG_p.y_range.renderers = MEG_lines

    # Events
    renderers = []
    for event in downsampled_events[run_idx]:
        if event[0] <= max(run_lengths):
            event_data = ColumnDataSource(
                dict(
                    event_type=[access.event_names[event[1] - 1]],
                    color=[access.event_colors[access.event_names[event[1] - 1]]],
                )
            )

            # EEG plot
            span = Rect(
                x=round(event[0] - (access.event_duration * access.avg_sfreq) / 2),
                y=0,
                width=access.event_duration * access.avg_sfreq,
                height=10000,
                width_units="data",
                height_units="data",
                line_alpha=0.1,
                line_color=access.event_colors[access.event_names[event[1] - 1]],
                fill_alpha=0.1,
                fill_color=access.event_colors[access.event_names[event[1] - 1]],
            )
            renderers.append(EEG_p.add_glyph(source_or_glyph=event_data, glyph=span))

            # MEG plot
            span = Rect(
                x=round(event[0] - (access.event_duration * access.avg_sfreq) / 2),
                y=0,
                width=access.event_duration * access.avg_sfreq,
                height=100000,
                width_units="data",
                height_units="data",
                line_alpha=0.1,
                line_color=access.event_colors[access.event_names[event[1] - 1]],
                fill_alpha=0.1,
                fill_color=access.event_colors[access.event_names[event[1] - 1]],
            )
            renderers.append(MEG_p.add_glyph(source_or_glyph=event_data, glyph=span))

    hovertool = HoverTool(renderers=renderers, tooltips=[("Event type", "@event_type")])
    EEG_p.add_tools(hovertool)
    MEG_p.add_tools(hovertool)

    return EEG_p, MEG_p


# Window plots
def create_window_plots(tmin, tplus, events):
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds

    # Window
    if EEG_window_group_avgs is None:
        (
            EEG_window_group_avgs,
            EEG_window_group_psds,
            MEG_window_group_avgs,
            MEG_window_group_psds,
        ) = access.avg_windows(
            runs,
            [int(event_id) for event_id in events],
            tmin,
            tplus,
            EEG_groups,
            MEG_groups,
        )

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # Ticks
    x_ticks = {
        math.floor(i * 145): str(round(i, 2))
        for i in numpy.arange(0, math.ceil(-tmin + tplus) + 0.1, 0.1)
    }

    # EEG
    EEG_p = figure(
        title="EEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        sizing_mode="stretch_both",
    )
    EEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    EEG_p.xaxis.major_label_overrides = x_ticks
    EEG_p.xaxis.axis_label = "Time (s)"
    EEG_p.yaxis.axis_label = "µV"
    EEG_p.toolbar.logo = None

    EEG_lines = []
    legend_items = []
    for group_name, group_data in EEG_window_group_avgs.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data), 1),
                y=group_data,
            )
        )
        line = EEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=access.group_colors[group_name],
        )
        EEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    EEG_p.add_layout(legend, "right")
    EEG_p.y_range.renderers = EEG_lines

    # MEG plot
    MEG_p = figure(
        title="MEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location=None,
        sizing_mode="stretch_both",
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    MEG_p.xaxis.major_label_overrides = x_ticks
    MEG_p.xaxis.axis_label = "Time (s)"
    MEG_p.yaxis.axis_label = "fT"
    MEG_p.toolbar.logo = None

    MEG_lines = []
    legend_items = []
    for group_name, group_data in MEG_window_group_avgs.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data), 1),
                y=group_data,
            )
        )
        line = MEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=access.group_colors[group_name],
        )
        MEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    MEG_p.add_layout(legend, "right")
    MEG_p.y_range.renderers = MEG_lines

    # Event line
    EEG_p.add_layout(
        Span(
            location=math.floor(-tmin * 145),
            dimension="height",
            line_color="#E70000",
        )
    )
    MEG_p.add_layout(
        Span(
            location=math.floor(-tmin * 145),
            dimension="height",
            line_color="#E70000",
        )
    )

    return EEG_p, MEG_p


# PSD plots
def create_psd_plots(run_idx):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # EEG
    EEG_p = figure(
        title="EEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        sizing_mode="stretch_both",
    )
    EEG_p.xaxis.axis_label = "Frequency (Hz)"
    EEG_p.yaxis.axis_label = "Density"
    EEG_p.toolbar.logo = None

    EEG_psds = (
        EEG_group_psds[run_idx]
        if current_view_mode == ViewMode.TOTAL
        else EEG_window_group_psds
    )
    EEG_lines = []
    legend_items = []
    for group_name, group_data in EEG_psds.items():
        freqs, psds = group_data
        for channel_psd in psds:
            source = ColumnDataSource(
                dict(
                    x=freqs,
                    y=channel_psd,
                )
            )
            line = EEG_p.line(
                x="x",
                y="y",
                line_width=1,
                source=source,
                line_color=access.group_colors[group_name],
            )
            EEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    EEG_p.add_layout(legend, "right")
    EEG_p.y_range.renderers = EEG_lines

    # MEG plot
    MEG_p = figure(
        title="MEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location=None,
        sizing_mode="stretch_both",
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.axis_label = "Frequency (Hz)"
    MEG_p.yaxis.axis_label = "Density"
    MEG_p.toolbar.logo = None

    MEG_psds = (
        MEG_group_psds[run_idx]
        if current_view_mode == ViewMode.TOTAL
        else MEG_window_group_psds
    )
    MEG_lines = []
    legend_items = []
    for group_name, group_data in MEG_psds.items():
        freqs, psds = group_data
        for channel_psd in psds:
            source = ColumnDataSource(
                dict(
                    x=freqs,
                    y=channel_psd,
                )
            )
            line = MEG_p.line(
                x="x",
                y="y",
                line_width=1,
                source=source,
                line_color=access.group_colors[group_name],
            )
            MEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    MEG_p.add_layout(legend, "right")
    MEG_p.y_range.renderers = MEG_lines

    return EEG_p, MEG_p


# Switching between runs
select_runs = Select(value="Run 1", options=["Run " + str(run) for run in range(1, 7)])


def change_run(attr, old, new):
    global current_data_mode
    streamlit.legacy_caching.caching.clear_cache()
    run_idx = int(new.removeprefix("Run ")) - 1

    if current_data_mode == DataMode.TIME:
        new_EEG_p, new_MEG_p = create_avg_plots(run_idx)
    else:
        new_EEG_p, new_MEG_p = create_psd_plots(run_idx)

    EEG_row.children = [new_EEG_p]
    MEG_row.children = [new_MEG_p]


select_runs.on_change("value", change_run)

# Switching between view modes
select_tmin = Spinner(title="tmin:", low=-1.5, high=0, step=0.1, value=-0.5, width=80)
select_tmax = Spinner(title="tplus:", low=0.1, high=1.5, step=0.1, value=0.5, width=80)


def reset_windows(attr, old, new):
    global EEG_window_group_avgs
    global EEG_window_group_psds
    global MEG_window_group_avgs
    global MEG_window_group_psds
    EEG_window_group_avgs = None
    EEG_window_group_psds = None
    MEG_window_group_avgs = None
    MEG_window_group_psds = None


select_tmin.on_change("value", reset_windows)
select_tmax.on_change("value", reset_windows)

select_events = MultiSelect(
    value=["1"],
    options=[
        (str(event_id + 1), event_name)
        for event_id, event_name in enumerate(access.event_names)
    ],
)


def enable_avg(attr, old, new):
    if len(select_events.value) > 0:
        average_button.disabled = False
    else:
        average_button.disabled = True


select_events.on_change("value", enable_avg)
select_events.on_change("value", reset_windows)

average_button = CheckboxButtonGroup(labels=["Average"], active=[1])


def change_view_mode(attr):
    global current_view_mode
    global current_data_mode
    streamlit.legacy_caching.caching.clear_cache()
    run_idx = int(select_runs.value.removeprefix("Run ")) - 1

    if current_view_mode == ViewMode.TOTAL:
        current_view_mode = ViewMode.WINDOW
        if current_data_mode == DataMode.TIME:
            new_EEG_p, new_MEG_p = create_window_plots(
                select_tmin.value, select_tmax.value, select_events.value
            )
        else:
            new_EEG_p, new_MEG_p = create_psd_plots(run_idx)
        select_runs.disabled = True
        select_tmin.disabled = True
        select_tmax.disabled = True
        select_events.disabled = True
    else:
        current_view_mode = ViewMode.TOTAL
        if current_data_mode == DataMode.TIME:
            new_EEG_p, new_MEG_p = create_avg_plots(run_idx)
            select_tmin.disabled = False
            select_tmax.disabled = False
            select_events.disabled = False
        else:
            new_EEG_p, new_MEG_p = create_psd_plots(run_idx)
        select_runs.disabled = False

    EEG_row.children = [new_EEG_p]
    MEG_row.children = [new_MEG_p]


average_button.on_click(change_view_mode)

# Switching between data modes
psd_button = CheckboxButtonGroup(labels=["PSD"], active=[1])


def change_data_mode(attr):
    global current_view_mode
    global current_data_mode
    streamlit.legacy_caching.caching.clear_cache()
    run_idx = int(select_runs.value.removeprefix("Run ")) - 1

    if current_data_mode == DataMode.TIME:
        current_data_mode = DataMode.FREQUENCY
        new_EEG_p, new_MEG_p = create_psd_plots(run_idx)
        if current_view_mode == ViewMode.TOTAL:
            average_button.disabled = True
        select_tmin.disabled = True
        select_tmax.disabled = True
    else:
        current_data_mode = DataMode.TIME
        average_button.disabled = False
        if current_view_mode == ViewMode.TOTAL:
            new_EEG_p, new_MEG_p = create_avg_plots(run_idx)
            select_tmin.disabled = False
            select_tmax.disabled = False
        else:
            new_EEG_p, new_MEG_p = create_window_plots(
                select_tmin.value, select_tmax.value, select_events.value
            )

    EEG_row.children = [new_EEG_p]
    MEG_row.children = [new_MEG_p]


psd_button.on_click(change_data_mode)

# Layout of whole
EEG_p, MEG_p = create_avg_plots(0)
EEG_row = row(EEG_p, sizing_mode="scale_both")
MEG_row = row(EEG_p, sizing_mode="scale_both")
doc.add_root(
    column(
        row(
            select_runs,
            psd_button,
            average_button,
            select_tmin,
            select_tmax,
            select_events,
            sizing_mode="scale_both",
        ),
        EEG_row,
        MEG_row,
        sizing_mode="scale_both"
    )
)