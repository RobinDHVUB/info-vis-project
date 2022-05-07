/* Main function that initializes everything that is needed for our visualization */
function initializeVisualizations() {

    // last stored cameraScene of each 3D plot
    eegCameraScene = {
        camera: {
            up: {
                x: 0,
                y: 0,
                z: 1
            },
            center: {
                x: 0,
                y: 0,
                z: 0
            },
            eye: {
                x: 1.25,
                y: 1.25,
                z: 1.25
            },
        },
    }

    megCameraScene = {
        camera: {
            up: {
                x: 0,
                y: 0,
                z: 1
            },
            center: {
                x: 0,
                y: 0,
                z: 0
            },
            eye: {
                x: 1.25,
                y: 1.25,
                z: 1.25
            },
        },
    }

    /* Function to update the subject select box based on the last filter values */
    function updateSelect(newdata) {
        // Get all filter values
        var slider_bot = $('#ageSlider').data("from")
        var slider_top = $('#ageSlider').data("to")
        var chosen_sex = d3.select("#subject-sex input:checked").attr("value")
        var chosen_hand = d3.select("#subject-hand input:checked").attr("value")

        // Filter the given data based on the filter values
        newdata = Array.from(newdata).filter(function(d) {
            return d.age >= slider_bot && d.age <= slider_top
                && (d.sex === chosen_sex || chosen_sex === 'all')
                && (d.hand === chosen_hand || chosen_hand === 'all')
        })

        // Update the options of the subject select box, based on the filtered data
        var select = d3.select("#subject-selection select");

        var options = select.selectAll("option")
            .data(newdata, function (d) {
                return d.id;
            });

        options.enter()
            .append('option')
            .text(function(d) {
                var sex = d.sex === 'm' ? 'male' : 'female'
                var hand = d.hand === 'l' ? 'left' : 'right'
                return "Subject " + d.id + ": " + sex + ", " + d.age + ", " + hand
            })

        options.exit().remove();
    }

    /* Function that checks whether the analysis button should be enabled or disabled (and enables/disables the button) */
    function checkAnalysis(selectedSubject) {
        // at least one cortex option and subject should be selected to be able to start an analysis
        if ((typeof selectedSubject === 'undefined') ||
            (d3.selectAll("#eeg-checkbox-container input:checked").empty()
                && d3.selectAll("#meg-checkbox-container input:checked").empty())) {
            d3.select("#startAnalysis").classed("disabled", true)
            d3.select(".analysis-wrapper").attr('data-bs-original-title', "Please select a subject and signal(s) first.")
        }
        else {
            d3.select("#startAnalysis").classed("disabled", false)
            d3.select(".analysis-wrapper").attr('data-bs-original-title', "Analyze the selected signals.");
        }
    }

    /*
    Function to store the camera scene of a 3DPlot
    - plotType is expected to be 'eeg' or 'meg'
    */
    function updateCameraScene(plotType, data) {
        if (plotType.includes('eeg')
            && (typeof data !== 'undefined')
            && (typeof data["scene.camera"] !== 'undefined')) {
            eegCameraScene={
                camera: {
                    center:data["scene.camera"]["center"],
                    eye: data["scene.camera"]["eye"],
                    projection: data["scene.camera"]["projection"],
                    up: data["scene.camera"]["up"],
                }
            }
        }
        else if (plotType.includes('meg')
            && (typeof data !== 'undefined')
            && (typeof data["scene.camera"] !== 'undefined')) {
            megCameraScene={
                camera: {
                    center:data["scene.camera"]["center"],
                    eye: data["scene.camera"]["eye"],
                    projection: data["scene.camera"]["projection"],
                    up: data["scene.camera"]["up"],
                }
            }
        }
        else {
                eegCameraScene = {
                    camera: {
                        up: {
                            x: 0,
                            y: 0,
                            z: 1
                        },
                        center: {
                            x: 0,
                            y: 0,
                            z: 0
                        },
                        eye: {
                            x: 1.25,
                            y: 1.25,
                            z: 1.25
                        },
                    },
                }

                megCameraScene = {
                    camera: {
                        up: {
                            x: 0,
                            y: 0,
                            z: 1
                        },
                        center: {
                            x: 0,
                            y: 0,
                            z: 0
                        },
                        eye: {
                            x: 1.25,
                            y: 1.25,
                            z: 1.25
                        },
                    },
                }
        }
    }

    /* Function for visualizing EEG electrode cap in 3D, based on the current subject that is selected */
    function visualizeEEG(eeg_names, eeg_colors, eeg_selection, eeg_coords, mesh_coords, keepCamera) {
        visualize3D("eeg", eeg_names, eeg_colors, eeg_selection, eeg_coords, mesh_coords, keepCamera)
    }

    /* Function for visualizing MEG electrode cap in 3D, based on the current subject that is selected */
    function visualizeMEG(meg_names, meg_colors, meg_selection, meg_coords, mesh_coords, keepCamera) {
        visualize3D("meg", meg_names, meg_colors, meg_selection, meg_coords, mesh_coords, keepCamera)
    }

    /*
    Function for visualizing EEG or MEG electrode cap in 3D, based on the current subject that is selected.
    - keepCamera is a parameter specifying whether the virtual camera position should be reset when updating the visualization.
    - plotType is expected to be 'eeg' or 'meg'
    */
    function visualize3D(plotType, el_names, el_colors, el_selection, el_coords, mesh_coords, keepCamera)
    {
        // get the div to show the 3D plot in
        var graphDiv = document.getElementById(plotType + "Plot")

        // get the coordinates of all EEG electrodes
        var el_x = el_coords[0]
        var el_y = el_coords[1]
        var el_z = el_coords[2]

        // get the coordinates for the mesh beneath the EEG electrodes (mesh is added for having a clearer view)
        var mesh_x = mesh_coords[0]
        var mesh_y = mesh_coords[1]
        var mesh_z = mesh_coords[2]

        // split up the data in sets for selected electrodes and non-selected electrodes to easily visualize them differently
        var el_selected_x = []
        var el_selected_y = []
        var el_selected_z = []
        var el_selected_names = []
        var el_selected_colors = []

        var el_nonselected_x = []
        var el_nonselected_y = []
        var el_nonselected_z = []
        var el_nonselected_names = []
        var el_nonselected_colors = []

        var el_selected = []
        for (var i = 0; i < el_selection.length; i++) {
            if (el_selection[i]) {
                el_selected_x.push(el_x[i])
                el_selected_y.push(el_y[i])
                el_selected_z.push(el_z[i])
                el_selected_names.push(el_names[i])
                el_selected_colors.push(el_colors[i])
            }
            else {
                el_nonselected_x.push(el_x[i])
                el_nonselected_y.push(el_y[i])
                el_nonselected_z.push(el_z[i])
                el_nonselected_names.push(el_names[i])
                el_nonselected_colors.push(el_colors[i])
            }
        }

        // trace for the non-selected electrodes
        var traceNon = {
            x: el_nonselected_x,
            y: el_nonselected_y,
            z: el_nonselected_z,
            mode: 'markers',
            hovertemplate: '%{text}<extra></extra>',
            text: el_nonselected_names,
            marker: {
                symbol: 'circle',
                size: 12,
                color: el_nonselected_colors,
                opacity: 0.6,
                line: {
                    color: 'white',
                    width: 1
                },
            },
            type: 'scatter3d'
        };

        // trace for the selected electrodes
        var traceSel = {
            x: el_selected_x,
            y: el_selected_y,
            z: el_selected_z,
            mode: 'markers',
            hovertemplate: '%{text}<extra></extra>',
            text: el_selected_names,
            marker: {
                symbol: 'circle',
                size: 14,
                color: el_selected_colors,
                opacity: 1,
                line: {
                    color: 'black',
                    width: 1
                },
            },
            type: 'scatter3d'
        };

        // trace for the mesh
        var traceMesh = {
                hoverinfo:'skip',
                opacity:1,
                color: 'rgb(300,100,200)',
                type: 'mesh3d',
                x: mesh_x,
                y: mesh_y,
                z: mesh_z,
            }

        // get the camera position to use (either the default one or the last stored one)
        var cameraValue = {
            up: {
                x: 0,
                y: 0,
                z: 1
            },
            center: {
                x: 0,
                y: 0,
                z: 0
            },
            eye: {
                x: 1.25,
                y: 1.25,
                z: 1.25
            },
        };
        if (keepCamera) {
            if (plotType.includes("eeg")) {
                cameraValue = eegCameraScene["camera"]
            }
            else {
                cameraValue = megCameraScene["camera"]
            }
        }

        // we show all traces in the same plot but without any grids, axes, etc. (since we just want the 3D figure)
        var data = [traceNon, traceSel, traceMesh];
        var layout = {
            showlegend: false,
            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0
            },
            scene:{
                camera: cameraValue,
                bgcolor: '#fff',
                xaxis: {
                    title: '',
                    showgrid: false,
                    zeroline: false,
                    showline: false,
                    autotick: false,
                    ticks: '',
                    showticklabels: false,
                    showspikes: false
                },
                yaxis: {
                    title: '',
                    ticks: '',
                    showline: false,
                    zeroline: false,
                    showgrid: false,
                    showticklabels: false,
                    showspikes: false,
                },
                zaxis: {
                    title: '',
                    ticks: '',
                    showline: false,
                    zeroline: false,
                    showgrid: false,
                    showticklabels: false,
                    showspikes: false
                }
            }
        };

        // show the (updated) 3D plot
        Plotly.react(graphDiv, data, layout, {displayModeBar: false, scrollZoom: false, responsive: true});

        // keep track of camera changes
        graphDiv.on('plotly_relayout', function(data) {
            return updateCameraScene(plotType, data)
        });
    }

    // read in the subject data from the JSON file and initialize everything based on this data
    d3.json("/static/json/subject_data.json").then(function(data)
    {
        // names
        eeg_names = data["eeg_names"]
        meg_names = data["meg_names"]

        // types
        eeg_types = data["eeg_types"]
        meg_types = data["meg_types"]

        // coordinates (MEG coordinates are fixed, EEG coordinates are stored per subject)
        meg_coords = data["meg_coords"]
        meg_mesh_coords = data["meg_mesh_coords"]

        // specify the color for each type of cortex
        eeg_colors = []
        for (var i = 0; i < eeg_types.length; i++) {
            if (eeg_types[i].toLowerCase() === "frontal lobe") {
                eeg_colors[i] = "red"
            }
            else if (eeg_types[i].toLowerCase() === "parietal lobe") {
                eeg_colors[i] = "blue"
            }
            else if (eeg_types[i].toLowerCase() === "occipital lobe") {
                eeg_colors[i] = "orange"
            }
            else if (eeg_types[i].toLowerCase() === "temporal lobe (l)") {
                eeg_colors[i] = "yellow"
            }
            else if (eeg_types[i].toLowerCase() === "temporal lobe (r)"){
                eeg_colors[i] = "black"
            }
            else
            {
                console.log("invalid type: " +  eeg_types[i])
            }
        }

        meg_colors = []
        for (var i = 0; i < meg_types.length; i++) {
            if (meg_types[i].toLowerCase() === "frontal lobe") {
                meg_colors[i] = "red"
            }
            else if (meg_types[i].toLowerCase() === "parietal lobe") {
                meg_colors[i] = "blue"
            }
            else if (meg_types[i].toLowerCase() === "occipital lobe") {
                meg_colors[i] = "orange"
            }
            else if (meg_types[i].toLowerCase() === "temporal lobe (l)") {
                meg_colors[i] = "yellow"
            }
            else if (meg_types[i].toLowerCase() === "temporal lobe (r)"){
                meg_colors[i] = "black"
            }
            else
            {
                console.log("invalid type: " + meg_types[i])
            }
        }

        // keep track of which electrodes have been selected (initially none are selected)
        eeg_selection = Array(eeg_types.length).fill().map(_ => false)
        meg_selection = Array(meg_types.length).fill().map(_ => false)

        // subject data
        subjects=data["subjects"]

        // data to show in the select (all subjects)
        selectData = new Set(subjects)

        // keep track of which subject is currently selected
        selectedSubject = undefined

        // Update select options when sex filter changes
        d3.selectAll("#subject-sex input").on("change", function(d) {
            updateSelect(selectData)
            handleSubjectChange()
        })

        // Update select options when handedness filter changes
        d3.selectAll("#subject-hand input").on("change", function(d) {
            updateSelect(selectData)
            handleSubjectChange()
        })

        // Initialize a slider for subject age filtering and update select options on change
        const minAge = d3.min(subjects, d => d.age)
        const maxAge = d3.max(subjects, d => d.age)

        // we round of to the nearest 5 on the slider
        var minLimit = 0
        var maxLimit = 0

        const lastDigitMin = Number(String(minAge).slice(-1))
        if (lastDigitMin == 5) {
            minLimit = minAge
        }
        else if (lastDigitMin < 5) {
            minLimit = ((minAge/10) | 0) * 10
        }
        else {
            minLimit = Number(String(minAge).slice(0, -1) + "5")
        }

        const lastDigitMax = Number(String(maxAge).slice(-1))
        if (lastDigitMax == 5) {
            maxLimit = maxAge
        }
        else if (lastDigitMax < 5) {
            maxLimit = Number(String(maxAge).slice(0, -1) + "5")
        }
        else {
            maxLimit = (((maxAge + 10)/10) | 0) * 10
        }

        $("#ageSlider").ionRangeSlider({
            type: "double",
            min: minLimit,
            max: maxLimit,
            from: minAge,
            to: maxAge,
            grid: true,
            grid_num: 3,
            step: 1,
            onChange: function (data) {
                 updateSelect(selectData);
                 handleSubjectChange();
            },
         });

        // update which EEG electrodes have been selected after checking one of the electrode checkboxes
        d3.selectAll("#eeg-checkbox-container input").on("change", function(d) {
          const isChecked = d3.select(this).property("checked")
          const boxValue = d3.select(this).property("value")

          for (var i = 0; i < eeg_types.length; i++) {
            if (eeg_types[i].toLowerCase() === boxValue.toLowerCase()) {
              eeg_selection[i] = isChecked
            }
          }

          visualizeEEG(eeg_names, eeg_colors, eeg_selection, selectedSubject.eeg_coords, selectedSubject.mesh_coords, true)
          checkAnalysis(selectedSubject)
        })

        // update which MEG electrodes have been selected after checking one of the electrode checkboxes
        d3.selectAll("#meg-checkbox-container input").on("change", function(d) {
          const isChecked = d3.select(this).property("checked")
          const boxValue = d3.select(this).property("value")

          for (var i = 0; i < meg_types.length; i++) {
            if (meg_types[i].toLowerCase() === boxValue.toLowerCase()) {
              meg_selection[i] = isChecked
            }
          }

          visualizeMEG(meg_names, meg_colors, meg_selection, meg_coords, meg_mesh_coords, true)
          checkAnalysis(selectedSubject)
        })

        /* Function to handle changing the selected subject */
        function handleSubjectChange() {
            var selectedOption = d3.selectAll("#subject-selection option:checked");

            // if no subject is selected we purge the 3D plots and disable selecting cortex checkboxes
            if (selectedOption.empty()){
                selectedSubject = undefined
                Plotly.purge(document.getElementById('eegPlot'))
                Plotly.purge(document.getElementById('megPlot'))
                d3.selectAll('#eeg-checkbox-container label').classed("disabled", true)
                d3.selectAll('#meg-checkbox-container label').classed("disabled", true)

                // also reset the camera view to its default value
                updateCameraScene("eeg", undefined)
                updateCameraScene("meg", undefined)
            }
            else {
                // if a subject is selected we update the 3D plots and enable selecting cortex checkboxes
                var newData = selectedOption.data();
                if ((typeof selectedSubject === 'undefined') || (selectedSubject["id"] !== newData[0]["id"])) {
                    selectedSubject = newData[0]
                    d3.selectAll('#eeg-checkbox-container label').classed("disabled", false)
                    d3.selectAll('#meg-checkbox-container label').classed("disabled", false)

                    visualizeEEG(eeg_names, eeg_colors, eeg_selection, selectedSubject.eeg_coords,
                        selectedSubject.mesh_coords, false)
                    visualizeMEG(meg_names, meg_colors, meg_selection, meg_coords, meg_mesh_coords, false)
                }
            }

            // check whether starting an analysis should be possible
            checkAnalysis(selectedSubject)
        }

        // update the EEG and MEG 3D plots when selecting another subject
        d3.select('#subject-selector')
          .on('change', handleSubjectChange);

        // fill the select options with all the subjects (and select the first one)
        updateSelect(subjects)
        handleSubjectChange()
    }).catch(function(error)
    {
        console.log(error)
    });
};

