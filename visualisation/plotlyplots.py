import plotly.graph_objects as go
import data_access

# Helper function to create a prettier mesh for the 3D MEG or EEG cap visualization.
# plot_type is expected to be either "meg" or "eeg"
def missing_mesh_idx(plot_type, el_names):
    if plot_type == "eeg":
        return missing_eeg_mesh_idx(el_names)

    return missing_meg_mesh_idx(el_names)


# Helper function to create a prettier mesh for the 3D MEG cap visualization.
# We initially created a more dynamic computation of which additional triangles should be drawn,
# but this seemed to be too variable and would take a lot of time.
# Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
def missing_eeg_mesh_idx(el_names):
    # list of EEG signals that should be connected to fill up some gaps
    els_to_connect = [
        "EEG007",
        "EEG008",
        "EEG002",
        "EEG005",
        "EEG004",
        "EEG038",
        "EEG039",
        "EEG050",
        "EEG003",
        "EEG074",
        "EEG069",
        "EEG029",
        "EEG030",
        "EEG041",
        "EEG040",
        "EEG052",
        "EEG051",
        "EEG001",
        "EEG070",
        "EEG018",
        "EEG060",
        "EEG049",
        "EEG028",
        "EEG027",
        "EEG017",
        "EEG026",
        "EEG016",
        "EEG009",
        "EEG010",
        "EEG059",
        "EEG071",
        "EEG072",
        "EEG073",
        "EEG015",
        "EEG011",
    ]

    # list of indices of the electrode signals in the original list of electrode names/coordinates
    indices = []
    for index, el_name in enumerate(els_to_connect):
        indices.append(el_names.index(el_name))

    # original coordinate indices that should be connected
    i = [
        indices[0],
        indices[3],
        indices[5],
        indices[8],
        indices[11],
        indices[11],
        indices[15],
        indices[17],
        indices[11],
        indices[7],
        indices[5],
        indices[17],
        indices[10],
        indices[20],
        indices[6],
        indices[24],
        indices[24],
        indices[4],
        indices[5],
        indices[15],
        indices[18],
        indices[29],
        indices[30],
        indices[31],
        indices[32],
        indices[9],
        indices[30],
        indices[17],
        indices[8],
        indices[8],
        indices[33],
        indices[2]
    ]

    j = [
        indices[1],
        indices[4],
        indices[6],
        indices[9],
        indices[12],
        indices[14],
        indices[14],
        indices[18],
        indices[12],
        indices[20],
        indices[7],
        indices[16],
        indices[20],
        indices[7],
        indices[22],
        indices[23],
        indices[26],
        indices[27],
        indices[6],
        indices[16],
        indices[17],
        indices[20],
        indices[18],
        indices[18],
        indices[31],
        indices[32],
        indices[8],
        indices[8],
        indices[18],
        indices[31],
        indices [2],
        indices[34]
    ]

    k = [
        indices[2],
        indices[2],
        indices[7],
        indices[10],
        indices[13],
        indices[13],
        indices[16],
        indices[16],
        indices[19],
        indices[10],
        indices[21],
        indices[15],
        indices[9],
        indices[21],
        indices[23],
        indices[25],
        indices[1],
        indices[28],
        indices[23],
        indices[18],
        indices[16],
        indices[9],
        indices[17],
        indices[17],
        indices[17],
        indices[8],
        indices[9],
        indices[18],
        indices[9],
        indices[9],
        indices[1],
        indices[4]
    ]

    return i, j, k


# Helper function to create a prettier mesh for the 3D MEG cap visualization.
# We initially created a more dynamic computation of which additional triangles should be drawn,
# but this seemed to be too variable and would take a lot of time.
# Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
def missing_meg_mesh_idx(el_names):

    # list of MEG signals that should be connected to fill up some gaps
    els_to_connect = [
        "MEG1211",
        "MEG1221",
        "MEG1321",
        "MEG1331",
        "MEG2421",
        "MEG2431",
        "MEG1411",
        "MEG1441",
        "MEG2611",
        "MEG2641",
        "MEG2521",
        "MEG1731",
        "MEG1931",
        "MEG2121",
        "MEG2331",
        "MEG2511",
        "MEG1421",
        "MEG1431",
        "MEG2621",
        "MEG2631",
        "MEG2531",
        "MEG2541",
        "MEG2131",
        "MEG2141",
        "MEG1741",
        "MEG1711",
    ]

    # list of indices of the electrode signals in the original list of electrode names/coordinates
    indices = []
    for index, el_name in enumerate(els_to_connect):
        indices.append(el_names.index(el_name))

    # original coordinate indices that should be connected
    i = [
        indices[0],
        indices[6],
        indices[2],
        indices[17],
        indices[18],
        indices[5],
        indices[20],
        indices[21],
        indices[22],
        indices[24],
    ]
    j = [
        indices[1],
        indices[7],
        indices[16],
        indices[18],
        indices[19],
        indices[19],
        indices[21],
        indices[22],
        indices[13],
        indices[25],
    ]
    k = [
        indices[6],
        indices[2],
        indices[17],
        indices[3],
        indices[4],
        indices[20],
        indices[15],
        indices[14],
        indices[23],
        indices[11],
    ]

    return i, j, k


