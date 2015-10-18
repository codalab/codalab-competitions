/*
Shows the side panel which contains information about the current bundle or
worksheet (with the focus).
*/

/** @jsx React.DOM */
var WorksheetSidePanel = React.createClass({
    focustype: 'worksheet', // worksheet, bundle or None
    getInitialState: function(){
        return { };
    },
    debouncedFetchExtra: undefined,
    componentDidMount: function(e){
        var self = this;
        $('#dragbar_vertical').mousedown(function(e){
            self.resizePanel(e);
        });
        $(document).mouseup(function(e){
            $(this).unbind('mousemove');
        });
        $(window).resize(function(e){
            self.resetPanel();
        });
    },
    capture_keys: function(){
    },
    _fetch_extra: function(){
        if(this.refs.hasOwnProperty('bundle_info_side_panel')){
            this.refs.bundle_info_side_panel.fetch_extra();
        }
    },
    componentDidUpdate:function(){
        this.capture_keys();
        var self = this;
        if(this.debouncedFetchExtra === undefined){
            // debounce it to wait for user to stop for X time.
            this.debouncedFetchExtra = _.debounce(self._fetch_extra, 500).bind(this);
        }
        //set up the wait for fetching extra
        this.debouncedFetchExtra();

        // update the child if bundle
        if(this.focustype == 'bundle'){
            var current_focus = this.current_focus();
            var subFocusIndex = this.props.subFocusIndex;
            var bundle_info;
            if(current_focus.bundle_info instanceof Array){ //tables are arrays
                bundle_info = current_focus.bundle_info[this.props.subFocusIndex]
            }else{ // content/images/ect. are not
                bundle_info = current_focus.bundle_info
            }
            if(this.refs.hasOwnProperty('bundle_info_side_panel')){ // just to double check so no errors
                this.refs.bundle_info_side_panel.setState(bundle_info);
            }
        }

    },
    current_focus: function(){
        var focus = undefined;
        if(this.props.focusIndex > -1){
            focus = ws_obj.state.items[this.props.focusIndex].state;
            if(focus.mode == "markup"){
                this.focustype = '';
                focus = undefined;
                return focus;
            }
            if(focus.mode == "worksheet" || focus.mode == "action"){
                this.focustype = 'worksheet';
                if(focus.mode != "worksheet"){ // are we not looking at a sub worksheet
                     //for lets default it back to showing the main worksheet info
                     focus = ws_obj.state;
                }
            }else{
                this.focustype = 'bundle';
            }// end of if focus.modes
        }else{// there is no focus index, just show the worksheet infomation
            focus = ws_obj.state;
            this.focustype = 'worksheet';
        }
        return  focus;
    },
    resizePanel: function(e){
        e.preventDefault();
        $(document).mousemove(function(e){
            var windowWidth = $(window).width();
            var panelWidth = windowWidth - e.pageX;
            var panelWidthPercentage = (windowWidth - e.pageX) / windowWidth * 100;
            console.log('########')
            console.log(panelWidth);
            console.log(panelWidthPercentage);
            if(240 < panelWidth && panelWidthPercentage < 55){
                $('.ws-container').css('width', e.pageX);
                $('.ws-panel').css('width', panelWidthPercentage + '%');
                $('#dragbar_vertical').css('right', panelWidthPercentage + '%');
            }
        });
    },
    resetPanel: function(){
        var windowWidth = $(window).width();
        if(windowWidth < 768){
            $('.ws-container').removeAttr('style');
        }else {
            var panelWidth = parseInt($('.ws-panel').css('width'));
            var containerWidth = windowWidth - panelWidth;
            $('.ws-container').css('width', containerWidth);
        }
    },
    render: function(){
        var current_focus = this.current_focus();
        var side_panel_details = '';
        switch (this.focustype) {
            case 'worksheet':
                side_panel_details = <WorksheetDetailSidePanel
                                        key={'ws' + this.props.focusIndex}
                                        item={current_focus}
                                        ref="worksheet_info_side_panel"
                                    />
                break;
            case 'bundle':
                // TODO TODO set bundle detail state
                side_panel_details = <BundleDetailSidePanel
                                        key={this.props.focusIndex + this.props.subFocusIndex}
                                        item={current_focus}
                                        subFocusIndex={this.props.subFocusIndex}
                                        ref="bundle_info_side_panel"
                                    />
                break;
            default:
                break;
        }


        return (
            <div className="ws-panel">
                {side_panel_details}
            </div>
        )
    }
});

////////////////////////////////////////////////////////////

