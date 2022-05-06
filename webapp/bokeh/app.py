import chunk
import itertools
import logging
import math

import streamlit as st

from bokeh.palettes import Dark2_5 as palette
from bokeh.layouts import column, row
from bokeh.models import (
    Tabs,
    Panel,
    Range1d,
    ColumnDataSource,
    CheckboxButtonGroup,
    Spinner,
    Select,
    PanTool,
    ResetTool,
    WheelZoomTool
)
from bokeh.plotting import figure, curdoc
from bokeh.events import Pan

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
EEG_channels = args.get("EEG")[0].decode("UTF-8").split(",")
MEG_channels = args.get("MEG")[0].decode("UTF-8").split(",")

# Parse required data
runs_EEG = []
runs_MEG = []
runs_events = []
for i in range(1,7):
    EEG_data, MEG_data, events = parse_run(
        subject_id, i, EEG_channels, MEG_channels
    )
    runs_EEG.append(EEG_data)
    runs_MEG.append(MEG_data)
    runs_events.append(events)

# Chunks
chunk_size = 10 * 145

# View
view_size = 5 * 145

# Color palette
colors = itertools.cycle(palette)

# Ticks
x_ticks = {i*145:str(i) for i in range(math.ceil(MEG_data.shape[1]/145))}

# EEG plot
first_run_EEG = runs_EEG[0][:,:chunk_size]
EEG_p = figure(
    title="EEG",
    #output_backend="webgl",
    tools=[PanTool(dimensions="width"), ResetTool(), WheelZoomTool(dimensions="width")],
    toolbar_location="above",
    sizing_mode="stretch_both",
)
EEG_p.x_range = Range1d(0, view_size, bounds=(0,first_run_EEG.shape[1]))
EEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
EEG_p.xaxis.major_label_overrides = x_ticks
EEG_p.xaxis.axis_label = 'Time (s)'
EEG_p.yaxis.axis_label = 'µV'
EEG_p.toolbar.logo=None
EEG_p.axis.visible = False

EEG_sources = []
for group, color in zip(range(len(first_run_EEG)), colors):
    source = ColumnDataSource(
        dict(
            x=numpy.arange(0, len(first_run_EEG[group]), 1),
            y=first_run_EEG[group]))
    EEG_p.line(x='x', y='y', line_width=1, source=source, line_color=color)
    EEG_sources.append(source)

# MEG plot
first_run_MEG = runs_MEG[0][:chunk_size]
MEG_p = figure(
    title="MEG",
    #output_backend="webgl",
    tools=[PanTool(dimensions="width"), ResetTool(), WheelZoomTool(dimensions="width")],
    toolbar_location=None,
    sizing_mode="stretch_both",
)
MEG_p.x_range = EEG_p.x_range
MEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
MEG_p.xaxis.major_label_overrides = x_ticks
MEG_p.xaxis.axis_label = 'Time (s)'
MEG_p.yaxis.axis_label = 'µV'
MEG_p.toolbar.logo=None
MEG_p.axis.visible = False

MEG_sources = []
for group, color in zip(range(len(first_run_MEG)), colors):
    source = ColumnDataSource(
        dict(
            x=numpy.arange(0, len(first_run_MEG[group]), 1),
            y=first_run_MEG[group]))
    MEG_p.line(x='x', y='y', line_width=1, source=source, line_color=color)
    MEG_sources.append(source)

# Events
#vline = Span(
#    location=0,
#    dimension="height",
#    line_color="red",
#    line_width=145,
#    line_alpha=0.2,
#)
#EEG_p.renderers.extend([vline])

# UI
checkbox_button_group = CheckboxButtonGroup(labels=["Normal", "PSD"], active=[0])
checkbox_button_group.on_click(print("ok"))

spinner_min = Spinner(low=-1.5, high=0, step=0.1, value=-0.5, width=80)
spinner_max = Spinner(low=0.1, high=1.5, step=0.1, value=0.5, width=80)

checkbox_button_group_average = CheckboxButtonGroup(labels=["Average"])
checkbox_button_group_average.on_click(print("ok"))

select_runs = Select(options=["Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Run 6"])

# Streaming
#def load_and_unload_chunk(event):
#    current_chunck =
#    if (event.x + event.delta_x) % chunk_size == 0:
#        for idx, EEG_source in enumerate(EEG_sources):
#            new_data = dict()
#            new_data["x"] = range(len(runs_EEG[0][idx,:]))
#            new_data["y"] = runs_EEG[0][idx,:]
#            EEG_source.data = new_data
#
#    logger.info(event.x)
#    logger.info(event.delta_x)
#
#
#EEG_p.on_event(Pan, load_and_unload_chunk)
#MEG_p.on_event(Pan, load_and_unload_chunk)

# Switching between runs
def change_run(attr, old, new):
    st.legacy_caching.caching.clear_cache()
    run = int(new.split(" ")[1])

    for idx, EEG_source in enumerate(EEG_sources):
        new_data = dict()
        new_data["x"] = range(len(runs_EEG[run-1][idx,:]))
        new_data["y"] = runs_EEG[run-1][idx,:]
        EEG_source.data = new_data

    for idx, MEG_source in enumerate(MEG_sources):
        new_data = dict()
        new_data["x"] = range(len(runs_MEG[run-1][idx,:]))
        new_data["y"] = runs_MEG[run-1][idx,:]
        MEG_source.data = new_data

select_runs.on_change("value", change_run)

# Layout of whole
doc.add_root(
    column(
        column(checkbox_button_group, sizing_mode="fixed"),
        row(
            column(children=[spinner_min, spinner_max]),
            column(checkbox_button_group_average),
        ),
        column(select_runs),
        column(children=[Tabs(tabs=[Panel(child=column(EEG_p, MEG_p, sizing_mode="stretch_both"), title=f"Run {1}")])], sizing_mode="stretch_both"),
        sizing_mode="stretch_width",
    )
)

#"""
#Adding events
        
#basic event at one second is added for testing purposes (too low amount of events to test)
        
#"""
#logger.info(events)
#events.append([145, 13])
#for event in events:
#    # for rectangle, start is around x and around y, so x + half of event duration is correct x-value
#    glyph = Rect(x=event[0] + (event_duration * 145) / 2, y=0, width=event_duration*145, height=100, width_units="data", height_units="data", line_alpha=0.3, fill_alpha=0.3)
#    EEG_p.add_glyph(glyph)
#    MEG_p.add_glyph(glyph)