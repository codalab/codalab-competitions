/** @jsx React.DOM */

var TableBundle = React.createClass({
    mixins: [TableMixin, CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    deleteCheckedRows: function(){
        var reactRows = this.refs; // react components
        var interpreted_row_indexes = []; // what indexes of the data do we want gone

        //lets find all rows that are checked
        for(var k in reactRows){
            if(reactRows[k].state.checked){
                //get the raw bundle info, since they are in the same order we can take the same index
                interpreted_row_indexes.push(reactRows[k].props.key);
            }
        }
        //delete and get our new interpreted. raw is handeled by ws_obj
        new_interpreted_rows = ws_obj.deleteTableRow(this.state, interpreted_row_indexes);
        //uncheck so we don't get any weird checked state hanging around
        this.unCheckRows();
        // go through and uncheck all the rows to get rid of lingering states
        this.setState({
            interpreted: new_interpreted_rows,
            rowFocusIndex: Math.max(this.state.rowFocusIndex - 1, 0)
        });
        // TODO: REMOVE _OWNER
        this._owner.saveAndUpdateWorksheet();
    },
    saveEditedItem: function(index, interpreted){
        this.props.handleSave(index, interpreted);
    },
    unCheckRows: function(){
        var reactRows = this.refs;
        for(var k in reactRows){
            reactRows[k].setState({checked:false});
        }
    },
    toggleCheckRows: function(){
        var reactRows = this.refs;
        for(var k in reactRows){
            reactRows[k].setState({checked:!this.state.checked});
        }
    },
    render: function() {
        var item = this.props.item.state;
        var canEdit = this.props.canEdit;
        var checkbox = canEdit ? <th width="20"><input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} /></th> : null;
        var className = 'table table-responsive' + (this.props.focused ? ' focused' : '');
        var bundle_info = item.bundle_info;
        var header_items = item.interpreted[0];
        var header_html = header_items.map(function(item, index) {
                return <th key={index}> {item} </th>;
            });
        var focusIndex = this.state.rowFocusIndex;
        var row_items = item.interpreted[1];
        var body_rows_html = row_items.map(function(row_item, index) {
            var row_ref = 'row' + index;
            var focused = index === focusIndex;
            var bundle_url = '/bundles/' + bundle_info[index].uuid;
            return <TableRow ref={row_ref} item={row_item} key={index} focused={focused} bundleURL={bundle_url} headerItems={header_items} canEdit={canEdit} />
        });
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <table className={className} onKeyDown={this.handleKeyboardShortcuts}>
                    <thead>
                        <tr>
                            {checkbox}
                            {header_html}
                        </tr>
                    </thead>
                    <tbody>
                        {body_rows_html}
                    </tbody>
                </table>
            </div>
        );
    } // end of render function
}); //end of  InlineBundle

var TableRow = React.createClass({
    getInitialState: function(){
        return {
            checked: false
        }
    },
    toggleChecked: function(){
        this.setState({checked: !this.state.checked});
    },
    render: function(){
        var focusedClass = this.props.focused ? 'focused' : '';
        var row_item = this.props.item;
        var header_items = this.props.headerItems;
        var bundle_url = this.props.bundleURL;
        var checkbox = this.props.canEdit ? <td className="checkbox"><input type="checkbox" onChange={this.toggleChecked} checked={this.state.checked} /></td> : null;
        var row_cells = this.props.headerItems.map(function(header_key, index){
            if(index == 0){
                return (
                    <td key={index}>
                        <a href={bundle_url} className="bundle-link">
                            {row_item[header_key]}
                        </a>
                    </td>
                )
            } else {
                return <td key={index}> {row_item[header_key]}</td>
            }
        });
        return (
            <tr className={focusedClass}>
                {checkbox}
                {row_cells}
            </tr>
        );

    }
})
