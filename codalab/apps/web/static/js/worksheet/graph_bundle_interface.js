/** @jsx React.DOM */

// Display a graph over the different bundles.
var GraphBundle = React.createClass({
    mixins: [CheckboxMixin, GoToBundleMixin],
    getInitialState: function() {
        return {};
    },
    handleClick: function(event) {
        this.props.setFocus(this.props.focusIndex, 0);
    },
    render: function() {
        var className = 'type-image' + (this.props.focused ? ' focused' : '');
        var item = this.props.item;
        console.log('GraphBundle.render', this.props.focusIndex);

        // Index in the table to find x and y
        var xi = parseInt(item.properties.x) || 0;
        var yi = parseInt(item.properties.y) || 1;

        // Axis labels
        var xlabel = item.properties.xlabel || x;
        var ylabel = item.properties.ylabel || y;

        // Create a bunch of C3 'columns', each of which is a label followed by a sequence of numbers.
        // For example: ['accuracy', 3, 5, 7].
        // Each trajectory is a bundle that we wish to plot and contributes two
        // columns, one for x and y.
        var ytox = {};  // Maps the names of the y columns to x columns
        var columns = [];
        for (var i = 0; i < item.interpreted.length; i++) {  // For each trajectory
          var info = item.interpreted[i];
          var points = info.points;
          var display_name = i + ': ' + info.display_name;
          var xcol = [display_name + '_x'];
          var ycol = [display_name];
          ytox[ycol[0]] = xcol[0];
          for (var j = 0; j < points.length; j++) {  // For each point in that trajectory
            var pt = points[j];
            var x = pt[xi];
            var y = pt[yi];
            xcol.push(x);
            ycol.push(y);
          }
          columns.push(xcol);
          columns.push(ycol);
        }

        // Create the chart
        var chartId = 'chart-' + this.props.focusIndex;
        var chart = c3.generate({
          bindto: '#' + chartId,
          data: {
            xs: ytox,
            columns: columns,
          },
          axis: {
            x: {label: {text: xlabel, position: 'outer-middle'}},
            y: {label: {text: ylabel, position: 'outer-middle'}},
          },
        });

        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className}>
                    <div id={chartId} />
                </div>
            </div>
        );
    }
});