/** @jsx React.DOM */
// When selecting a worksheet.
var WorksheetDetailSidePanel = React.createClass({
    getInitialState: function(){
        return { };
    },
    componentDidMount: function() {
    },
    componentWillUnmount: function() {
    },
    render: function() {
      // Select the current worksheet or the subworksheet.
      var worksheet = this.props.item;
      if (worksheet.hasOwnProperty('subworksheet_info'))
        worksheet = worksheet.subworksheet_info;

      // Show brief summary of contents
      var rows = [];
      if (worksheet.items) {
        worksheet.items.forEach(function(item) {
          if (item.state.bundle_info) {
            // Show bundle
            var bundle_infos = item.state.bundle_info;
            if (!(bundle_infos instanceof Array))
              bundle_infos = [bundle_infos];

            bundle_infos.forEach(function(b) {
              var url = "/bundles/" + b.uuid;
              var short_uuid = shorten_uuid(b.uuid);
              rows.push(<tr>
                <td>{b.bundle_type}</td>
                <td><a href={url} target="_blank">{b.metadata.name}({short_uuid})</a></td>
              </tr>);
            });
          } else if (item.state.mode == 'worksheet') {
            // Show worksheet
            var info = item.state.subworksheet_info;
            var title = info.title || info.name;
            var url = '/worksheets/' + info.uuid;
            rows.push(<tr>
              <td>worksheet</td>
              <td><a href={url} target="_blank">{title}</a></td>
            </tr>);
          }
        });
      }

      var bundles_html = (
        <div className="bundles-table">
            <table className="bundle-meta table">
                <thead>
                  <tr>
                    <th>type</th>
                    <th>name</th>
                  </tr>
                </thead>
                <tbody>
                  {rows}
                </tbody>
            </table>
        </div>
      );

      return (
          <div id="panel_content">
              <h4 className="ws-title">{worksheet.title}</h4>
              <table className="bundle-meta table">
                <tr><th>name</th><td>{worksheet.name}</td></tr>
                <tr><th>uuid</th><td>{worksheet.uuid}</td></tr>
                <tr><th>owner</th><td>{worksheet.owner_name}</td></tr>
                <tr><th>permissions</th><td>{render_permissions(worksheet)}</td></tr>
              </table>
              {bundles_html}
          </div>
      );
    }
});

////////////////////////////////////////////////////////////

