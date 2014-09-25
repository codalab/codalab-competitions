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
            "fileBrowserData": "",
            "currentWorkingDirectory": "",
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

        this.updateFileBrowser();
    },
    // File browser is updated based on location.hash!
    updateFileBrowser: function(specific_folder_path) {
        var folder_path = specific_folder_path || '';

//        if(folder_path == '') {
//            folder_path = location.hash.replace('#', '');
//        }

        if(this.state.currentWorkingDirectory != '') {
            folder_path = this.state.currentWorkingDirectory + "/" + folder_path;
            this.setState({"currentWorkingDirectory": folder_path});
        } else {
            this.setState({"currentWorkingDirectory": folder_path});
        }

        //location.hash = folder_path;

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
        }
        var bundle_download_url = "/bundles/" + this.state.uuid + "/download";

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
                            <button className="button secondary" onClick={this.toggleEditing}>
                                {editButtonText}
                            </button>
                            {saveButton}
                        </h4>
                        <div className="row">
                            <div className="large-6 columns">
                                <table id="metadata_table" className={tableClassName}>
                                    <tbody>
                                        {bundleAttrs}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div className="bundle-file-view-container">
                            {fileBrowser}
                        </div>
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
                    <th width="33%">
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
                    <th width="33%">
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
});

var FileBrowser = React.createClass({
    render: function() {
        var items = [];
        var item; // so we have 1, see later
        var files;
        if(this.props.fileBrowserData.contents) {
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

            file_browser = (

                <table className="file-browser-table">
                    <thead>
                        <th>File name</th>
                    </thead>
                    <tbody>
                        {items}
                    </tbody>
                </table>
                );
        } else {
            file_browser = (<b>No files found</b>);
        }

        return (
            <div>
                <h4>file browser</h4>
                {file_browser}
            </div>
            );
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
