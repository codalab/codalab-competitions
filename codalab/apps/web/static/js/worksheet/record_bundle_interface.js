/** @jsx React.DOM */

var RecordBundle = React.createClass({
    mixins: [TableMixin],
    render: function() {
        var className = 'table table-record' + (this.props.focused ? ' focused' : '');
        var header = this.state.interpreted[0];
        // var focusIndex = this.state.rowFocusIndex;
        var k = header[0];
        var v = header[1];
        var items = this.state.interpreted[1].map(function(item, index){
            // var focused = index === focusIndex;
            return(
                <tr key={index}>
                    <th>
                        {item[k]}
                    </th>
                    <td>
                        {item[v]}
                    </td>
                </tr>
            )
        });
        return (
            <table className={className}>
                <tbody>
                    {items}
                </tbody>
            </table>
        );
    } // end of render function
}); //end of  RecordBundle