/** @jsx React.DOM */
// When selecting a bundle.
var BundleDetailSidePanel = React.createClass({
    getInitialState: function() {
        // Set the state from the props and leave props.item alone
        var item = this.props.item;
        var bundle_info;
        if (item.bundle_info instanceof Array) { // Is a table
          bundle_info = item.bundle_info[this.props.subFocusIndex];
        } else {
          bundle_info = item.bundle_info;
        }

        bundle_info.fileBrowserData = {};
        bundle_info.currentWorkingDirectory = '';

        return bundle_info;
    },
    fetch_extra: function() {
        // Fetch detailed information about this bundle.
        var bundle_info = this.state;
        ws_bundle_obj.state = bundle_info;

        // Break out if we don't match. The user has moved on.
        if(ws_bundle_obj.current_uuid == bundle_info.uuid){
            return;
        }

        //update we are at the correct focus.
        ws_bundle_obj.current_uuid = bundle_info.uuid;
        ws_bundle_obj.fetch({
            success: function(data){
                console.log("BundleDetailSidePanel.fetch_extra: " + bundle_info.uuid);
                // do a check since this fires async to double check users intent.
                if(ws_bundle_obj.current_uuid == bundle_info.uuid){
                    if(this.isMounted()){
                        this.setState(data)
                    }
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(ws_obj.url, status, err);
            }.bind(this)
        });
    },
    componentDidMount: function(){},
    componentWillUnmount: function(){},
    componentWillMount: function() {
      this.updateFileBrowser();
    },

    updateFileBrowser: function(folder_path, reset_cwd) {
        folder_path = folder_path || '';
        if (folder_path == '..')
          folder_path = this.state.currentWorkingDirectory.replace(/\/[^\/]*$/, '');

        if(reset_cwd) {
        } else {
          if (this.state.currentWorkingDirectory != '')
              folder_path = this.state.currentWorkingDirectory + "/" + folder_path;
        }
        this.setState({"currentWorkingDirectory": folder_path});

        var url = '/api/bundles/content/' + this.state.uuid + '/' + folder_path;
        $.ajax({
            type: "GET",
            url: url,
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
      var fileBrowser = (<FileBrowser
        bundle_uuid={this.state.uuid}
        fileBrowserData={this.state.fileBrowserData}
        updateFileBrowser={this.updateFileBrowser}
        currentWorkingDirectory={this.state.currentWorkingDirectory}/>);

      var bundle_info = this.state;
      return (<div id="panel_content">
        {renderHeader(bundle_info)}
        {renderDependencies(bundle_info)}
        {renderContents(bundle_info)}
        {fileBrowser}
        {renderMetadata(bundle_info)}
        {renderHostWorksheets(bundle_info)}
      </div>);
    }
});

function renderDependencies(bundle_info) {
  var dependencies_table = [];
  if (!bundle_info.dependencies || bundle_info.dependencies.length == 0) return <div/>;

  bundle_info.dependencies.forEach(function(dep, i) {
    var dep_bundle_url = "/bundles/" + dep.parent_uuid;
    dependencies_table.push(<tr>
      <td>
          {dep.child_path}
      </td>
      <td>
          &rarr; {dep.parent_name}(<a href={dep_bundle_url}>{shorten_uuid(dep.parent_uuid)}</a>){dep.parent_path ? '/' + dep.parent_path : ''}
      </td>
    </tr>);
  });

  return (<div>
    <h4>dependencies</h4>
    <table className="bundle-meta table">
      <tbody>{dependencies_table}</tbody>
    </table>
  </div>);
}

function renderMetadata(bundle_info) {
  // TODO: allow editing
  var metadata = bundle_info.metadata;
  var metadata_list_html = [];

  // Sort the metadata by key.
  var keys = [];
  for (var property in metadata) {
    if (metadata.hasOwnProperty(property))
      keys.push(property);
  }
  keys.sort();
  for (var i = 0; i < keys.length; i++) {
    var property = keys[i];
    metadata_list_html.push(<tr>
      <th>{property}</th>
      <td><span>{metadata[property]}</span></td>
    </tr>);
  }

  return (<div>
    <h4>metadata</h4>
    <table className="bundle-meta table">
      <tbody>{metadata_list_html}</tbody>
    </table>
  </div>);
}

function renderHeader(bundle_info) {
  var bundle_url = '/bundles/' + bundle_info.uuid;
  var bundle_download_url = "/bundles/" + bundle_info.uuid + "/download";
  var bundle_name;
  if (bundle_info.metadata.name) {
    // TODO: allow editing
    bundle_name = <h3 className="bundle-name">{bundle_info.metadata.name}</h3>
  }
  var bundle_state_class = 'bundle-state state-' + (bundle_info.state || 'ready');
  var bundle_description = bundle_info.metadata.description ? <p className="bundle-description">{bundle_info.metadata.description}</p> : ''

  // Display basic information
  function createRow(key, value) {
    return (<tr>
      <th>{key}:</th>
      <td>{value}</td>
    </tr>);
  }
  var rows = [];
  rows.push(createRow('uuid', bundle_info.uuid));
  rows.push(createRow('owner', bundle_info.owner_name));
  rows.push(createRow('permissions', render_permissions(bundle_info)));
  if (bundle_info.bundle_type == 'run') {
    rows.push(createRow('command', bundle_info.command));
    rows.push(createRow('state', <span className={bundle_state_class}>{bundle_info.state}</span>));
  }

  return (<div>
    <div className="bundle-header">
      <a href={bundle_url} className="bundle-link" target="_blank">{bundle_name}</a>
      {bundle_description}
    </div>
    <table className="bundle-meta table">
      <tbody>{rows}</tbody>
    </table>
    <div className="bundle-links">
      <a href={bundle_download_url} className="bundle-download btn btn-default btn-sm" alt="Download Bundle">
        <span className="glyphicon glyphicon-download-alt"></span>
      </a>
    </div>
  </div>);
}

function renderContents(bundle_info) {
  var stdout_html = '';
  if (bundle_info.stdout) {
    var stdout_url = '/api/bundles/filecontent/' + bundle_info.uuid + '/stdout';
    stdout_html = (<span>
      <h4><a href={stdout_url} target="_blank">stdout</a></h4>
      <div className="bundle-meta">
          <pre>
              {bundle_info.stdout}
          </pre>
      </div>
    </span>);
  }

  var stderr_html = '';
  if (bundle_info.stderr) {
    var stderr_url = '/api/bundles/filecontent/' + bundle_info.uuid + '/stderr';
    stderr_html = (<span>
      <h4><a href={stderr_url} target="_blank">stderr</a></h4>
      <div className="bundle-meta">
          <pre>
              {bundle_info.stderr}
          </pre>
      </div>
    </span>);
  }

  return (<div>
    {stdout_html}
    {stderr_html}
  </div>);
}

function renderHostWorksheets(bundle_info) {
  if (!bundle_info.host_worksheets) return <div/>;

  var host_worksheets_rows = [];
  bundle_info.host_worksheets.forEach(function(worksheet) {
    var host_worksheets_url = "/worksheets/" + worksheet.uuid;
    host_worksheets_rows.push(<tr>
      <td>
          <a href={host_worksheets_url}>{worksheet.name}</a>
      </td>
    </tr>);
  });
  
  return (
    <div className="host-worksheets-table">
        <h4>host worksheets</h4>
        <table className="bundle-meta table">
          <tbody>
              {host_worksheets_rows}
          </tbody>
        </table>
    </div>
  );
}

////////////////////////////////////////////////////////////
// FileBrowser

var FileBrowser = React.createClass({
    render: function() {
        var items = [];
        if (this.props.fileBrowserData.contents) {
          // Parent directory (..)
          if(this.props.currentWorkingDirectory) {
            items.push(<FileBrowserItem key=".." index=".."type=".." updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory} />);
          }

          // Show directories
          for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
            var item = this.props.fileBrowserData.contents[i];
            if (item.type == 'directory')
              items.push(<FileBrowserItem key={item.name} index={item.name} type={item.type} updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory}  />);
          }

          // Show files
          for (var i = 0; i < this.props.fileBrowserData.contents.length; i++) {
            var item = this.props.fileBrowserData.contents[i];
            if (item.type != 'directory')
              items.push(<FileBrowserItem bundle_uuid={this.props.bundle_uuid} key={item.name} index={item.name} type={item.type} size={item.size} updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory}  />);
          }

          file_browser = (
            <table className="file-browser-table">
              <tbody>{items}</tbody>
            </table>
          );
        } else {
          file_browser = (<b>(no files)</b>);
        }

        var bread_crumbs = (<FileBrowserBreadCrumbs
            updateFileBrowser={this.props.updateFileBrowser}
            currentWorkingDirectory={this.props.currentWorkingDirectory}/>);

        return (<div>
          <div className="panel panel-default">
              {bread_crumbs.props.currentWorkingDirectory.length ? bread_crumbs : null}
              <div className="panel-body">
                  {file_browser}
              </div>
          </div>
        </div>);
    }
});

