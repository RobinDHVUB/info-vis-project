import chunk
import itertools
import logging
import math

import streamlit as st

from bokeh.palettes import Dark2_5 as palette
from bokeh.layouts import column, row
from bokeh.models import (
    Range1d,
    ColumnDataSource,
    CheckboxButtonGroup,
    Spinner,
    Span,
    Rect,
    Select,
    PanTool,
    ResetTool,
    WheelZoomTool,
    HoverTool,
    Legend,
    LegendItem,
)
from bokeh.plotting import figure, curdoc

from data.parse import *

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

# Parse required data
runs = []
runs_events = []
for i in range(1, 7):
    run = parse_run(subject_id, i)
    runs.append(run)
    runs_events.append(extract_events(run))

# Calculate group averages
EEG_group_avgs = []
MEG_group_avgs = []
for run in runs:
    EEG_group_avg, MEG_group_avg = group_average(run, EEG_groups, MEG_groups)
    EEG_group_avgs.append(EEG_group_avg)
    MEG_group_avgs.append(MEG_group_avg)

# Chunks
chunk_size = 500 * 145

# View
view_size = 10 * 145

# Color palette
colors = itertools.cycle(palette)
group_colors = {id: next(colors) for id in group_names}
event_colors = {id: next(colors) for id in event_names.keys()}

# Ticks
x_ticks = {i * 145: str(i) for i in range(math.ceil(chunk_size / 145))}

# Average plots
def create_avg_plots(run):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # EEG
    run_EEG = EEG_group_avgs[run]
    EEG_p = figure(
        title="EEG",
        # output_backend="webgl",
        tools=tools,
        toolbar_location="above",
        sizing_mode="stretch_both",
    )
    EEG_p.x_range = Range1d(0, view_size, bounds=(0, chunk_size))
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
    run_MEG = MEG_group_avgs[run]
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
    for event in runs_events[run]:
        event_data = ColumnDataSource(
            dict(event_type=[event_names[event[1]]], color=[event_colors[event[1]]])
        )

        # EEG plot
        span = Rect(
            x=event[0] - (event_duration * 145) / 2,
            y=0,
            width=event_duration * 145,
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
            x=event[0] - (event_duration * 145) / 2,
            y=0,
            width=event_duration * 145,
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
def create_window_plots(run):
    return 0


# UI
checkbox_button_group = CheckboxButtonGroup(labels=["Normal", "PSD"], active=[0])
checkbox_button_group.on_click(print("ok"))

spinner_min = Spinner(low=-1.5, high=0, step=0.1, value=-0.5, width=80)
spinner_max = Spinner(low=0.1, high=1.5, step=0.1, value=0.5, width=80)

checkbox_button_group_average = CheckboxButtonGroup(labels=["Average"])
checkbox_button_group_average.on_click(print("ok"))

select_runs = Select(options=["Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Run 6"])

# Switching between runs
def change_run(attr, old, new):
    st.legacy_caching.caching.clear_cache()
    run = int(new.split(" ")[1]) - 1

    new_EEG_p, new_MEG_p = create_avg_plots(run)
    plots_column.children = [new_EEG_p, new_MEG_p]


select_runs.on_change("value", change_run)

# Layout of whole
EEG_p, MEG_p = create_avg_plots(0)
plots_column = column(children=[EEG_p, MEG_p], sizing_mode="stretch_both")
doc.add_root(
    column(
        column(checkbox_button_group, sizing_mode="fixed"),
        row(
            column(children=[spinner_min, spinner_max]),
            column(checkbox_button_group_average),
        ),
        column(select_runs, sizing_mode="fixed"),
        plots_column,
        sizing_mode="stretch_both",
    )
)
