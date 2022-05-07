import itertools
import logging
import math
from select import select
import streamlit
import numpy
from enum import Enum

from bokeh.palettes import Dark2_5 as palette
from bokeh.layouts import column, row
from bokeh.models import (
    Range1d,
    ColumnDataSource,
    CheckboxButtonGroup,
    Spinner,
    Rect,
    Span,
    Select,
    PanTool,
    ResetTool,
    WheelZoomTool,
    HoverTool,
    Legend,
    LegendItem,
)
from bokeh.plotting import figure, curdoc

import data.parse as parse

# Document
doc = curdoc()

# Logging
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get session arguments
args = doc.session_context.request.arguments
subject_id = int(args.get("id")[0].decode("UTF-8").split(",")[0])
EEG_groups = {"Parietal lobe": args.get("EEG")[0].decode("UTF-8").split(",")}
MEG_groups = {"Parietal lobe": args.get("MEG")[0].decode("UTF-8").split(",")}

# Modes
class Mode(Enum):
    TOTAL = 1
    WINDOW = 2
current_mode = Mode.TOTAL

# Parse required data
runs = []
runs_events = []
for i in range(1, 7):
    run = parse.parse_run(subject_id, i)
    runs.append(run)
    runs_events.append(parse.extract_events(run))

# Calculate group averages
EEG_group_avgs, MEG_group_avgs = parse.group_averages(runs, EEG_groups, MEG_groups)

# Window averages
EEG_window_group_avgs = None
MEG_window_group_avgs = None

# Chunks
chunk_size = 500 * 145

# View
view_size = 10 * 145

# Color palette
colors = itertools.cycle(palette)
group_colors = {id: next(colors) for id in parse.group_names}
event_colors = {id: next(colors) for id in parse.event_names.keys()}

# Average plots
def create_avg_plots(run_idx):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # Ticks
    x_ticks = {i * 145: str(i) for i in range(math.ceil(chunk_size / 145) + 1)}

    # EEG
    run_EEG = EEG_group_avgs[run_idx]
    EEG_p = figure(
        title="EEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        sizing_mode="stretch_both",
    )
    EEG_p.x_range = Range1d(0, view_size)
    EEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    EEG_p.xaxis.major_label_overrides = x_ticks
    EEG_p.xaxis.axis_label = "Time (s)"
    EEG_p.yaxis.axis_label = "µV"
    EEG_p.toolbar.logo = None

    EEG_lines = []
    legend_items = []
    for group_name, group_data in run_EEG.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data[:chunk_size]), 1),
                y=group_data[:chunk_size],
            )
        )
        line = EEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=group_colors[group_name],
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
        # output_backend="webgl",
        tools=tools,
        toolbar_location=None,
        sizing_mode="stretch_both",
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    MEG_p.xaxis.major_label_overrides = x_ticks
    MEG_p.xaxis.axis_label = "Time (s)"
    MEG_p.yaxis.axis_label = "µV"
    MEG_p.toolbar.logo = None

    MEG_lines = []
    legend_items = []
    for group_name, group_data in run_MEG.items():
        source = ColumnDataSource(
            dict(
                x=numpy.arange(0, len(group_data[:chunk_size]), 1),
                y=group_data[:chunk_size],
            )
        )
        line = MEG_p.line(
            x="x",
            y="y",
            line_width=1,
            source=source,
            line_color=group_colors[group_name],
        )
        MEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    MEG_p.add_layout(legend, "right")
    MEG_p.y_range.renderers = MEG_lines

    # Events
    renderers = []
    for event in runs_events[run_idx]:
        event_data = ColumnDataSource(
            dict(
                event_type=[parse.event_names[event[1]]], color=[event_colors[event[1]]]
            )
        )

        # EEG plot
        span = Rect(
            x=event[0] - (parse.event_duration * 145) / 2,
            y=0,
            width=parse.event_duration * 145,
            height=10000,
            width_units="data",
            height_units="data",
            line_alpha=0.1,
            line_color=event_colors[event[1]],
            fill_alpha=0.1,
            fill_color=event_colors[event[1]],
        )
        renderers.append(EEG_p.add_glyph(source_or_glyph=event_data, glyph=span))

        # MEG plot
        span = Rect(
            x=event[0] - (parse.event_duration * 145) / 2,
            y=0,
            width=parse.event_duration * 145,
            height=10000,
            width_units="data",
            height_units="data",
            line_alpha=0.1,
            line_color=event_colors[event[1]],
            fill_alpha=0.1,
            fill_color=event_colors[event[1]],
        )
        renderers.append(MEG_p.add_glyph(source_or_glyph=event_data, glyph=span))

    hovertool = HoverTool(renderers=renderers, tooltips=[("Event type", "@event_type")])
    EEG_p.add_tools(hovertool)
    MEG_p.add_tools(hovertool)

    return EEG_p, MEG_p