/*
Function to create a String summary of the most important subject information
*/
function createSubjectInfo(subjectData) {
    var sex = subjectData.sex === 'm' ? 'male' : 'female'
    var hand = subjectData.hand === 'l' ? 'left-handed' : 'right-handed'

    return "Subject " + subjectData.id + ": " + sex + ", " + subjectData.age + " years old, " + hand
}

/*
Function to go back to subject selection
*/
function subjectSelectionPage() {
    // hide the first page and "start analysis" button
    d3.select(".main-wrapper").classed("d-none", false)
    d3.select(".analysis-wrapper").classed("d-none", false)

    // show the back button
    d3.select(".back-btn-wrapper").classed("d-none", true)
    d3.select("#backToSubjectSel").classed("disabled", true)
    d3.select(".loading-screen").classed("d-none", true)
    $(".bokeh-wrapper").html("");
    $("script").last().remove()

    // replace the the subject info by the title
    d3.select("#datasetUrl").classed("d-none", false)
    d3.select("#subjectInfoSummary").classed("d-none", true)

    // TODO: Close Bokeh connection/socket!!!
}

/* Function to build a dictionary with an array of electrodes (value) for each electrode type (key) */
function groupPerType(elecTypes, elecs) {
    var dict = {}

    for (var i = 0; i < elecs.length; i++) {
        const elecType = elecTypes[i]
        const elec = elecs[i]

        if (dict.hasOwnProperty(elecType)) {
            dict[elecType].push(elec)
        }
        else {
            dict[elecType] = [elec]
        }
    }

    return dict
}

