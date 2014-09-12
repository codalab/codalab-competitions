/** @jsx React.DOM */

var RecordBundle = React.createClass({
    mixins: [TableMixin],
    render: function() {
        var header = this.state.interpreted[0];
        var focusIndex = this.state.rowFocusIndex;
        var k = header[0];
        var v = header[1];
        var items = this.state.interpreted[1].map(function(item, index){
            var focused = index === focusIndex;
            return(
                <tr key={index} focused={focused} className={focused ? 'focused' : ''}>
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
            <table className="table table-record">
                <tbody>
                    {items}
                </tbody>
            </table>
        );
    } // end of render function
}); //end of  RecordBundle
