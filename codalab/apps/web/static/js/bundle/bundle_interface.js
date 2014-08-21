/** @jsx React.DOM */

var Bundle = React.createClass({
    getInitialState: function(){
        return {
            "data_hash": "",
            "uuid": "",
            "hard_dependencies": [],
            "state": "ready",
            "dependencies": [],
            "command": null,
            "bundle_type": "",
            "metadata": {}
        };
    },
    componentWillMount: function() {  // once on the page lets get the ws info
        $.ajax({
            type: "GET",
            //  /api/bundles/0x706<...>d5b66e
            url: "/api" + document.location.pathname,
            dataType: 'json',
            cache: false,
            success: function(data) {
                if(this.isMounted()){
                    this.setState(data);
                }
                $("#bundle-message").hide();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#bundle").html("Bundle was not found.");
                } else {
                    $("#bundle").html("An error occurred. Please try refreshing the page.");
                }
            }.bind(this)
        });
    },
    render: function() {
        var metadata = this.state.metadata;
        var bundleAttrList = []
        Object.keys(metadata).forEach(function(key){
            var val = metadata[key];
            var attr = {};
            attr['key'] = key;
            attr['val'] = val;
            bundleAttrList.push(attr);
        });
        bundleAttrs = bundleAttrList.map(function(item){
            return <BundleAttr item={item} />
        })
        return (
            <div className="row">
                <div className="large-12 columns">
                    <div className="bundle-tile">
                        <div className="large-6 columns">
                            <h4 className="bundle-name bundle-icon-sm bundle-icon-sm-indent">
                                <a href="" className="bundle-link">{this.state.metadata.name}</a>
                            </h4>
                        </div>
                        <div className="large-6 columns">
                            <a href="" className="bundle-download" alt="Download Bundle">
                                <button className="small button secondary">
                                    <i className="fi-arrow-down"></i>
                                </button>
                            </a>
                            <label className="bundle-uuid">{this.state.uuid}</label>
                        </div>
                        <hr />
                        <p>
                            {this.state.metadata.description}
                        </p>
                        <h4>
                            metadata
                        </h4>
                        <table className="bundle-meta-view-container">
                            <tbody>
                                {bundleAttrs}
                            </tbody>
                        </table>
                        <a href="" className="bundle__expand_button">
                            <img src="/static/img/expand-arrow.png" alt="More" />
                        </a>
                        <div className="bundle-file-view-container large-12-columns"></div>
                    </div>
                </div>
            </div>
        );
    }
});

var BundleAttr = React.createClass({
    render: function(){
        if(this.props.item.key !== 'description'){
            return (
                <tr>
                    <th>
                        {this.props.item.key}
                    </th>
                    <td>
                        {this.props.item.val}
                    </td>
                </tr>
            );
        }else {
            return false;
        }
    }
})

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));