# Window plots
def create_window_plots(tmin, tplus):

    # Window
    EEG_window_group_avgs, MEG_window_group_avgs = parse.avg_windows(
        runs, None, tmin, tplus, EEG_groups, MEG_groups
    )  # TODO: add selected events

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # Ticks
    x_ticks = {math.floor(i * 145): str(round(i, 2)) for i in numpy.arange(0, math.ceil(-tmin + tplus)+0.1, 0.1)}

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
            line_color=group_colors[group_name],
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
            line_color=group_colors[group_name],
        )
        MEG_lines.append(line)
        legend_items.append(LegendItem(label=group_name, renderers=[line]))
    legend = Legend(items=legend_items)
    legend.click_policy = "mute"
    MEG_p.add_layout(legend, "right")
    MEG_p.y_range.renderers = MEG_lines

    # Event line
    EEG_p.add_layout(
        Span(location=math.floor(-tmin * 145), dimension="height", line_color=list(event_colors.values())[0])
    )
    MEG_p.add_layout(
        Span(location=math.floor(-tmin * 145), dimension="height", line_color=list(event_colors.values())[0])
    )

    return EEG_p, MEG_p


# Switching between runs
select_runs = Select(value="Run 1", options=["Run " + str(run) for run in range(1, 7)])
def change_run(attr, old, new):
    global current_mode
    streamlit.legacy_caching.caching.clear_cache()
    run_idx = int(new.removeprefix("Run ")) - 1

    new_EEG_p, new_MEG_p = create_avg_plots(run_idx)
    plots_column.children = [new_EEG_p, new_MEG_p]

select_runs.on_change("value", change_run)

# Switching between modes
select_tmin = Spinner(low=-1.5, high=0, step=0.1, value=-0.5, width=80)
select_tmax = Spinner(low=0.1, high=1.5, step=0.1, value=0.5, width=80)

average_button = CheckboxButtonGroup(labels=["Average"], active=[1])

def change_mode(attr):
    global current_mode
    streamlit.legacy_caching.caching.clear_cache()

    if current_mode == Mode.TOTAL:
        current_mode = Mode.WINDOW
        new_EEG_p, new_MEG_p = create_window_plots(select_tmin.value, select_tmax.value)
        select_runs.disabled=True
        select_tmin.disabled = True
        select_tmax.disabled = True
    else:
        run_idx = int(select_runs.value.removeprefix("Run ")) - 1
        current_mode = Mode.TOTAL
        new_EEG_p, new_MEG_p = create_avg_plots(run_idx)
        select_runs.disabled=False
        select_tmin.disabled = False
        select_tmax.disabled = False
    
    plots_column.children = [new_EEG_p, new_MEG_p]

average_button.on_click(change_mode)

# PSD
psd_button = CheckboxButtonGroup(labels=["PSD"], active=[1], disabled=True)

# Layout of whole
EEG_p, MEG_p = create_avg_plots(0)
plots_column = column(children=[EEG_p, MEG_p], sizing_mode="stretch_both")
doc.add_root(
    column(
        row(select_runs, average_button, select_tmin, select_tmax, psd_button),
        plots_column,
        sizing_mode="stretch_both",
    )
)
