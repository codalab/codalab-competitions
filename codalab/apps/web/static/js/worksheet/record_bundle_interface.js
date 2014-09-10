/** @jsx React.DOM */

var RecordBundle = React.createClass({
    getInitialState: function(){
        var state = this.props.item.state;
        state.rowFocusIndex = 0;
        state.handleKeyboardShortcuts = this.handleKeyboardShortcuts;
        return state;
    },
    handleKeyboardShortcuts: function(event){
        var key = keyMap[event.keyCode];
        var index = this.state.rowFocusIndex;
        var rowsInTable = this.props.item.state.interpreted[1].length;
        if(typeof key !== 'undefined'){
            event.preventDefault();
            switch (key) {
                case 'up':
                case 'k':
                    event.preventDefault();
                    index = Math.max(this.state.rowFocusIndex - 1, 0);
                    if(this.state.rowFocusIndex === 0){
                        ws_interactions.state.worksheetFocusIndex--;
                        ws_broker.fire('updateState');
                    }else {
                        this.setState({rowFocusIndex: index});
                    }
                    break;
                case 'down':
                case 'j':
                    event.preventDefault();
                    index = Math.min(this.state.rowFocusIndex + 1, rowsInTable);
                    if(index == rowsInTable){
                        ws_interactions.state.worksheetFocusIndex++;
                        ws_broker.fire('updateState');
                    }else {

                        this.setState({rowFocusIndex: index});
                    }
                    break;
                default:
                    return true;
                }
            } else {
                return true;
            }
        event.stopPropagation();
    },
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
                {items}
            </table>
        );
    } // end of render function
}); //end of  RecordBundle
