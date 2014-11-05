/** @jsx React.DOM */

var RecordBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        return {
            checked: false
        }
    },
    handleClick: function(){
        this.props.setFocus(this.props.key);
    },
    render: function() {
        var item = this.props.item.state;
        var className = 'table table-record' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} disabled={!this.props.checkboxEnabled}/> : null;
        var header = item.interpreted[0];
        var k = header[0];
        var v = header[1];
        var focusIndex = item.rowFocusIndex;
        var items = item.interpreted[1].map(function(item, index){
            var ref = 'row' + index;
            var focused = index === focusIndex;
            var focusedClass = focused ? 'focused' : '';
            return(
                <tr ref={ref} key={index} focused={focused} className={focusedClass}>
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
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <table className={className}>
                    <tbody>
                        {items}
                    </tbody>
                </table>
            </div>
        );
    } // end of render function
}); //end of  RecordBundle
