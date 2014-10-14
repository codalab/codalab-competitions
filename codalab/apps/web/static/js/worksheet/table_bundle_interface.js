/** @jsx React.DOM */

var TableBundle = React.createClass({
    mixins: [TableMixin, CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    deleteCheckedRows: function(){
        console.log('delete checked rows');
        // TODO MOVE LOGIC  TO CONTENT
        // // do basically the same thing we do in worksheet_content's insertItem and cleanUp methods
        var rows = this.state.interpreted; // data
        var reactRows = this.refs; // react components
        var removed_bundles = new Array();
        // if the row is checked, set its data to null
        for(var k in reactRows){
            if(reactRows[k].state.checked){
                //get the raw bundle info, since they are in the same order we can take the same index
                removed_bundles.push(this.state.bundle_info[reactRows[k].props.key]);
                rows[1][reactRows[k].props.key] = null;
            }
        }
        var newRows = new Array();
        // clean up the data by copying all non-null rows into a new array
        for(var i = 0; i < rows[1].length; i++){
            if (rows[1][i]){
                newRows.push(rows[1][i]);
            }
        }
        // then set the raw data to that new array
        rows[1] = newRows;
        // //set the new state for the IU
        this.setState({
            interpreted: rows,
            rowFocusIndex: Math.max(this.state.rowFocusIndex - 1, 0)
        });

        //lets update the raw and save
        var r_index = this.state.raw_index; //shortcut naming
        var r_size = this.state.raw_size;
        for(var b_index in removed_bundles){
            //look though our chunk of the raw for this
            for(var i = r_index; i< r_index+r_size; i++){
                if(ws_obj.state.raw[i].search(removed_bundles[b_index].uuid) > -1){
                    console.log("removing line");
                    console.log(ws_obj.state.raw[i]);
                    ws_obj.state.raw[i] = 'undefined';
                }
            }
        }
        ws_obj.cleanUp();


        // this.saveEditedItem(this.props.key, newRows);
        // go through and uncheck all the rows to get rid of lingering states
        this.unCheckRows();
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
