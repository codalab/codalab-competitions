/** @jsx React.DOM */

var TableBundle = React.createClass({
    mixins: [TableMixin, CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    render: function() {
        var item = this.props.item.state;
        var className = 'table table-responsive' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} /> : null;
        var bundle_info = item.bundle_info;
        var header_items = item.interpreted[0];
        var header_html = header_items.map(function(item, index) {
                return <th key={index}> {item} </th>;
            });
        var focusIndex = this.state.rowFocusIndex;
        var row_items = item.interpreted[1];
        var body_rows_html = row_items.map(function(row_item, index) {
            var focused = index === focusIndex;
            var focusedClass = focused ? 'focused' : '';
            var bundle_url = '/bundles/' + bundle_info[index].uuid;
            var ref = 'row' + index;
            var row_cells = header_items.map(function(header_key, index){
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
                <tr ref={ref} key={index} focused={focused} className={focusedClass}>
                    {row_cells}
                </tr>
            );
        });
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <table className={className} onKeyDown={this.handleKeydown}>
                    <thead>
                        <tr>{header_html}</tr>
                    </thead>
                    <tbody>
                        {body_rows_html}
                    </tbody>
                </table>
            </div>
        );
    } // end of render function
}); //end of  InlineBundle
