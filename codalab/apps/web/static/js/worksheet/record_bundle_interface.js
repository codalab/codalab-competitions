/** @jsx React.DOM */

var RecordBundle = React.createClass({
    mixins: [TableMixin, CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    render: function() {
        var item = this.props.item.state;
        var className = 'table table-record' + (this.props.focused ? ' focused' : '');
        var header = item.interpreted[0];
        var k = header[0];
        var v = header[1];
        var focusIndex = this.state.rowFocusIndex;
        var items = item.interpreted[1].map(function(item, index){
            var focused = index === focusIndex;
            var focusedClass = focused ? 'focused' : '';
            return(
                <tr key={index} focused={focused} className={focusedClass}>
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
            <div className="ws-item">
                <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                <table className={className}>
                    <tbody>
                        {items}
                    </tbody>
                </table>
            </div>
        );
    } // end of render function
}); //end of  RecordBundle
