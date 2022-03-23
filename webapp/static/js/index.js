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