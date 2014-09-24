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
            "files": {},
            "showFileBrowser": false
        };
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
    toggleFileBrowser: function() {
        $.ajax({
            type: "GET",
            //  /api/bundles/0x706<...>d5b66e
            url: document.location.pathname.replace('/bundles/', '/api/bundles/content/') + '/', //extra slash at end means root dir
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log(data);
            }.bind(this),
            error: function(xhr, status, err) {
                if (xhr.status != 404) {
                    $("#bundle-message").html("Bundle was not found.").addClass('alert-box alert');
                } else {
                    $("#bundle-message").html("An error occurred. Please try refreshing the page.").addClass('alert-box alert');
                }
                $('.bundle-file-view-container').hide();
            }.bind(this)
        });
        this.setState({"showFileBrowser": !this.state.showFileBrowser});
    },
    render: function() {
        var metadata = this.state.metadata;

        var bundleAttrs = [];
        for(var k in metadata) {
            bundleAttrs.push(<BundleAttr key={k} val={metadata[k]} />);
        }
        bundle_download_url = "/bundles/" + this.state.uuid + "/download";

        var fileBrowser = <FileBrowser />;

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
                        </h4>
                        <table className="table">
                            <tbody>
                                {bundleAttrs}
                            </tbody>
                        </table>
                        <div className="bundle__expand_button" onClick={this.toggleFileBrowser}>
                            <img src="/static/img/expand-arrow.png" alt="More" />
                        </div>
                    </div>

                    <div class="bundle-file-view-container">
                        {this.state.showFileBrowser ? fileBrowser : null}
                    </div>
                </div>
            </div>
        );
    }
});

var BundleAttr = React.createClass({
    render: function(){
        if(this.props.key !== 'description' && this.props.val !== ''){
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
        }else {
            return false;
        }
    }
});

var FileBrowser = React.createClass({
    render: function() {
        var items = [];

        items.push(<FileBrowserItem key='test1.py' />);
        items.push(<FileBrowserItem key='test2.py' />);

        return (
            <div className="row">
                <div className="large-12 columns">
                    <div className="bundle-tile">
                        <h4><b>File Browser</b></h4>
                        <table>
                            <thead>
                                <th>File name</th>
                            </thead>
                            <tbody>
                                {items}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }
});

var FileBrowserItem = React.createClass({
    // Type can be 'file' or 'folder'
    type: 'file',
    render: function() {
        return (
            <tr>
                <td>
                    (icon file or folder) <a href="#">{this.props.key}</a> click this to view file OR if folder go there
                </td>
            </tr>
        );
    }
});

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));
