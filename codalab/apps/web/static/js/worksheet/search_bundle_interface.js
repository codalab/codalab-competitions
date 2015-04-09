/** @jsx React.DOM */

var SearchBundleItem = React.createClass({
    render: function(){
        var item = this.props.item;
        var key = 'sbi_' + item.mode + '_' + this.props.index;
        //What is the type so we can set up stuff
        if(item.mode == "table"){
            var header_items = item.interpreted[0];
            var row_items = item.interpreted[1];
            //set up table head
            var header_html = header_items.map(function(item, index) {
                var key = "sbth_" + index;
                return <th key={key}> {item} </th>;
            });
            //set up table body
            var body_rows_html = row_items.map(function(row_item, index) {
                var key = 'sbtr_' + index;
                var row_cells = header_items.map(function(header_key, index){
                    var key = "sbtd_" + index;
                    return <td key={key}> {row_item[header_key]}</td>
                }); // end of row_cells = header_items.map
                return (<tr key={key}>{row_cells}</tr>);
            }); // end of body_rows_html = row_items.map
            //Mash it all together
            return (
                <table key={key} className="table">
                    <thead>
                        <tr>
                            {header_html}
                        </tr>
                    </thead>
                    <tbody>
                        {body_rows_html}
                    </tbody>
                </table>
            )
        }else{ // just a simple markdown type.
            return (
                <div key={key} className="result">
                    {item.interpreted}
                </div>
            )
        }
    }
})
var SearchBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    handleClick: function(event){
        this.props.setFocus(this.props.index, event);
    },
    render: function() {
        var className = 'type-search' + (this.props.focused ? ' focused' : '');
        var checkbox = null;
        if(this.props.canEdit){
            checkbox = (
                <input
                    type="checkbox"
                    className="ws-checkbox"
                    onChange={this.handleCheck}
                    checked={this.state.checked}
                    disabled={!this.props.checkboxEnabled}
                />
            )
        }
        var search_items = this.state.interpreted.items;
        var search_items_interpreted;
        var parentIndex = this.props.index;
        if(search_items.length){
            search_items_interpreted = search_items.map(function(item, index){
                // currently there will only be one item in the items array
                // but in the future there might be more so handle that with map.
                var key = 'sbi_' + parentIndex + '_' + index;
                return <SearchBundleItem
                        key={key}
                        index={index}
                        item={item}
                    />
            });
        }else {
            search_items_interpreted = <div className="result empty"><em>Nothing Found</em></div>
        }
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <div className={className}>
                    {search_items_interpreted}
                </div>
            </div>
        );
    } // end of render function
}); //end of  SearchBundle
