/** @jsx React.DOM */

var TableMixin = { 
    // This handles some common elements of worksheet items that are presented as tables
    // TableBundle and RecordBundle
    getInitialState: function(){
        return {
            rowFocusIndex: 0
        }
    },
    handleKeyboardShortcuts: function(event){
        var item = this.props.item.state;
        var key = keyMap[event.keyCode];
        var index = this.state.rowFocusIndex;
        var rowsInTable = item.interpreted[1].length;
        var parentFocusIndex = this._owner.state.focusIndex;
        if(typeof key !== 'undefined'){
            event.preventDefault();
            switch (key) {
                case 'up':
                case 'k':
                    event.preventDefault();
                    index = Math.max(this.state.rowFocusIndex - 1, 0);
                    if(this.state.rowFocusIndex == 0){
                        this._owner.setState({focusIndex: parentFocusIndex - 1});
                    }else {
                        this.setState({rowFocusIndex: index});
                    }
                    break;
                case 'down':
                case 'j':
                    event.preventDefault();
                    index = Math.min(this.state.rowFocusIndex + 1, rowsInTable);
                    if(index == rowsInTable){
                        this._owner.setState({focusIndex: parentFocusIndex + 1});
                    }else {
                        this.setState({rowFocusIndex: index});
                    }
                    break;
                case 'd':
                    if(event.ctrlKey || event.metaKey){
                        this._owner._owner.deleteItem(ws_interactions.state.worksheetFocusIndex)
                    }else {
                        this.deleteRow(this.state.rowFocusIndex);
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
    deleteRow: function(index){
        var newItems = this.state.interpreted[1];
        if(index == newItems.length - 1){
            if(newItems.length == 1){
                // delete the whole table by calling its grandparent
                this._owner._owner.deleteItem(ws_interactions.state.worksheetFocusIndex);
            }else{
                // it's the last row, so change the focus to the new last row
                this.setState({rowFocusIndex:index-1});
            }
        }
        newItems.splice(index, 1);
        this.setState({interpreted:[
            this.state.interpreted[0],
            newItems
        ]});
    }
}