var FileBrowserBreadCrumbs = React.createClass({
    breadCrumbClicked: function(path) {
        console.log("breadcrumb -> "+path);
        //this.props.updateFileBrowser(path, true);
    },
    render: function() {
        var links = [];
        var splitDirs = this.props.currentWorkingDirectory.split('/');
        var currentDirectory = '';

        // Generate list of breadcrumbs separated by ' / '
        for(var i=0; i < splitDirs.length; i++) {
            if(i == 0) {
                currentDirectory += splitDirs[i];
            } else {
                currentDirectory += "/" + splitDirs[i];
            }
            links.push(<span key={splitDirs[i]} index={splitDirs[i]} onClick={this.breadCrumbClicked.bind(null, currentDirectory)}> / {splitDirs[i]}</span>);
        }

        return (
            <div className="panel-heading">{links}</div>
        );
    }
});

var FileBrowserItem = React.createClass({
    browseToFolder: function(type) {
        this.props.updateFileBrowser(this.props.index);
    },
    render: function() {
        // Type can be 'file' or 'folder'
        var icon = "glyphicon-folder-close";
        if (this.props.type == "file") {
          icon = "glyphicon-file";
        }
        icon += " glyphicon";

        var file_location = '';
        if (this.props.currentWorkingDirectory) {
          file_location = this.props.currentWorkingDirectory + '/' + this.props.index;
        } else {
          file_location = this.props.index;
        }

        var file_link = '/api/bundles/filecontent/' + this.props.bundle_uuid + '/' + file_location;
        var size = '';
        if(this.props.hasOwnProperty('size')){
            if(this.props.size == 0 || this.props.size === undefined)
                size = "0 bytes"
            else{ // we have a real size create a nice human readable version
                var k = 1000;
                var sizes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                var i = Math.floor(Math.log(this.props.size) / Math.log(k));
                size = (this.props.size / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i];
            }
        }
        return (
            <tr>
                <td>
                    <div className={this.props.type} onClick={this.props.type != 'file' ? this.browseToFolder : null}>
                        <span className={icon} alt="More"></span>
                        <a href={this.props.type == 'file' ? file_link : null} target="_blank">{this.props.index}</a>
                        <span className="pull-right"> {size} </span>
                    </div>
                </td>
            </tr>
        );
    }
});
