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
        var sliderBot = $('#ageSlider').data("from")
        var sliderTop = $('#ageSlider').data("to")
        var chosenSex = d3.select("#subject-sex input:checked").attr("value")

        // Filter the given data based on the filter values
        newdata = Array.from(newdata).filter(function(d) {
            return d.age >= sliderBot && d.age <= sliderTop
                && (d.sex === chosenSex || chosenSex === 'all')
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
                return "Subject " + d.id + ": " + sex + ", " + d.age
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
    function visualizeEEG(eegNames, eegColors, eegSelection, eegCoords, meshCoords, keepCamera) {
        visualize3D("eeg", eegNames, eegColors, eegSelection, eegCoords, meshCoords, keepCamera)
    }

    /* Function for visualizing MEG electrode cap in 3D, based on the current subject that is selected */
    function visualizeMEG(megNames, megColors, megSelection, megCoords, meshCoords, keepCamera) {
        visualize3D("meg", megNames, megColors, megSelection, megCoords, meshCoords, keepCamera)
    }

    /*
    Function for visualizing EEG or MEG electrode cap in 3D, based on the current subject that is selected.
    - keepCamera is a parameter specifying whether the virtual camera position should be reset when updating the visualization.
    - plotType is expected to be 'eeg' or 'meg'
    */
    function visualize3D(plotType, elNames, elColors, elSelection, elCoords, meshCoords, keepCamera)
    {
        // get the div to show the 3D plot in
        var graphDiv = document.getElementById(plotType + "Plot")

        // get the coordinates of all electrodes
        var elX = elCoords[0]
        var elY = elCoords[1]
        var elZ = elCoords[2]

        // get the coordinates for the mesh beneath the electrodes (mesh is added for having a clearer view)
        var meshX = meshCoords[0]
        var meshY = meshCoords[1]
        var meshZ = meshCoords[2]

        // split up the data in sets for selected electrodes and non-selected electrodes to easily visualize them differently
        var elSelectedX = []
        var elSelectedY = []
        var elSelectedZ = []
        var elSelectedNames = []
        var elSelectedColors = []

        var elNonselectedX = []
        var elNonselectedY = []
        var elNonselectedZ = []
        var elNonselectedNames = []
        var elNonselectedColors = []

        var elSelected = []
        for (var i = 0; i < elSelection.length; i++) {
            if (elSelection[i]) {
                elSelectedX.push(elX[i])
                elSelectedY.push(elY[i])
                elSelectedZ.push(elZ[i])
                elSelectedNames.push(elNames[i])
                elSelectedColors.push(elColors[i])
            }
            else {
                elNonselectedX.push(elX[i])
                elNonselectedY.push(elY[i])
                elNonselectedZ.push(elZ[i])
                elNonselectedNames.push(elNames[i])
                elNonselectedColors.push(elColors[i])
            }
        }

        // trace for the non-selected electrodes
        var traceNon = {
            x: elNonselectedX,
            y: elNonselectedY,
            z: elNonselectedZ,
            mode: 'markers',
            hovertemplate: '%{text}<extra></extra>',
            text: elNonselectedNames,
            marker: {
                symbol: 'circle',
                size: 12,
                color: elNonselectedColors,
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
            x: elSelectedX,
            y: elSelectedY,
            z: elSelectedZ,
            mode: 'markers',
            hovertemplate: '%{text}<extra></extra>',
            text: elSelectedNames,
            marker: {
                symbol: 'circle',
                size: 14,
                color: elSelectedColors,
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
                color: '#C0C0C0',
                type: 'mesh3d',
                x: meshX,
                y: meshY,
                z: meshZ,
        }

        // add missing Mesh connections for a prettier mesh
        var missingMeshIdx = undefined
        if (plotType == 'meg') {
            missingMeshIdx = missingMEGMeshIdx(elNames)
        }
        else {
            missingMeshIdx = missingEEGMeshIdx(elNames)
        }

        missingMesh = {
            hoverinfo:'skip',
            opacity:1,
            color: '#C0C0C0',
            type: 'mesh3d',
            x: meshX,
            y: meshY,
            z: meshZ,
            i: missingMeshIdx["i"],
            j: missingMeshIdx["j"],
            k: missingMeshIdx["k"]
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
        var data = [traceNon, traceSel, traceMesh, missingMesh];
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
        graphDiv.removeAllListeners('plotly_relayout')
        graphDiv.on('plotly_relayout', function(data) {
            return updateCameraScene(plotType, data)
        });
    }

    // read in the subject data from the JSON file and initialize everything based on this data
    d3.json("/static/subject-data/subject_data.json").then(function(data)
    {
        // names
        eegNames = data["eeg_names"]
        megNames = data["meg_names"]

        // types
        eegTypes = data["eeg_types"]
        megTypes = data["meg_types"]

        // coordinates (MEG coordinates are fixed, EEG coordinates are stored per subject)
        megCoords = data["meg_coords"]
        megMeshCoords = data["meg_mesh_coords"]

        // specify the color for each type of cortex
        eegColors = []
        for (var i = 0; i < eegTypes.length; i++) {
            if (eegTypes[i].toLowerCase() === "frontal lobe") {
                eegColors[i] = "red"
            }
            else if (eegTypes[i].toLowerCase() === "parietal lobe") {
                eegColors[i] = "blue"
            }
            else if (eegTypes[i].toLowerCase() === "occipital lobe") {
                eegColors[i] = "orange"
            }
            else if (eegTypes[i].toLowerCase() === "temporal lobe (l)") {
                eegColors[i] = "yellow"
            }
            else if (eegTypes[i].toLowerCase() === "temporal lobe (r)"){
                eegColors[i] = "black"
            }
            else
            {
                console.log("invalid type: " +  eegTypes[i])
            }
        }

        megColors = []
        for (var i = 0; i < megTypes.length; i++) {
            if (megTypes[i].toLowerCase() === "frontal lobe") {
                megColors[i] = "red"
            }
            else if (megTypes[i].toLowerCase() === "parietal lobe") {
                megColors[i] = "blue"
            }
            else if (megTypes[i].toLowerCase() === "occipital lobe") {
                megColors[i] = "orange"
            }
            else if (megTypes[i].toLowerCase() === "temporal lobe (l)") {
                megColors[i] = "yellow"
            }
            else if (megTypes[i].toLowerCase() === "temporal lobe (r)"){
                megColors[i] = "black"
            }
            else
            {
                console.log("invalid type: " + megTypes[i])
            }
        }

        // keep track of which electrodes have been selected (initially none are selected)
        eegSelection = Array(eegTypes.length).fill().map(_ => false)
        megSelection = Array(megTypes.length).fill().map(_ => false)

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

          for (var i = 0; i < eegTypes.length; i++) {
            if (eegTypes[i].toLowerCase() === boxValue.toLowerCase()) {
              eegSelection[i] = isChecked
            }
          }

          visualizeEEG(eegNames, eegColors, eegSelection, selectedSubject.eeg_coords, selectedSubject.mesh_coords, true)
          checkAnalysis(selectedSubject)
        })

        // update which MEG electrodes have been selected after checking one of the electrode checkboxes
        d3.selectAll("#meg-checkbox-container input").on("change", function(d) {
          const isChecked = d3.select(this).property("checked")
          const boxValue = d3.select(this).property("value")

          for (var i = 0; i < megTypes.length; i++) {
            if (megTypes[i].toLowerCase() === boxValue.toLowerCase()) {
              megSelection[i] = isChecked
            }
          }

          visualizeMEG(megNames, megColors, megSelection, megCoords, megMeshCoords, true)
          checkAnalysis(selectedSubject)
        })

        /* Function to handle changing the selected subject */
        function handleSubjectChange() {
            var selectedOption = d3.selectAll("#subject-selection option:checked");

            // we reset the camera view to its default valueon subject change
            updateCameraScene("eeg", undefined)
            updateCameraScene("meg", undefined)

            // if no subject is selected we purge the 3D plots and disable selecting cortex checkboxes
            if (selectedOption.empty()){
                selectedSubject = undefined
                Plotly.purge(document.getElementById('eegPlot'))
                Plotly.purge(document.getElementById('megPlot'))
                d3.selectAll('#eeg-checkbox-container label').classed("disabled", true)
                d3.selectAll('#meg-checkbox-container label').classed("disabled", true)
            }
            else {
                // if a subject is selected we update the 3D plots and enable selecting cortex checkboxes
                var newData = selectedOption.data();
                if ((typeof selectedSubject === 'undefined') || (selectedSubject["id"] !== newData[0]["id"])) {
                    selectedSubject = newData[0]
                    d3.selectAll('#eeg-checkbox-container label').classed("disabled", false)
                    d3.selectAll('#meg-checkbox-container label').classed("disabled", false)

                    visualizeEEG(eegNames, eegColors, eegSelection, selectedSubject.eeg_coords,
                        selectedSubject.mesh_coords, false)
                    visualizeMEG(megNames, megColors, megSelection, megCoords, megMeshCoords, false)
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
Helper function to create a prettier mesh for the 3D MEG cap visualization.
We initially created a more dynamic computation of which additional triangles should be drawn,
but this seemed to be too variable and would take a lot of time.
Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
*/
function missingMEGMeshIdx(megNames) {

    // list of MEG signals that should be connected
    var megsToConnect = ["MEG1211", "MEG1221", "MEG1321", "MEG1331", "MEG2421",
        "MEG2431", "MEG1411", "MEG1441", "MEG2611", "MEG2641",
        "MEG2521", "MEG1731", "MEG1931", "MEG2121", "MEG2331",
        "MEG2511", "MEG1421", "MEG1431", "MEG2621", "MEG2631",
        "MEG2531", "MEG2541", "MEG2131", "MEG2141", "MEG1741",
        "MEG1711"]

    // list of indices of the MEG signals in the original list of MEG names/coordinates
    var indices = []
    for (var i = 0; i < megsToConnect.length; i++) {
        indices.push(megNames.indexOf(megsToConnect[i], 0))
    }

    // original coordinate indices that should be connected
    var i = [indices[0], indices[6], indices[2], indices[17], indices[18], indices[5],
        indices[20], indices[21], indices[22], indices[24]]
    var j = [indices[1], indices[7], indices[16], indices[18], indices[19], indices[19],
        indices[21], indices[22], indices[13], indices[25]]
    var k = [indices[6], indices[2], indices[17], indices[3], indices[4], indices[20],
        indices[15], indices[14], indices[23], indices[11]]

    return {"i": i, "j": j, "k": k}
}

/*
Helper function to create a prettier mesh for the 3D EEG cap visualization.
We initially created a more dynamic computation of which additional triangles should be drawn,
but this seemed to be too variable and would take a lot of time.
Since it's not the prime focus of this project, we therefore chose to hardcode missing electrode mesh connections.
*/
function missingEEGMeshIdx(eegNames) {

    // list of EEG signals that should be connected
    var eegsToConnect = ["EEG007", "EEG008", "EEG002", "EEG005", "EEG004",
        "EEG038", "EEG039", "EEG050", "EEG003", "EEG074",
        "EEG069", "EEG029", "EEG030", "EEG041", "EEG040",
        "EEG052", "EEG051", "EEG001", "EEG070", "EEG018",
        "EEG060", "EEG049", "EEG028", "EEG027", "EEG017",
        "EEG026", "EEG016", "EEG009", "EEG010", "EEG059",
        "EEG071", "EEG072", "EEG073", "EEG015", "EEG011"
    ]

    // list of indices of the MEG signals in the original list of MEG names/coordinates
    var indices = []
    for (var i = 0; i < eegsToConnect.length; i++) {
        indices.push(eegNames.indexOf(eegsToConnect[i], 0))
    }

    // original coordinate indices that should be connected
    var i = [indices[0], indices[3], indices[5], indices[8], indices[11], indices[11], indices[15],
    indices[17], indices[11], indices[7], indices[5], indices[17], indices[10], indices[20], indices[6],
    indices[24], indices[24], indices[4], indices[5], indices[15], indices[18],
    indices[29], indices[30], indices[31], indices[32], indices[9], indices[30], indices[17], indices[8],
    indices[8], indices[33], indices[2]]

    var j = [indices[1], indices[4], indices[6], indices[9], indices[12], indices[14], indices[14],
    indices[18], indices[12], indices[20], indices[7], indices[16], indices[20], indices[7], indices[22],
    indices[23], indices[26], indices[27], indices[6], indices[16], indices[17],
    indices[20], indices[18], indices[18], indices[31], indices[32], indices[8], indices[8], indices[18],
    indices[31], indices [2], indices[34]]

    var k = [indices[2], indices[2], indices[7], indices[10], indices[13], indices[13], indices[16],
    indices[16], indices[19], indices[10], indices[21], indices[15], indices[9], indices[21], indices[23],
    indices[25], indices[1], indices[28], indices[23], indices[18], indices[16],
    indices[9], indices[17], indices[17], indices[17], indices[8], indices[9], indices[18], indices[9],
    indices[9], indices[1], indices[4]]

    return {"i": i, "j": j, "k": k}
}

/*
Function to create a String summary of the most important subject information
*/
function createSubjectInfo(subjectData) {
    var sex = subjectData.sex === 'm' ? 'male' : 'female'

    return "Subject " + subjectData.id + ": " + sex + ", " + subjectData.age + " years old"
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
    var subjectIds = []
    d3.selectAll("#subject-selection option:checked").data().forEach(function(d) {
        subject = d;
        subjectIds.push(d.id);
    });

    // get the selected EEG channels
    var eegChannels = []
    var eegChannelTypes = []
    for (var i = 0; i < eegSelection.length; i++) {
        if (eegSelection[i]) {
            eegChannels.push(eegNames[i])
            eegChannelTypes.push(eegTypes[i])
        }
    }

    // get the selected MEG channels
    var megChannels = []
    var megChannelTypes = []
    for (var i = 0; i < megSelection.length; i++) {
        if (megSelection[i]) {
          megChannels.push(megNames[i])
          megChannelTypes.push(megTypes[i])
        }
    }

    const sel = JSON.stringify({
        "subject": subjectIds[0],
        "eeg": groupPerType(eegChannelTypes, eegChannels),
        "meg": groupPerType(megChannelTypes, megChannels)
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
        url: "/data-analysis",
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
            console.log(xhr.status);
            console.log(thrownError);
        }
    });
}

/* UNUSED FUNCTIONS */

/*
This function generates a standard 2D view of EEG electrodes using D3.
However, it is currently unused since 3D visualization was eventually deemed more informative and especially more correct.
*/
function drawEEGElectrodeSelector() {
    // general sizing info of figure
    const earSize = 25
    const noseHeight = 40
    const electrodeSize = 15
    const width = 450, height = 450;
    const margin = {top: 25 + noseHeight, right: 25 + earSize, bottom: 25, left: 25 + earSize};


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
            .innerRadius(earSize)
            .outerRadius(earSize)
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
            .innerRadius(earSize)
            .outerRadius(earSize)
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

    var lineData = [{"x": width / 2 - earSize, "y": 1}, {
        "x": width / 2,
        "y": -noseHeight
    }, {"x": width / 2 + earSize, "y": 1}];

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
            .attr("r", electrodeSize)
            .attr("stroke", "black")
            .attr("fill", "yellow")

        /* Generate the text in the nodes */
        elemEnter.append("text")
            .text(function (d) {
                return d.name
            })
            .attr("text-anchor", "middle")
            .attr("font-size", electrodeSize / ((electrodeSize * 10) / 100))
            .attr("dy", electrodeSize / ((electrodeSize * 25) / 100))
    }).catch(function (error) {
        console.log(error)
    });

    // CHECKBOXES
    // keep track of the current selection (for hovering behavior)
    var currentSelection = d3.selectAll("#eeg-selection-container .node-group.selected")

    d3.selectAll("#eeg-selection-checkboxes input").on("change", function (d) {

        // available electrode types
        const availableValues = ["visual", "motor", "sensory"]

        const isChecked = d3.select(this).property("checked")
        const boxValue = d3.select(this).property("value")

        d3.selectAll("#eeg-selection-container .node-group.eeg-" + boxValue).classed("selected", !isChecked)

        // update current selection
        currentSelection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })

    d3.selectAll(".eeg-input-container").on("mouseover", function () {
        currentSelection = d3.selectAll("#eeg-selection-container .node-group.selected")
        const isChecked = d3.select(this).select("input").property("checked")
        const boxValue = d3.select(this).select("input").property("value")

        d3.selectAll("#eeg-selection-container .node-group." + boxValue).classed("selected", !isChecked)
    }).on("mouseout", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        currentSelection.classed("selected", true)
    })

    d3.select(".eeg-all-btn").on("click", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", true)
        d3.selectAll("#eeg-selection-checkboxes input").property("checked", true)

        currentSelection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })
    d3.select(".eeg-reset-btn").on("click", function () {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        d3.selectAll("#eeg-selection-checkboxes input").property("checked", false)

        currentSelection = d3.selectAll("#eeg-selection-container .node-group.selected")
    })
}