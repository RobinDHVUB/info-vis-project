drawEEGElectrodeSelector();

// TODO: should we just make the whole component in JS, also the input checkboxes?
d3.selectAll("#eeg-selection-checkboxes input").on("change", function(d){

    const available_values = ["visual", "motor", "sensory"]

    const isChecked = d3.select(this).property("checked")
    const boxValue = d3.select(this).property("value")

    checked = []
    var boxes = d3.selectAll('#eeg-selection-checkboxes input[type="checkbox"]:checked')
    boxes.each(function() {
        checked.push(this.value)
    });

    if (checked.includes('eeg-all')) {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", true)
    }
    else {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        available_values.forEach(function(val){
            if (checked.includes('eeg-'+val)) {
                d3.selectAll("#eeg-selection-container .eeg-"+val).classed("selected", true)
            }
        })
    }

    manual_selection.forEach(function(val) {
        val.classed("selected", true)
    })
    current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
})

var manual_selection = []
var current_selection = []
d3.selectAll(".eeg-input-container").on("mouseover", function(){
    const isChecked = d3.select(this).select("input").property("checked")
    current_selection = d3.selectAll("#eeg-selection-container .node-group.selected")
    const boxValue = d3.select(this).select("input").property("value")
    if (boxValue == 'eeg-all') {
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", !isChecked)
    } 
    else {
        d3.selectAll("#eeg-selection-container .node-group." + boxValue).classed("selected", !isChecked)
    }
    if (isChecked) {
        manual_selection.forEach(function(val) {
            val.classed("selected", true)
        })
    }
}).on("mouseout", function(){
        d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
        current_selection.classed("selected", true)
})

d3.select(".eeg-reset-btn").on("click", function(){
    d3.selectAll("#eeg-selection-container .node-group").classed("selected", false)
    d3.selectAll("#eeg-selection-checkboxes input").property("checked", false)

    manual_selection = []
    current_selection = []
})

function drawEEGElectrodeSelector()
{
    const ear_size = 25
    const nose_height = 40
    const electrode_size = 15
    const width = 512, height = 512;
    const margin = {top: 25+nose_height, right: 25+ear_size, bottom: 25, left: 25+ear_size};


    const svg = d3.select("#eeg-selection-container")
                  .append("svg")
                  .attr("class","eeg_head")
                  .attr("width", width + margin.left + margin.right + 2*ear_size)
                  .attr("height", height + margin.top + margin.bottom)
                  .append("g")
                  .attr("transform", "translate(" + margin.left +","+ margin.top +")");


    // add an ellipsis for general head shape
    svg.append("ellipse")
    .attr("cx", width/2)
    .attr("cy", height/2)
    .attr("rx", width/2)
    .attr("ry", height/2)
    .attr('stroke-width', 2)
    .attr("stroke","black")
    .attr("fill", "none");

    // add the left ear
    svg.append("path")
    .attr("transform", "translate(0," + height/2 + ")")
    .attr("d", d3.arc()
      .innerRadius( ear_size )
      .outerRadius( ear_size )
      .startAngle( 3.14 )     // angle is in radian (pi = 3.14 = bottom).
      .endAngle( 6.28 )       // 2*pi = 6.28 = top
      )
    .attr('stroke', 'black')
    .attr("stroke-width", 2)
    .attr("fill", "none");

    // add the right ear
    svg.append("path")
    .attr("transform", "translate("+ width +"," + height/2 + ")")
    .attr("d", d3.arc()
        .innerRadius( ear_size )
        .outerRadius( ear_size )
        .startAngle( -3.14 ) 
        .endAngle( -6.28 )  
        )
    .attr('stroke', 'black')
    .attr("stroke-width", 2)
    .attr("fill", "none");

    // add the nose
    var bezierLine = d3.line()
        .x(function(d) { return d.x; })
        .y(function(d) { return d.y; })
        .curve(d3.curveBasis);

    var lineData = [ { "x": width/2-25,   "y": 1}, { "x": width/2,  "y": -40}, { "x": width/2+25,  "y": 1}];

    svg.append("path")
            .attr("d", bezierLine(lineData))
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .attr("fill", "none");

    // add a horizontal line
    svg.append('line')
    .attr('x1', 0)
    .attr('y1', height/2)
    .attr('x2', width)
    .attr('y2', height/2)
    .attr('stroke-width', 1)
    .attr('stroke', 'black')
    .attr("stroke-dasharray", ("3, 3"))

    // add a vertical line
    svg.append('line')
    .attr('x1', width/2)
    .attr('y1', 0)
    .attr('x2', width/2)
    .attr('y2', height)
    .attr('stroke-width', 1)
    .attr('stroke', 'black')
    .attr("stroke-dasharray", ("3, 3"))

    // add an inner ellipsis
    svg.append("ellipse")
    .attr("cx", width/2)
    .attr("cy", height/2)
    .attr("rx", 0.8*width/2)
    .attr("ry", 0.8*height/2)
    .attr("fill", "none")
    .attr('stroke-width', 1)
    .attr("stroke","black")
    .attr("stroke-dasharray", ("3, 3"))
    
    d3.json("static/json/eeg_electrodes.json").then(function(electrodes)
    {
        var elem = svg
        .selectAll("g")
        .data(electrodes)

        /*Create and place the "blocks" containing the circle and the text */
        var elemEnter = elem.enter()
        .append("g")
        .classed("node-group", true)
        .each(function(d) {
            const electrodeName = d.name.toLowerCase()
            this.classList.add(electrodeName)
            this.classList.add(d.types.map(i => 'eeg-' + i).join(" "))
        })
        .attr("data-electrode", d => d.name.toLowerCase())
        .attr("transform", function(d) {
          return "translate(" + d.location.x*width + ","+d.location.y*height+")"
        })
        .on("click", 
        function(){
            selected = d3.select(this).classed("selected")
            d3.select(this).classed("selected", !selected)
            if (!selected) {
                manual_selection.push(d3.select(this))
            }
            else {
                current_this = d3.select(this)
                manual_selection = manual_selection.filter(function(ele){ 
                    return ele.attr("data-electrode") != current_this.attr("data-electrode"); 
                });
            }

            d3.select(this).classed("hovering", false)
        })
        .on("mouseover", 
        function(){
            d3.select(this).classed("hovering", true)
        })
        .on("mouseout",
        function(){
            d3.select(this).classed("hovering", false)
        });

        /*Create the circle for each block */
        var circleInner = elemEnter.append("circle")
        .attr("r", electrode_size)
        .attr("stroke", "black")
        .attr("fill", "yellow")

        /* Create the text for each block */
        elemEnter.append("text")
        .text(function(d) {
            return d.name
        })
        .attr("text-anchor" , "middle")
        .attr("font-size", electrode_size / ((electrode_size * 10) / 100))
        .attr("dy", electrode_size / ((electrode_size * 25) / 100))
    }).catch(function(error)
    {
        console.log(error)
    });
}


function letsgo() 
{
    const values = []
    d3.selectAll('#eeg-selection-container .node-group.selected').each(function() {
        values.push(d3.select(this).attr("data-electrode"))
    });
    
    console.log(values)
}