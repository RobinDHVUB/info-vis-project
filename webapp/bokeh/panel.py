import panel
panel.extension()
from webapp.bokeh.bokeh import EEG_p

bokeh_pane = panel.pane.Bokeh(EEG_p, theme="dark_minimal")

import numpy as np
import plotly.graph_objs as go

xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-(x-1)**2-y**2)-(x**3+y**4-x/5)*np.exp(-(x**2+y**2))

surface = go.Surface(z=z)
layout = go.Layout(
    title='Plotly 3D Plot',
    autosize=False,
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50)
)
fig = dict(data=[surface], layout=layout)

plotly_pane = panel.pane.Plotly(fig)

row = panel.Row(bokeh_pane, plotly_pane, sizing_mode="stretch_both")
row.servable()
