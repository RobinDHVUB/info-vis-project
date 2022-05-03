# myapp.py
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
from bokeh.layouts import column, gridplot, row
from bokeh.models import Button, ColumnDataSource, PanTool, Tabs, Panel, Range1d
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
import pandas as pd

from data.parse import *

"""
Get arguments that are given to session

"""

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

args = curdoc().session_context.request.arguments

subject_id = args.get("id")[0].decode("UTF-8").split(",")
EEG_channels = args.get("EEG")[0].decode("UTF-8").split(",")
MEG_channels = args.get("MEG")[0].decode("UTF-8").split(",")
logger.info(subject_id)

TOOLS = "xpan, reset"

start = 1000
step = 3000
current = 1000

runs_data = [parse_run(int(subject_id[0]), run, EEG_channels, MEG_channels) for run in [1, 1, 1, 1, 1, 1]]
logger.info("logging...")


def start_bokeh():
    tabs = []
    EEG_sources = []
    MEG_sources = []

    """
    The if should later be used to plot only when channels are selected ==> does not work yet with parse
    """
    if 2 > 1:
        for i in range(1, 7):
            colors = itertools.cycle(palette)

            EEG_temp_source = []
            MEG_temp_source = []

            EEG_data = runs_data[i - 1][0]
            MEG_data = runs_data[i - 1][1]

            EEG_p = figure(title="EEG", plot_height=200, plot_width=1000,
                           tools=TOOLS, output_backend="canvas", x_range=(0, 500), toolbar_location="above")
            MEG_p = figure(title="MEG", plot_height=200, plot_width=1000,
                           tools=TOOLS, output_backend="canvas", x_range=EEG_p.x_range, toolbar_location=None)

            EEG_p.y_range = Range1d(-50, 50)
            MEG_p.y_range = Range1d(-1500, 1500)

            EEG_p.xaxis.axis_label = 'seconds'
            EEG_p.yaxis.axis_label = 'µV'

            MEG_p.xaxis.axis_label = 'seconds'
            MEG_p.yaxis.axis_label = 'fT'
            for channel, color in zip(range(len(EEG_data)), colors):
                source = ColumnDataSource(
                    dict(
                        x=np.arange(0, current, 1),
                        y=EEG_data[channel][:start]))
                EEG_p.line(x='x', y='y', line_width=1, source=source, line_color=color)
                EEG_temp_source.append(source)

            for channel, color in zip(range(len(MEG_data)), colors):
                source = ColumnDataSource(
                    dict(
                        x=np.arange(0, current, 1),
                        y=MEG_data[channel][:start]))
                MEG_p.line(x='x', y='y', line_width=1, source=source, line_color=color)
                MEG_temp_source.append(source)

            x_ticks_loc = [i * 145 for i in range(500)]

            tick_labels = [str(i) for i in range(500)]
            EEG_p.xaxis.ticker = x_ticks_loc
            EEG_p.xaxis.major_label_overrides = dict(zip(x_ticks_loc, tick_labels))

            MEG_p.xaxis.ticker = x_ticks_loc
            MEG_p.xaxis.major_label_overrides = dict(zip(x_ticks_loc, tick_labels))
            EEG_sources.append(EEG_temp_source)
            MEG_sources.append(MEG_temp_source)

            tabs.append(Panel(child=column(EEG_p, MEG_p, sizing_mode="stretch_both"), title=f'Run {i}'))

    curdoc().add_root(Tabs(tabs=tabs))
    return EEG_sources, MEG_sources


EEG_sources, MEG_sources = start_bokeh()

a = 1


def update_callback():
    global a
    global current
    new_current = current + step

    for i in range(1, 7):
        EEG_data = runs_data[i - 1][0]
        MEG_data = runs_data[i - 1][1]

        for idx, EEG_source in enumerate(EEG_sources[i - 1]):
            x = np.arange(current, new_current, 1)
            y = EEG_data[idx][current:new_current]
            new_data = dict()
            new_data['x'] = np.append(EEG_source.data['x'], x)
            new_data['y'] = np.append(EEG_source.data['y'], y)
            EEG_source.data = new_data

        for idx, MEG_source in enumerate(MEG_sources[i - 1]):
            x = np.arange(current, new_current, 1)
            y = MEG_data[idx][current:new_current]
            new_data = dict()
            new_data['x'] = np.append(MEG_source.data['x'], x)
            new_data['y'] = np.append(MEG_source.data['y'], y)
            MEG_source.data = new_data

    current = new_current

    if current >= len(EEG_data[0]) or current >= len(MEG_data[0]):
        curdoc().remove_periodic_callback(pc_id)

    a = a + 1


# put the button and plot in a layout and add to the document
# curdoc().add_root(column(p2, p3, p4, p5, p6, p7, p8))
pc_id = curdoc().add_periodic_callback(update_callback, 3000)
