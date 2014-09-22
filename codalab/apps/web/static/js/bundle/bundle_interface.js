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
            "metadata": {},
            "editing": false
        };
    },
    toggleEditing: function(){
        this.setState({editing:!this.state.editing});
    },
    componentWillMount: function() {  // once on the page lets get the bundle info
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
                $("#bundle-message").hide().removeClass('alert-box alert');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#bundle-message").html("Bundle was not found.").addClass('alert-box alert');
                } else {
                    $("#bundle-message").html("An error occurred. Please try refreshing the page.").addClass('alert-box alert');
                }
                $('#bundle-content').hide();
            }.bind(this)
        });
    },
    render: function() {
        var footer;
        var metadata = this.state.metadata;
        var bundleAttrs = [];
        var editing = this.state.editing;
        var editButtonText = editing ? 'save' : 'edit';
        if(editing){
            footer = <tfoot><tr><td colSpan="2"><button>+ add row</button></td></tr></tfoot>
        }
        for(var k in metadata) {
            bundleAttrs.push(<BundleAttr key={k} val={metadata[k]} editing={editing} />);
        };
        bundle_download_url = "/bundles/" + this.state.uuid + "/download"
        return (
            <div className="row">
                <div className="large-12 columns">
                    <div className="bundle-tile">
                        <div className="bundle-header">
                            <div className="large-6 columns">
                                <h4 className="bundle-name bundle-icon-sm bundle-icon-sm-indent">
                                    <a href="" className="bundle-link">{this.state.metadata.name}</a>
                                </h4>
                            </div>
                            <div className="large-6 columns">
                                <a href={bundle_download_url} className="bundle-download" alt="Download Bundle">
                                    <button className="small button secondary">
                                            <i className="fi-arrow-down"></i>
                                    </button>
                                </a>
                                <div className="bundle-uuid">{this.state.uuid}</div>
                            </div>
                        </div>
                        <p>
                            {this.state.metadata.description}
                        </p>
                        <h4>
                            metadata
                            <button className="button secondary" onClick={this.toggleEditing}>
                                {editButtonText}
                            </button>
                        </h4>
                        <table className="table">
                            <tbody>
                                {bundleAttrs}
                            </tbody>
                            {footer}
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
        if(this.props.key !== 'description' && this.props.val !== ''){
            if(this.props.editing){
                return (
                    <tr>
                        <th>
                            <input type="text" defaultValue={this.props.key} />
                        </th>
                        <td>
                            <input type="text" defaultValue={this.props.val} />
                        </td>
                    </tr>
                )
            } else {
                return (
                    <tr>
                        <th>
                            {this.props.key}
                        </th>
                        <td>
                            {this.props.val}
                        </td>
                    </tr>
                );
            }
        }else {
            return false;
        }
    }
})

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));

