/** @jsx React.DOM */

var SearchBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    handleClick: function(event){
        this.props.setFocus(this.props.index, event);
    },
    formatInterpreted: function(interpreted){
        var formatted = [] // formatted is an array becasue there might be more then one type of response.
        if(interpreted.items.length > 0){
            //What is the type so we can set up stuff
            if(interpreted.items[0].mode == "table"){
                // currently there will only be one item in the items array
                // but there might because in the future where there is more then 1 so handle that with forEach.
                interpreted.items.forEach(function(item, i){
                    var header_items = item.interpreted[0];
                    var row_items = item.interpreted[1];
                    //set up table head
                    var header_html = header_items.map(function(item, index) {
                        return <th key={index}> {item} </th>;
                    });
                    //set up table body
                    var body_rows_html = row_items.map(function(row_item, index) {
                        var row_cells = header_items.map(function(header_key, index){
                            return <td key={index}> {row_item[header_key]}</td>
                        }); // end of row_cells = header_items.map
                        return (<tr>{row_cells} </tr>);
                    }); // end of body_rows_html = row_items.map

                    //Mash it all together
                    formatted.push(
                        <table className="table">
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
                });// end of interpreted.items.forEach
            }else{ // just a simple markdown type.
                interpreted.items.forEach(function(item, i){
                    formatted.push(<em> {item.interpreted} </em> )
                });
            }
        }else{//Nothing found in your search
            formatted.push(<em>Nothing Found</em>)
        }
        return formatted
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
        search_item_display = this.formatInterpreted(this.state.interpreted)
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <div className={className}>
                        {search_item_display}
                </div>
            </div>
        );
    } // end of render function
}); //end of  SearchBundle
