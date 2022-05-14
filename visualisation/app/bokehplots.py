import math
import numpy

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
from bokeh.plotting import figure

import data.access as access

# View
view_size = 10 * 45

# Average plots
def avg_plots(EEG_avgs, MEG_avgs, events, logger):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # Ticks
    run_lengths = [len(group_avg) for group_avg in list(EEG_avgs.values())]
    x_ticks = {
        i * access.avg_sfreq: str(i)
        for i in range(round(max(run_lengths) / access.avg_sfreq) + 1)
    }

    # EEG
    EEG_p = figure(
        title="EEG",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        lod_threshold=None,
        sizing_mode="stretch_both",
    )
    EEG_p.x_range = Range1d(0, view_size)
    EEG_p.xaxis.axis_label = "Time (s)"
    EEG_p.yaxis.axis_label = "µV"
    EEG_p.toolbar.logo = None
    EEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    EEG_p.xaxis.major_label_overrides = x_ticks

    EEG_lines = {group_name: [] for group_name in EEG_avgs.keys()}
    for group_name, group_data in EEG_avgs.items():
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
        EEG_lines[group_name].append(line)
    EEG_p.y_range.renderers = [line for group in EEG_lines.values() for line in group]

    # MEG plot
    MEG_p = figure(
        title="MEG",
        tools=tools,
        toolbar_location=None,
        lod_threshold=None,
        sizing_mode="stretch_both",
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.ticker = [tick for tick in x_ticks.keys()]
    MEG_p.xaxis.major_label_overrides = x_ticks
    MEG_p.xaxis.axis_label = "Time (s)"
    MEG_p.yaxis.axis_label = "fT"
    MEG_p.toolbar.logo = None

    MEG_lines = {group_name: [] for group_name in MEG_avgs.keys()}
    for group_name, group_data in MEG_avgs.items():
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
        MEG_lines[group_name].append(line)
    MEG_p.y_range.renderers = [line for group in MEG_lines.values() for line in group]

    # Events
    renderers = []
    for event in events:
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

    return EEG_p, EEG_lines, MEG_p, MEG_lines


# Window plots
def window_plots(EEG_window_group_avgs, MEG_window_group_avgs, tmin, tplus, logger):

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

    EEG_lines = {group_name: [] for group_name in EEG_window_group_avgs.keys()}
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
        EEG_lines[group_name].append(line)
    EEG_p.y_range.renderers = [line for group in EEG_lines.values() for line in group]

    # MEG plot
    MEG_p = figure(
        title="MEG",
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

    MEG_lines = {group_name: [] for group_name in MEG_window_group_avgs.keys()}
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
        MEG_lines[group_name].append(line)
    MEG_p.y_range.renderers = [line for group in MEG_lines.values() for line in group]

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

    return EEG_p, EEG_lines, MEG_p, MEG_lines


# PSD plots
def psd_plots(EEG_psds, MEG_psds, logger):

    # Tools
    tools = [
        PanTool(dimensions="width"),
        ResetTool(),
        WheelZoomTool(dimensions="width"),
    ]

    # EEG
    EEG_p = figure(
        title="EEG",
        tools=tools,
        toolbar_location="above",
        toolbar_sticky=False,
        sizing_mode="stretch_both",
    )
    EEG_p.xaxis.axis_label = "Frequency (Hz)"
    EEG_p.yaxis.axis_label = "Density"
    EEG_p.toolbar.logo = None

    EEG_lines = {group_name: [] for group_name in EEG_psds.keys()}
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
            EEG_lines[group_name].append(line)
    EEG_p.y_range.renderers = [line for group in EEG_lines.values() for line in group]

    # MEG plot
    MEG_p = figure(
        title="MEG",
        tools=tools,
        toolbar_location=None,
        sizing_mode="stretch_both",
    )
    MEG_p.x_range = EEG_p.x_range
    MEG_p.xaxis.axis_label = "Frequency (Hz)"
    MEG_p.yaxis.axis_label = "Density"
    MEG_p.toolbar.logo = None

    MEG_lines = {group_name: [] for group_name in MEG_psds.keys()}
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
            MEG_lines[group_name].append(line)
    MEG_p.y_range.renderers = [line for group in MEG_lines.values() for line in group]

    return EEG_p, EEG_lines, MEG_p, MEG_lines


# Switching between view modes
select_tmin = Spinner(title="tmin:", low=-1.5, high=0, step=0.1, value=-0.5, width=80)
select_tmax = Spinner(title="tplus:", low=0.1, high=1.5, step=0.1, value=0.5, width=80)



select_events = MultiSelect(
    value=["1"],
    options=[
        (str(event_id + 1), event_name)
        for event_id, event_name in enumerate(access.event_names)
    ],
)