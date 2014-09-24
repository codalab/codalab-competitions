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
    saveMetadata: function(){
        var metadata = this.state.metadata;
        $('#metadata_table input').each(function(){
            var key = $(this).attr('name');
            var val = $(this).val();
            metadata[key] = val;
        });
        this.setState({
            editing:false,
            metadata: metadata
        });
        console.log('------ save the bundle here ------');
        console.log('new metadata:');
        console.log(metadata);
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
        var saveButton;
        var metadata = this.state.metadata;
        var bundleAttrs = [];
        var editing = this.state.editing;
        var tableClassName = 'table' + (editing ? ' editing' : '');
        var editButtonText = editing ? 'cancel' : 'edit';
        if(editing){
            saveButton = <button className="button primary" onClick={this.saveMetadata}>save</button>
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
                            {saveButton}
                        </h4>
                        <table id="metadata_table" className={tableClassName}>
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
        var defaultVal = this.props.val;
        if(this.props.key !== 'description' && !this.props.editing){
            return (
                <tr>
                    <th>
                        {this.props.key}
                    </th>
                    <td>
                        {defaultVal}
                    </td>
                </tr>
            );
        } else if(this.props.editing){
            return (
                <tr>
                    <th>
                        {this.props.key}
                    </th>
                    <td>
                        <input name={this.props.key} type="text" defaultValue={defaultVal} />
                    </td>
                </tr>
            )
        }else {
            return false;
        }
    }
})

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));

