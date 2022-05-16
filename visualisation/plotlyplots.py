import plotly.graph_objects as go
import data_access


# Helper function to create a prettier mesh for the 3D MEG/EEG cap visualization.
# We initially created a more dynamic computation of which additional triangles should be drawn,
# but this seemed to be too variable and would take a lot of time.
# Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
def missing_mesh_idx(plot_type, el_names):

    if plot_type.lower() == "meg":
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
    else:
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


# convert a list of electrode types to a list of colors
def types_to_colors(el_types):
    return [data_access.group_colors[el_type] for el_type in el_types]


# generate a 3D visualization of an EEG or MEG "electrode cap"
# plot_type is expected be either "eeg" or "meg" and is used to fill up "gaps" in the mesh
def electrode_plot(el_names, el_types, el_coords, mesh_coords, plot_type):

    # get the coordinates of all electrodes
    el_x = el_coords[0]
    el_y = el_coords[1]
    el_z = el_coords[2]

    # get the coordinates for the mesh beneath the electrodes (mesh is added to have a clearer view)
    mesh_x = mesh_coords[0]
    mesh_y = mesh_coords[1]
    mesh_z = mesh_coords[2]

    # get the non-selected elements
    el_colors = types_to_colors(el_types)

    # trace for the non-selected electrodes
    trace_non = go.Scatter3d(
        x=el_x,
        y=el_y,
        z=el_z,
        mode="markers",
        hovertemplate="%{text}<extra></extra>",
        text=el_names,
        marker=dict(
            symbol="circle",
            size=12,
            color=el_colors,
            opacity=0.6,
            line=dict(color="white", width=1),
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
    data = [trace_non, trace_mesh, trace_missing_mesh]

    # don't include any grids, axes, etc. (since we just want the 3D figure)
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            # camera?
            bgcolor="#EAEAEA",
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
    fig.update_layout(paper_bgcolor="#EAEAEA")
    fig.update_layout(plot_bgcolor="#EAEAEA")
    return fig