# helper function to get selection-specific attributes,
# i.e., the electrode plot attributes used to distinguish selected markers from unselected markers
def get_marker_values(selected):
    size = 10 if selected else 9
    opacity = 1 if selected else 0.6
    line_color = "black" if selected else "white"

    return {"size": size, "opacity": opacity, "line_color": line_color}


# generate a 3D visualization of an EEG or MEG "electrode cap"
# plot_type is expected be either "eeg" or "meg" and is used to fill up "gaps" in the mesh
def electrode_plot(el_names, el_types, el_coords, mesh_coords, plot_type, group_toggles=None):

    # get the unique group names
    group_names = list(set(el_types))

    # collect the indices per group
    electrode_indices = {group_name: [] for group_name in group_names}
    for el_index, el_type in enumerate(el_types):
        electrode_indices[el_type].append(el_index)

    # generate and store the trace per group
    electrode_traces = {}

    # get the coordinates of all electrodes
    el_x = el_coords[0]
    el_y = el_coords[1]
    el_z = el_coords[2]

    # get the coordinates for the mesh beneath the electrodes (mesh is added to have a clearer view)
    mesh_x = mesh_coords[0]
    mesh_y = mesh_coords[1]
    mesh_z = mesh_coords[2]

    for group_name in group_names:
        trace_x = [el_x[i] for i in electrode_indices[group_name]]
        trace_y = [el_y[i] for i in electrode_indices[group_name]]
        trace_z = [el_z[i] for i in electrode_indices[group_name]]
        trace_names = [el_names[i] for i in electrode_indices[group_name]]
        trace_colors = [data_access.group_colors[el_types[i]] for i in electrode_indices[group_name]]

        marker_values = get_marker_values(group_toggles is not None and group_name in group_toggles and group_toggles[group_name])

        electrode_traces[group_name] = go.Scatter3d(
            name=group_name, # set the group name, so we can easily select on this name for modifying specific traces
            x=trace_x,
            y=trace_y,
            z=trace_z,
            mode="markers",
            hovertemplate="%{text}<extra></extra>",
            text=trace_names,
            marker=dict(
                symbol="circle",
                size=marker_values["size"],
                color=trace_colors,
                opacity=marker_values["opacity"],
                line=dict(color=marker_values["line_color"], width=1),
            ),
        )

    # trace for the mesh
    trace_mesh = go.Mesh3d(
        hoverinfo="skip",
        opacity=1,
        color="#C0C0C0",
        x=mesh_x,
        y=mesh_y,
        z=mesh_z,
    )

    # add missing Mesh connections for a prettier mesh
    missing_i, missing_j, missing_k = missing_mesh_idx(plot_type, el_names)
    trace_missing_mesh = go.Mesh3d(
        hoverinfo="skip",
        opacity=1,
        color="#C0C0C0",
        type="mesh3d",
        x=mesh_x,
        y=mesh_y,
        z=mesh_z,
        i=missing_i,
        j=missing_j,
        k=missing_k,
    )

    # include all traces
    data = [trace_mesh, trace_missing_mesh]
    data.extend(electrode_traces.values())

    # don't include any grids, axes, etc. (since we just want the 3D figure)
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            # camera?
            bgcolor="#E8FCFF",
            xaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
            zaxis=dict(
                title="",
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showspikes=False,
                visible=False,
            ),
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(paper_bgcolor="#E8FCFF")
    fig.update_layout(plot_bgcolor="#E8FCFF")

    return fig

# update fig, which is the 3D visualization of an EEG or MEG "electrode cap"
# group_toggles is a dictionary containing group names as key and as value True if that group should be selected
# and False if not
def update_electrode_plot(fig, group_toggles):

    # get the attributes that should be updated to distinguish between selected and unselected markers
    selected_markers = get_marker_values(True)
    unselected_markers = get_marker_values(False)

    # update all traces with the same name as the group name in group_toggles
    for group_name, group_toggle in group_toggles.items():
        # if the group_toggle has value True, we should update the trace, so it looks selected
        if group_toggle:
            fig.update_traces(
                marker=dict(
                    size=selected_markers["size"],
                    opacity=selected_markers["opacity"],
                    line=dict(
                        color=selected_markers["line_color"]
                    )
                ),
                selector=dict(name=group_name)
            )
        else:
            # if the group_toggle has value False, we should update the trace, so it looks unselected
            fig.update_traces(
                marker=dict(
                    size=unselected_markers["size"],
                    opacity=unselected_markers["opacity"],
                    line=dict(
                        color=unselected_markers["line_color"]
                    )
                ),
                selector=dict(name=group_name)
            )

    return fig