/* Function to go to the signals analysis page */
function startAnalysis()
{
    // get the selected subjects (there will only be one subject selected in our visualization)
    var subject = undefined
    var subject_ids = []
    d3.selectAll("#subject-selection option:checked").data().forEach(function(d) {
        subject = d;
        subject_ids.push(d.id);
    });

    // get the selected EEG channels
    var eeg_channels = []
    var eeg_channel_types = []
    for (var i = 0; i < eeg_selection.length; i++) {
        if (eeg_selection[i]) {
            eeg_channels.push(eeg_names[i])
            eeg_channel_types.push(eeg_types[i])
        }
    }

    // get the selected MEG channels
    var meg_channels = []
    var meg_channel_types = []
    for (var i = 0; i < meg_selection.length; i++) {
        if (meg_selection[i]) {
          meg_channels.push(meg_names[i])
          meg_channel_types.push(meg_types[i])
        }
    }

    const sel = JSON.stringify({
        "subject": subject_ids[0],
        "eeg": groupPerType(eeg_channel_types, eeg_channels),
        "meg": groupPerType(meg_channel_types, meg_channels)
    });

    // hide the first page and "start analysis" button
    d3.select(".main-wrapper").classed("d-none", true)
    d3.select(".analysis-wrapper").classed("d-none", true)

    // show the back button
    d3.select(".back-btn-wrapper").classed("d-none", false)
    d3.select(".loading-screen").classed("d-none", false)

    // replace the title by the subject info
    d3.select("#datasetUrl").classed("d-none", true)
    d3.select("#subjectInfoSummary").classed("d-none", false)

    // put the correct subjectInfo into the summary
    console.log(d3.select("#subjectInfoSummary span"))
    d3.select("#subjectInfoSummary span").html(createSubjectInfo(subject))

    $.ajax({
        type: 'POST',
        url: "/data",
        data: sel,
        dataType: 'html',
        contentType: 'application/json',
        success: function(data){
            /*
              Since Bokeh doesn't fire an accessible event when all items are rendered, we can only check for the message
              it emits once it's finished. We remove the loading screen spinner once all items are rendered.
              This was based on: https://stackoverflow.com/questions/42794556/how-to-check-if-my-bokeh-server-application-is-completely-loaded-and-rendered
             */
            oldLog = console.log;
            console.log = function (message) {
                if (message.localeCompare('Bokeh items were rendered successfully') == 0) {
                    d3.select("#backToSubjectSel").classed("disabled", false)
                    d3.select(".loading-screen").classed("d-none", true)
                    console.log = oldLog;
                }
                oldLog.apply(console, arguments);
            };

            // add the Bokeh plot to the page
            $(".bokeh-wrapper").append(data);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log("nok")
            console.log(xhr.status);
            console.log(thrownError);
        }
    });

    // Go to Bokeh

    /* location.href = `http://localhost:5000/data?id=1&MEG=[1,2,3,4]&EEG=${eeg_values}`; */
    //location.href = `http://localhost:5006/app?id=` + subject_ids + `&EEG=` + eeg_channels + `&MEG=` + meg_channels;
}

