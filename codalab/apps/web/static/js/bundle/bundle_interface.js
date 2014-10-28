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
            "editing": false,
            "edit_permission": false
        };
    },
    toggleEditing: function(){
        this.setState({editing:!this.state.editing});
    },
    saveMetadata: function(){
        var new_metadata = this.state.metadata;
        $('#metadata_table input').each(function(){
            var key = $(this).attr('name');
            var val = $(this).val();
            new_metadata[key] = val;
        });

        console.log('------ save the bundle here ------');
        console.log('new metadata:');
        console.log(new_metadata);
        var postdata = {
            'metadata': new_metadata,
            'uuid': this.state.uuid
        };

        $.ajax({
            type: "POST",
            cache: false,
            //  /api/bundles/0x706<...>d5b66e
            url: "/api" + document.location.pathname,
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            data: JSON.stringify(postdata),
            success: function(data) {
                console.log('success')
                console.log(data)
                if('error' in data){
                    $("#bundle-message").html(data['error']).addClass('alert-danger alert');
                    $("#bundle-message").show()
                }else{
                    this.setState(data);
                    this.setState({
                         editing:false,
                    });
                    $("#bundle-message").hide().removeClass('alert-danger alert');
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                $("#bundle-message").html("An error occurred. Please try refreshing the page.").addClass('alert-danger alert');
                $("#bundle-message").show()
            }.bind(this)
        });
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
                $("#bundle-message").hide().removeClass('alert-danger alert');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#bundle-message").html("Bundle was not found.").addClass('alert-danger alert');
                } else {
                    $("#bundle-message").html("An error occurred. Please try refreshing the page.").addClass('alert-danger alert');
                }
                $('#bundle-content').hide();
            }.bind(this)
        });

        this.updateFileBrowser();
    },
    // File browser is updated based on location.hash!
    updateFileBrowser: function(specific_folder_path, reset_cwd) {
        var folder_path = specific_folder_path || '';

//        if(folder_path == '') {
//            folder_path = location.hash.replace('#', '');
//        }

        // Special case '..' we go up a directory
        if(folder_path == '..') {
            // Remove the last directory
            dirs = this.state.currentWorkingDirectory.split('/');
            dirs.pop();
            folder_path = dirs.join('/');
            // Remove last '/'
            if(folder_path.substr(-1) == '/') {
                return folder_path.substr(0, folder_path.length - 1);
            }

            reset_cwd = true;
        }

        if(reset_cwd) {
            this.setState({"currentWorkingDirectory": folder_path});
        } else {
            if (this.state.currentWorkingDirectory != '') {
                folder_path = this.state.currentWorkingDirectory + "/" + folder_path;
                this.setState({"currentWorkingDirectory": folder_path});
            } else {
                this.setState({"currentWorkingDirectory": folder_path});
            }
        }

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
                    $("#bundle-message").html("Bundle was not found.").addClass('alert-danger alert');
                } else {
                    $("#bundle-message").html("An error occurred. Please try refreshing the page.").addClass('alert-danger alert');
                }
                $('.bundle-file-view-container').hide();
            }.bind(this)
        });
    },
    render: function() {
        var saveButton;
        var metadata = this.state.metadata;
        var bundle_download_url = "/bundles/" + this.state.uuid + "/download";
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

        var fileBrowser = (
                <FileBrowser
                    fileBrowserData={this.state.fileBrowserData}
                    updateFileBrowser={this.updateFileBrowser}
                    currentWorkingDirectory={this.state.currentWorkingDirectory} />
            );

        var edit = ''
        if(this.state.edit_permission){
            edit = (
                <button className="button secondary" onClick={this.toggleEditing}>
                        {editButtonText}
                </button>
            )
        }
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
                                        Download <i className="fi-arrow-down"></i>
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
                            {edit}
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
                            {this.state.fileBrowserData.contents ? fileBrowser : null}
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
            // .. special item, only on inside dirs (current directory not '')
            if(this.props.currentWorkingDirectory) {
                items.push(<FileBrowserItem key=".." type=".." updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory} />);
            }

            // One loop for folders so they are on the top of the list
            for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
                item = this.props.fileBrowserData.contents[i];
                if (item.type == 'directory') {
                    items.push(<FileBrowserItem key={item.name} type={item.type} updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory}  />);
                }
            }

            // Next loop for files
            for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
                item = this.props.fileBrowserData.contents[i];
                if (item.type != 'directory') {
                    items.push(<FileBrowserItem key={item.name} type={item.type} updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory}  />);
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

        var bread_crumbs = (<FileBrowserBreadCrumbs updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory} />);

        return (
            <div>
                <hr></hr>
                <h4>file browser</h4>
                {bread_crumbs}
                {file_browser}
            </div>
            );
    }
});

var FileBrowserBreadCrumbs = React.createClass({
    breadCrumbClicked: function(path) {
        this.props.updateFileBrowser(path, true);
        console.log("breadcrumb -> "+path);
    },
    render: function() {
        var links = [];
        var splitDirs = this.props.currentWorkingDirectory.split('/');
        var currentDirectory = '';

        // Generate list of breadcrumbs separated by ' / '
        for(var i=0; i<splitDirs.length; i++) {
            if(i == 0) {
                currentDirectory += splitDirs[i];
            } else {
                currentDirectory += "/" + splitDirs[i];
            }
            links.push(<a key={splitDirs[i]} onClick={this.breadCrumbClicked.bind(null, currentDirectory)}>{splitDirs[i]}</a>);
            if(i+1<splitDirs.length) {
                links.push(" / ");
            }
        }

        return (
            <div className="file-browser-bread-crumbs">{links}&nbsp;</div>
            );
    }
});

var FileBrowserItem = React.createClass({
    browseToFolder: function(type) {
        this.props.updateFileBrowser(this.props.key);
    },
    render: function() {
        // Type can be 'file' or 'folder'
        var icon = "icon_folder";
        if(this.props.type == "file") {
            icon = "icon_document"
        }

        var file_location = '';
        if(this.props.currentWorkingDirectory) {
            file_location = this.props.currentWorkingDirectory + '/' + this.props.key;
        } else {
            file_location = this.props.key;
        }

        var file_link = document.location.pathname.replace('/bundles/', '/api/bundles/filecontent/') + file_location + '/';

        return (
            <tr>
                <td>
                    <div onClick={this.props.type != 'file' ? this.browseToFolder : null}>
                        <img src={"/static/img/" + icon + ".png"} alt="More" />&nbsp;
                        <a href={this.props.type == 'file' ? file_link : null} target="_blank">{this.props.key}</a>
                    </div>
                </td>
            </tr>
        );
    }
});

React.renderComponent(<Bundle />, document.getElementById('bundle-content'));
