# myapp.py
import itertools
import logging
import os
from random import random
from bokeh.palettes import Dark2_5 as palette

import mne
import numpy as np
from bokeh.client import push_session
from bokeh.io import show
from bokeh.layouts import column, gridplot, row
from bokeh.models import Button, ColumnDataSource, PanTool
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

TOOLS = "xpan"

start = 500
step = 3000
current = 500

runs_data = [parse_run(int(subject_id[0]), run, EEG_channels, MEG_channels) for run in [1, 1, 1, 1, 1, 1]]
logger.info("logging...")
logger.info(runs_data)


def start_bokeh():
    EEG_plots = []
    MEG_plots = []

    if len(EEG_channels) > 4:
        for i in range(1, 7):
            if i == 1:
                toolbar = "above"
            else:
                toolbar = None

            colors = itertools.cycle(palette)

            EEG_data = runs_data[i - 1][0]

            EEG_p = figure(title=f'Run {i}:', plot_height=200,
                           tools=TOOLS, output_backend="canvas", x_range=(0, 500), toolbar_location=toolbar)
            EEG_p.xaxis.axis_label = 'seconds'
            EEG_p.yaxis.axis_label = 'µV'
            for channel, color in zip(range(len(EEG_data)), colors):
                source = ColumnDataSource(
                    dict(
                        x=np.arange(0, current, 1),
                        y=EEG_data[channel][:start]))
                EEG_p.line(x='x', y='y', line_width=3, source=source, line_color=color)

            x_ticks_loc = [i * 145 for i in range(500)]

            tick_labels = [str(i) for i in range(500)]
            EEG_p.xaxis.ticker = x_ticks_loc
            EEG_p.xaxis.major_label_overrides = dict(zip(x_ticks_loc, tick_labels))
            EEG_plots.append(EEG_p)

    if len(MEG_channels) > 4:
        for i in range(1, 7):
            if i == 1:
                toolbar = "above"
            else:
                toolbar = None

            """
            source = ColumnDataSource(
                dict(
                    x=np.arange(0, current, 1),
                    y=runs_data[0][i - 1][:start]))
            """
            MEG_p = figure(title=f'Run {i}:', plot_height=200,
                           tools=TOOLS, output_backend="canvas", x_range=(100, 200), toolbar_location=toolbar)
            MEG_p.xaxis.axis_label = 'samples'
            MEG_p.yaxis.axis_label = 'µV'
            MEG_p.line(x='x', y='y', line_color="purple", line_width=3)
            MEG_plots.append(MEG_p)

    curdoc().add_root(row(column(EEG_plots), column(MEG_plots), sizing_mode="scale_width"))


start_bokeh()

"""
def start_eeg(channels=[0]):
    sources = []
    obj_list = []
    for channel in channels:
        source = ColumnDataSource(
            dict(
                x=np.arange(0, current, 1),
                y=np.arange(0, current, 1)))
        sources.append(source)

        p = figure(title="Electrode_name", plot_height=300,
                   tools=TOOLS, plot_width=600, output_backend="canvas", x_range=(100, 200))
        p.xaxis.axis_label = 'samples'
        p.yaxis.axis_label = 'µV'
        p.line(x='x', y='y', line_color="purple", line_width=3, source=source)

        obj_list.append(p)

    curdoc().add_root(column(*obj_list))

    return sources, channels


sources, channels = start_eeg([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
"""

a = 1

"""
def update_callback():
    global a
    global current
    global sources
    new_current = current + step
    for source, channel, idx in zip(sources, channels, range(len(channels))):
        new_mne_data = mne_result.get_data()[channel, current:new_current]
        x = np.arange(current, new_current, 1)
        new_data = dict()
        new_data['x'] = np.append(source.data['x'], x)
        new_data['y'] = np.append(source.data['y'], new_mne_data)
        source.data = new_data

    current = new_current

    if current >= max_len:
        curdoc().remove_periodic_callback(pc_id)

    a = a + 1

button = Button(label="reset", button_type="success")
button.on_click(reset_data)

"""
# put the button and plot in a layout and add to the document
# curdoc().add_root(column(p2, p3, p4, p5, p6, p7, p8))
# pc_id = curdoc().add_periodic_callback(update_callback, 3000)
