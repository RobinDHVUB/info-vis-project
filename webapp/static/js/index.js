

draw_head();

function draw_head()
{
    const ear_size = 25
    const nose_height = 40
    const electrode_size = 15
    const width = 512, height = 512;
    const margin = {top: 25+nose_height, right: 25+ear_size, bottom: 25, left: 25+ear_size};


    const svg = d3.select(".container")
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
      .innerRadius( 0 )
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
        .innerRadius( 0 )
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
        .attr("transform", function(d) {
            console.log(d.location.y)
          return "translate(" + d.location.x*width + ","+d.location.y*height+")"
        })
        .on("click", 
        function(){
            var temp = d3.select(this).select("circle.clicked")
            if (temp.empty()) {
                d3.select(this).select("circle:not(.clicked)").classed("clicked", true).attr("fill", "blue")
            }
            else {
                d3.select(this).select("circle.clicked").classed("clicked", false).attr("fill", "yellow")
            }
        })
        .on("mouseover", 
        function(){
            d3.select(this).select("circle").attr("fill", "blue")
        })
        .on("mouseout",
        function(){
            d3.select(this).select("circle:not(.clicked)").attr("fill", "yellow")
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
              
function drawExample(shape) {
    if (shape == 'circle') {
        var squareSelection = d3.select("svg.border");

        var circleSelection = squareSelection.selectAll('circle')

        if (circleSelection.empty()) {
            squareSelection.append("circle")
            .attr("cx", 25)
            .attr("cy", 25)
            .attr("r", 25)
            .style("fill", "purple");
        }
        else {
            var xcoo = circleSelection.filter(function(d, i, list) {
                console.log(d)
                console.log(i)
                console.log(list)
                return i === list.length - 1;
            }).attr('cx');

            squareSelection.append("circle")
            .attr("cx", (2*25 + parseInt(xcoo)))
            .attr("cy", 25)
            .attr("r", 25)
            .style("fill", "yellow");
        }
    }
}