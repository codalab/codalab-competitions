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
            "showFileBrowser": false,
            "fileBrowserData": "",
            "currentWorkingDirectory": ""
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
        this.setState({"showFileBrowser": !this.state.showFileBrowser});

        // it's still false, but is true
        if(!this.state.showFileBrowser) {
            this.updateFileBrowser();
        }
    },
    // File browser is updated based on location.hash!
    updateFileBrowser: function(specific_folder_path) {
        var folder_path = specific_folder_path || '';

        if(folder_path == '') {
            folder_path = location.hash.replace('#', '');
        }

        if(this.state.currentWorkingDirectory != '') {
            folder_path = this.state.currentWorkingDirectory + "/" + folder_path;
            this.setState({"currentWorkingDirectory": folder_path});
        } else {
            this.setState({"currentWorkingDirectory": folder_path});
        }

        location.hash = folder_path;

        console.log("fp: " + folder_path);
        console.log("cwd: " + this.state.currentWorkingDirectory);

        $.ajax({
            type: "GET",
            //  /api/bundles/0x706<...>d5b66e
            url: document.location.pathname.replace('/bundles/', '/api/bundles/content/') + folder_path + '/', //extra slash at end means root dir
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({"fileBrowserData": data});
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
    },
    render: function() {
        var metadata = this.state.metadata;

        var bundleAttrs = [];
        for(var k in metadata) {
            bundleAttrs.push(<BundleAttr key={k} val={metadata[k]} />);
        }
        bundle_download_url = "/bundles/" + this.state.uuid + "/download";

        var fileBrowser = <FileBrowser fileBrowserData={this.state.fileBrowserData} updateFileBrowser={this.updateFileBrowser} />;

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
        var item;

        if(!this.props.fileBrowserData.contents) {
            return (
                <div className="row">
                    <div className="large-12 columns">
                        <div className="bundle-tile">
                            <h4>
                                <b>File Browser</b>
                            </h4>
                            <b>No files found</b>
                        </div>
                    </div>
                </div>
                );
        } else {
            // One loop for folders so they are on the top of the list
            for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
                item = this.props.fileBrowserData.contents[i];
                if (item.type == 'directory') {
                    items.push(<FileBrowserItem key={item.name} type={item.type} updateFileBrowser={this.props.updateFileBrowser} />);
                }
            }

            // Next loop for files
            for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
                item = this.props.fileBrowserData.contents[i];
                if (item.type != 'directory') {
                    items.push(<FileBrowserItem key={item.name} type={item.type} updateFileBrowser={this.props.updateFileBrowser} />);
                }
            }

            return (
                <div className="row">
                    <div className="large-12 columns">
                        <div className="bundle-tile">
                            <h4>
                                <b>File Browser</b>
                            </h4>
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
    }
});

var FileBrowserItem = React.createClass({
    linkClicked: function(evt) {
        this.props.updateFileBrowser(this.props.key);
    },
    render: function() {
        // Type can be 'file' or 'folder'
        var icon = "icon_folder";
        var link = this.props.key;
        if(this.props.type == "file") {
            icon = "icon_document"
        }

        return (
            <tr>
                <td>
                    <div onClick={this.linkClicked}>
                        <img src={"/static/img/" + icon + ".png"} alt="More" />&nbsp;
                        <b>{this.props.key}</b>
                    </div>
                </td>
            </tr>
        );
    }
});

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));
