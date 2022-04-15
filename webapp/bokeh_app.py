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

args = curdoc().session_context.request.arguments

# print(type(args.get("eeg")[0].decode("UTF-8")))
# print(args.get("eeg")[0].decode("UTF-8").split(","))
# print(type(args.get("eeg")[0].decode("UTF-8").split(",")))


# create a plot and style its properties
p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

# add a text renderer to the plot (no data yet)
r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
           text_baseline="middle", text_align="center")

i = 0

ds = r.data_source


# create a callback that adds a number in a random location
def callback():
    global i

    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random() * 70 + 15]
    new_data['y'] = ds.data['y'] + [random() * 70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i % 3]]
    new_data['text'] = ds.data['text'] + [str(i)]
    ds.data = new_data

    i = i + 1


TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'
parent_dir = os.path.abspath(os.pardir)
path_to_patient = parent_dir + f"\\data\\ICA_processed\\sub001\\0.fif"
mne_result = mne.io.read_raw_fif(path_to_patient)

start = 200
step = 200
current = 200
x = range(current)
mne_data = mne_result.get_data()[0, :start]
max_len = len(mne_result.get_data()[0, :])

source = ColumnDataSource(dict(
    x=np.arange(0, current, 1), y=mne_data
))

a = 1

p2 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p2.xaxis.axis_label = 'Year'
p2.yaxis.axis_label = 'Total Crimes'
p2.line(x='x', y='y', line_color="purple", line_width=3, source=source)


def per_callback():
    global a
    global current
    new_current = current + (a * start)
    new_mne_data = mne_result.get_data()[0, current:new_current]
    x = np.arange(current, new_current, 1)
    new_data = dict()
    new_data['x'] = np.append(source.data['x'], x)
    new_data['y'] = np.append(source.data['y'], new_mne_data)
    source.data = new_data
    current = new_current

    if current >= max_len:

        curdoc().remove_periodic_callback(pc_id)

    a = a + 1


p3 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p3.xaxis.axis_label = 'Year'
p3.yaxis.axis_label = 'Total Crimes'
p3.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

p4 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p4.xaxis.axis_label = 'Year'
p4.yaxis.axis_label = 'Total Crimes'
p4.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

p5 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p5.xaxis.axis_label = 'Year'
p5.yaxis.axis_label = 'Total Crimes'
p5.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

p6 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p6.xaxis.axis_label = 'Year'
p6.yaxis.axis_label = 'Total Crimes'
p6.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

p7 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p7.xaxis.axis_label = 'Year'
p7.yaxis.axis_label = 'Total Crimes'
p7.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

p8 = figure(title="Year-wise total number of crimes", y_axis_type="linear", plot_height=400,
            tools=TOOLS, plot_width=800, output_backend="canvas", x_range=(100, 200))
p8.xaxis.axis_label = 'Year'
p8.yaxis.axis_label = 'Total Crimes'
p8.line(x=range(len(mne_data)), y=mne_data, line_color="purple", line_width=3)

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)
button2 = Button(label="Press Me")

# put the button and plot in a layout and add to the document
curdoc().add_root(column(p2, p3, p4, p5, p6, p7, p8))
pc_id = curdoc().add_periodic_callback(per_callback, 2000)