/* UNUSED FUNCTIONS */

/*
This function generates a standard 2D view of EEG electrodes using D3.
However, it is currently unused since 3D visualization was eventually deemed more informative and especially more correct.
*/
function drawEEGElectrodeSelector() {
    // general sizing info of figure
    const ear_size = 25
    const nose_height = 40
    const electrode_size = 15
    const width = 450, height = 450;
    const margin = {top: 25 + nose_height, right: 25 + ear_size, bottom: 25, left: 25 + ear_size};


    const svg = d3.select("#eeg-selection-container")
        .append("svg")
        .attr("class", "eeg_head")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    // add an ellipsis for general head shape
    svg.append("ellipse")
        .attr("cx", width / 2)
        .attr("cy", height / 2)
        .attr("rx", width / 2)
        .attr("ry", height / 2)
        .attr('stroke-width', 2)
        .attr("stroke", "black")
        .attr("fill", "none");

    // add the left ear
    svg.append("path")
        .attr("transform", "translate(0," + height / 2 + ")")
        .attr("d", d3.arc()
            .innerRadius(ear_size)
            .outerRadius(ear_size)
            .startAngle(3.14)     // angle is in radian (pi = 3.14 = bottom).
            .endAngle(6.28)       // 2*pi = 6.28 = top
        )
        .attr('stroke', 'black')
        .attr("stroke-width", 2)
        .attr("fill", "none");

    // add the right ear
    svg.append("path")
        .attr("transform", "translate(" + width + "," + height / 2 + ")")
        .attr("d", d3.arc()
            .innerRadius(ear_size)
            .outerRadius(ear_size)
            .startAngle(-3.14)
            .endAngle(-6.28)
        )
        .attr('stroke', 'black')
        .attr("stroke-width", 2)
        .attr("fill", "none");

    // add the nose
    var bezierLine = d3.line()
        .x(function (d) {
            return d.x;
        })
        .y(function (d) {
            return d.y;
        })
        .curve(d3.curveBasis);

    var lineData = [{"x": width / 2 - ear_size, "y": 1}, {
        "x": width / 2,
        "y": -nose_height
    }, {"x": width / 2 + ear_size, "y": 1}];

    svg.append("path")
        .attr("d", bezierLine(lineData))
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("fill", "none");

    // add a horizontal midline
    svg.append('line')
        .attr('x1', 0)
        .attr('y1', height / 2)
        .attr('x2', width)
        .attr('y2', height / 2)
        .attr('stroke-width', 1)
        .attr('stroke', 'black')
        .attr("stroke-dasharray", ("3, 3"))

    // add a vertical midline
    svg.append('line')
        .attr('x1', width / 2)
        .attr('y1', 0)
        .attr('x2', width / 2)
        .attr('y2', height)
        .attr('stroke-width', 1)
        .attr('stroke', 'black')
        .attr("stroke-dasharray", ("3, 3"))

    // add an inner ellipsis
    svg.append("ellipse")
        .attr("cx", width / 2)
        .attr("cy", height / 2)
        .attr("rx", 0.8 * width / 2)
        .attr("ry", 0.8 * height / 2)
        .attr("fill", "none")
        .attr('stroke-width', 1)
        .attr("stroke", "black")
        .attr("stroke-dasharray", ("3, 3"))

    d3.json("static/json/eeg_electrodes.json").then(function (electrodes) {
        var elem = svg
            .selectAll("g")
            .data(electrodes)

        /* Generate the nodes */
        var elemEnter = elem.enter()
            .append("g")
            .classed("node-group", true)
            .each(function (d) {
                const electrodeName = d.name.toLowerCase()
                this.classList.add(electrodeName)
                this.classList.add(d.types.map(i => 'eeg-' + i).join(" "))
            })
            .attr("data-electrode", d => d.name.toLowerCase())
            .attr("transform", function (d) {
                return "translate(" + d.location.x * width + "," + d.location.y * height + ")"
            })
            .on("click",
                function () {
                    selected = d3.select(this).classed("selected")
                    d3.select(this).classed("selected", !selected)
                    if (selected) {
                        this.classList.forEach(function (e) {
                            d3.select("#" + e).property("checked", false)
                        })
                    }

                    d3.select(this).classed("hovering", false)
                })
            .on("mouseover",
                function () {
                    d3.select(this).classed("hovering", true)
                })
            .on("mouseout",
                function () {
                    d3.select(this).classed("hovering", false)
                });

        /* Generate the circles for the nodes */
        elemEnter.append("circle")
            .attr("r", electrode_size)
            .attr("stroke", "black")
            .attr("fill", "yellow")

        /* Generate the text in the nodes */
        elemEnter.append("text")
            .text(function (d) {
                return d.name
            })
            .attr("text-anchor", "middle")
            .attr("font-size", electrode_size / ((electrode_size * 10) / 100))
            .attr("dy", electrode_size / ((electrode_size * 25) / 100))
    }).catch(function (error) {
        console.log(error)
    });

    // CHECKBOXES
    // keep track of the current selection (for hovering behavior)
    var current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")

    d3.selectAll("#eeg-selection-checkboxes input").on("change", function (d) {

        // available electrode types
        const available_values = ["visual", "motor", "sensory"]

        const isChecked = d3.select(this).property("checked")
        const boxValue = d3.select(this).property("value")

        d3.selectAll("#eeg-selection-container .node-group.eeg-" + boxValue).classed("selected", !isChecked)

        // update current selection
        current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })

    d3.selectAll(".eeg-input-container").on("mouseover", function () {
        current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
        const isChecked = d3.select(this).select("input").property("checked")
        const boxValue = d3.select(this).select("input").property("value")

        d3.selectAll("#eeg-selection-container .node-group." + boxValue).classed("selected", !isChecked)
    }).on("mouseout", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        current_selection.classed("selected", true)
    })

    d3.select(".eeg-all-btn").on("click", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", true)
        d3.selectAll("#eeg-selection-checkboxes input").property("checked", true)

        current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })
    d3.select(".eeg-reset-btn").on("click", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        d3.selectAll("#eeg-selection-checkboxes input").property("checked", false)

        current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })
}