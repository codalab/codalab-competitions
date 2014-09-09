/** @jsx React.DOM */

var TableBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        var bundle_info = this.state.bundle_info;
        var header_items = this.state.interpreted[0];
        var header_html = header_items.map(function(item, index) {
                return <th key={index}> {item} </th>;
            });

        var row_items = this.state.interpreted[1];
        var body_rows_html = row_items.map(function(row_item, index) {
            var bundle_url = '/bundles/' + bundle_info[index].uuid + '/';
            var row_cells = header_items.map(function(header_key, index){
                if(header_key == 'name'){
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
                <tr key={index}>
                    {row_cells}
                </tr>
            );
        });

        return(
            <table className="table table-responsive">
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {body_rows_html}
                </tbody>
            </table>
        );
    } // end of render function
}); //end of  InlineBundle
