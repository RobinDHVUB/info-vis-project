# myapp.py
import os
from random import random

import mne
import numpy as np
from bokeh.client import push_session
from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
import pandas as pd

"""
Get arguments that are given to session

"""
args = curdoc().session_context.request.arguments

# print(type(args.get("eeg")[0].decode("UTF-8")))
# print(args.get("eeg")[0].decode("UTF-8").split(","))
# print(type(args.get("eeg")[0].decode("UTF-8").split(",")))

"""
Hardcoded path to patient
"""
TOOLS = 'save,xpan,wheel_zoom, reset'
parent_dir = os.path.abspath(os.pardir)
path_to_patient = parent_dir + f"\\data\\ICA_processed\\sub001\\0.fif"
mne_result = mne.io.read_raw_fif(path_to_patient)

start = 200
step = 3000
current = 200
max_len = len(mne_result.get_data()[0, :])


def start_eeg(channels=[0]):
    sources = []
    obj_list = []
    for channel in channels:
        source = ColumnDataSource(
            dict(
                x=np.arange(0, current, 1),
                y=mne_result.get_data()[channel, :start]))
        sources.append(source)

        p = figure(title="Year-wise total number of crimes", plot_height=300,
                   tools=TOOLS, plot_width=600, output_backend="canvas", x_range=(100, 200))
        p.xaxis.axis_label = 'Year'
        p.yaxis.axis_label = 'Total Crimes'
        p.line(x='x', y='y', line_color="purple", line_width=3, source=source)

        obj_list.append(p)

    curdoc().add_root(column(*obj_list))

    return sources, channels


sources, channels = start_eeg([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

a = 1

def reset_data():
    current = 200
    for source in sources:
        source.data = dict(
                x=np.arange(0, current, 1),
                y=mne_result.get_data()[0, :start])
    print("ok")

    curdoc().add_periodic_callback(update_callback, 2000)




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
# put the button and plot in a layout and add to the document
# curdoc().add_root(column(p2, p3, p4, p5, p6, p7, p8))
curdoc().add_root(column(button))
pc_id = curdoc().add_periodic_callback(update_callback, 3000)
