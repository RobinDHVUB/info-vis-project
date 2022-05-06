import itertools
import logging
import os
from math import ceil, floor
from random import random

from bokeh.core.property.container import ColumnData
from bokeh.palettes import Dark2_5 as palette

import mne
import numpy as np
from bokeh.client import push_session
from bokeh.io import show
from bokeh.layouts import column, gridplot, row, layout
from bokeh.models import (
    Button,
    ColumnDataSource,
    PanTool,
    Tabs,
    Panel,
    Range1d,
    CheckboxButtonGroup,
    CustomJS,
    Spinner,
    Span,
    Dropdown,
    Select,
)
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
import pandas as pd

from data.parse import *

import streamlit as st

# Logging
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get session arguments
args = curdoc().session_context.request.arguments
subject_id = args.get("id")[0].decode("UTF-8").split(",")
EEG_channels = args.get("EEG")[0].decode("UTF-8").split(",")
MEG_channels = args.get("MEG")[0].decode("UTF-8").split(",")

# Parse required data
EEG_data, MEG_data, events = parse_run(
    int(subject_id[0]), 1, EEG_channels, MEG_channels
)

# CUT FIRST 10 SECONDS
EEG_data = EEG_data[:, : 10 * 145]
MEG_data = MEG_data[:, : 10 * 145]

# Buttons
LABELS = ["Normal", "PSD"]

checkbox_button_group = CheckboxButtonGroup(labels=LABELS, active=[0])
checkbox_button_group.on_click(print("ok"))

spinner_min = Spinner(low=-1.5, high=0, step=0.1, value=-0.5, width=80)
spinner_max = Spinner(low=0.1, high=1.5, step=0.1, value=0.5, width=80)

checkbox_button_group_average = CheckboxButtonGroup(labels=["Average"])
checkbox_button_group_average.on_click(print("ok"))

select_runs = Select(options=["run 1", "run 2", "run 3", "run 4", "run 5", "run 6"])

# Creates and renders the EEG and MEG plots as well as the UI
tabs = []
EEG_sources = []
MEG_sources = []

colors = itertools.cycle(palette)

EEG_p = figure(
    title="EEG",
    plot_height=200,
    plot_width=1000,
    tools="xpan, reset",
    output_backend="canvas",
    x_range=(0, 500),
    toolbar_location="above",
)
MEG_p = figure(
    title="MEG",
    plot_height=200,
    plot_width=1000,
    tools="xpan, reset",
    output_backend="canvas",
    x_range=EEG_p.x_range,
    toolbar_location=None,
)

# Turn off logo
EEG_p.toolbar.logo = None
MEG_p.toolbar.logo = None

# Fixed y range
EEG_p.y_range = Range1d(-50, 50)
MEG_p.y_range = Range1d(-1500, 1500)

vline = Span(
    location=0,
    dimension="height",
    line_color="red",
    line_width=145,
    line_alpha=0.2,
)
EEG_p.renderers.extend([vline])

# Units
EEG_p.xaxis.axis_label = "seconds"
EEG_p.yaxis.axis_label = "µV"

MEG_p.xaxis.axis_label = "seconds"
MEG_p.yaxis.axis_label = "fT"

# Plot EEG
for channel, color in zip(range(len(EEG_data)), colors):
    source = ColumnDataSource(
        dict(x=np.arange(0, len(EEG_data[channel]), 1), y=EEG_data[channel])
    )
    EEG_p.line(x="x", y="y", line_width=1, source=source, line_color=color)
    EEG_sources.append(source)

# Plot MEG
for channel, color in zip(range(len(MEG_data)), colors):
    source = ColumnDataSource(
        dict(x=np.arange(0, len(MEG_data[channel]), 1), y=MEG_data[channel])
    )
    MEG_p.line(x="x", y="y", line_width=1, source=source, line_color=color)
    MEG_sources.append(source)

# Correct ticks
x_ticks_loc = [i * 145 for i in range(500)]

tick_labels = [str(i) for i in range(500)]
EEG_p.xaxis.ticker = x_ticks_loc
EEG_p.xaxis.major_label_overrides = dict(zip(x_ticks_loc, tick_labels))

MEG_p.xaxis.ticker = x_ticks_loc
MEG_p.xaxis.major_label_overrides = dict(zip(x_ticks_loc, tick_labels))

tabs.append(
    Panel(child=column(EEG_p, MEG_p, sizing_mode="stretch_both"), title=f"Run {1}")
)

curdoc().add_root(
    column(
        column(checkbox_button_group, sizing_mode="fixed"),
        row(
            column(children=[spinner_min, spinner_max]),
            column(checkbox_button_group_average),
        ),
        column(select_runs),
        column(children=[Tabs(tabs=tabs)], sizing_mode="stretch_both"),
        sizing_mode="stretch_width",
    )
)


# def update_callback():
#    global a
#    global current
#    new_current = current + 1
#
#    for i in range(1, 7):
#        EEG_data = runs_data[i - 1][0]
#        MEG_data = runs_data[i - 1][1]
#
#        for idx, EEG_source in enumerate(EEG_sources[i - 1]):
#            x = np.arange(current, new_current, 1)
#            y = EEG_data[idx][current:new_current]
#            new_data = dict()
#            new_data["x"] = np.append(EEG_source.data["x"], x)
#            new_data["y"] = np.append(EEG_source.data["y"], y)
#            EEG_source.data = new_data
#
#        for idx, MEG_source in enumerate(MEG_sources[i - 1]):
#            x = np.arange(current, new_current, 1)
#            y = MEG_data[idx][current:new_current]
#            new_data = dict()
#            new_data["x"] = np.append(MEG_source.data["x"], x)
#            new_data["y"] = np.append(MEG_source.data["y"], y)
#            MEG_source.data = new_data
#
#    current = new_current
#
#    if current >= len(EEG_data[0]) or current >= len(MEG_data[0]):
#        # curdoc().remove_periodic_callback(pc_id)
#        print("ok")
#
#    a = a + 1


# Switching between runs
def change_run(attr, old, new):
    st.legacy_caching.caching.clear_cache()
    run = int(new.split(" ")[1])
    EEG_data, MEG_data = parse_run(int(subject_id[0]), run, EEG_channels, MEG_channels)

    for idx, EEG_source in enumerate(EEG_sources):
        x = np.arange(0, len(EEG_data[idx][:]), 1)
        y = EEG_data[idx][:]
        new_data = dict()
        new_data["x"] = x
        new_data["y"] = y
        EEG_source.data = new_data

    for idx, MEG_source in enumerate(MEG_sources):
        x = np.arange(0, len(MEG_data[idx][:]), 1)
        y = MEG_data[idx][:]
        new_data = dict()
        new_data["x"] = x
        new_data["y"] = y
        MEG_source.data = new_data


select_runs.on_change("value", change_run)

# pc_id = curdoc().add_periodic_callback(update_callback, 3000)
