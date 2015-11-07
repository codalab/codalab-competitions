/*
Shows the side panel which contains information about the current bundle or
worksheet (with the focus).
*/

/** @jsx React.DOM */
var WorksheetSidePanel = React.createClass({
    getInitialState: function() {
        return { };
    },
    componentDidMount: function(e) {
        var self = this;
        $('#dragbar_vertical').mousedown(function(e) {
            self.resizePanel(e);
        });
        $(document).mouseup(function(e) {
            $(this).unbind('mousemove');
        });
        $(window).resize(function(e) {
            self.resetPanel();
        });
    },

    componentDidUpdate: function() {
        var __innerFetchExtra = function() {
          //console.log('__innerFetchExtra');
          if (this.refs.hasOwnProperty('bundle_info_side_panel'))
            this.refs.bundle_info_side_panel.fetchExtra();
        }
        if (this.debouncedFetchExtra === undefined)
            this.debouncedFetchExtra = _.debounce(__innerFetchExtra, 200).bind(this);
        this.debouncedFetchExtra();
    },

    getFocus: function() {
        // Return the state to show on the side panel
        var focusedBundle = this.props.ws.state.items[this.props.focusIndex];
        if (this.props.focusIndex == -1 || focusedBundle === undefined) {
          return this.props.ws.state;  // Show current worksheet
        }
        return focusedBundle.state;
    },

    // What kind of thing is it?
    isFocusWorksheet: function(focus) {
      return focus.mode === undefined || focus.mode == 'worksheet';
    },
    isFocusMarkup: function(focus) {
      return focus.mode == 'markup';
    },
    isFocusBundle: function(focus) {
      return !this.isFocusWorksheet(focus) && !this.isFocusMarkup(focus);
    },
    getBundleInfo: function(focus) {
      if (focus.mode == 'table')  // Drill down into row of table
          return focus.bundle_info[this.props.subFocusIndex];
      else
          return focus.bundle_info;
    },

    resizePanel: function(e) {
        e.preventDefault();
        $(document).mousemove(function(e) {
            var windowWidth = $(window).width();
            var panelWidth = windowWidth - e.pageX;
            var panelWidthPercentage = (windowWidth - e.pageX) / windowWidth * 100;
            if (240 < panelWidth && panelWidthPercentage < 55) {
                $('.ws-container').css('width', e.pageX);
                $('.ws-panel').css('width', panelWidthPercentage + '%');
                $('#dragbar_vertical').css('right', panelWidthPercentage + '%');
            }
        });
    },
    resetPanel: function() {
        var windowWidth = $(window).width();
        if (windowWidth < 768) {
            $('.ws-container').removeAttr('style');
        } else {
            var panelWidth = parseInt($('.ws-panel').css('width'));
            var containerWidth = windowWidth - panelWidth;
            $('.ws-container').css('width', containerWidth);
        }
    },

    render: function() {
        //console.log('WorksheetSidePanel.render');

        // General buttons
        var buttons = '';
        if (home_worksheet_name) {
          buttons = <div>
            <button className="active" onClick={this.props.myHomeWorksheet}>My home worksheet</button>
            &nbsp;
            <button className="active" onClick={this.props.uploadBundle}>Upload bundle</button>
          </div>;
        }

        var focus = this.getFocus();
        var side_panel_details = '';
        if (this.isFocusWorksheet(focus)) {
          // Show worksheet (either main worksheet or subworksheet)
          var worksheet_info;
          if (focus.mode == 'worksheet')
            worksheet_info = focus.subworksheet_info;
          else
            worksheet_info = focus;

          side_panel_details = <WorksheetDetailSidePanel
                                 key={'ws' + this.props.focusIndex}
                                 worksheet_info={worksheet_info}
                                 ref="worksheet_info_side_panel"
                               />;
        } else if (this.isFocusMarkup(focus)) {
          // Show nothing (maybe later show markdown just for fun?)
        } else if (this.isFocusBundle(focus)) {
          // Show bundle (either full bundle or row in table)
          var bundle_info = this.getBundleInfo(focus);
          if (bundle_info) {
            side_panel_details = <BundleDetailSidePanel
                                   key={'table' + this.props.focusIndex + ',' + this.props.subFocusIndex}
                                   bundle_info={bundle_info}
                                   ref="bundle_info_side_panel"
                                   bundleMetadataChanged={this.props.bundleMetadataChanged}
                                 />;
          }
        }

        return (
          <div className="ws-panel">
              {buttons}
              {side_panel_details}
          </div>
        );
    }
});

////////////////////////////////////////////////////////////

/** @jsx React.DOM */
// When selecting a worksheet.
var WorksheetDetailSidePanel = React.createClass({
    getInitialState: function() {
        return { };
    },

    render: function() {
      // Select the current worksheet or the subworksheet.
      var worksheet = this.props.worksheet_info;

      // Show brief summary of contents.
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
              <h4 className="ws-title"><a href="#" id='title' className='editable-field' data-value={worksheet.title} data-type="text" data-url="/api/worksheets/command/">{worksheet.title}</a></h4>
              <table className="bundle-meta table">
                <tr><th>name</th><td><a href="#" id='name' className='editable-field' data-value={worksheet.name} data-type="text" data-url="/api/worksheets/command/">{worksheet.name}</a></td></tr>
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
// props:
// - bundle_info: contains information about the bundle to render
var BundleDetailSidePanel = React.createClass({
    getInitialState: function() {
        var bundle_info = this.props.bundle_info;

        // State associated with file browser
        bundle_info.fileBrowserData = {};
        bundle_info.currentWorkingDirectory = '';

        return bundle_info;
    },

    fetchExtra: function() {
      // Fetch detailed information about this bundle.
      var bundle_info = this.state;
      //console.log('BundleDetailSidePanel.fetchExtra', bundle_info.uuid);
      $.ajax({
          type: "GET",
          url: "/api/bundles/" + bundle_info.uuid,
          dataType: 'json',
          cache: false,
          success: function(data) {
              //console.log("BundleDetailSidePanel.fetchExtra success: " + bundle_info.uuid);
              if (this.isMounted()) {
                  this.setState(data);
                  this.updateFileBrowser('');
              }
          }.bind(this),
          error: function(xhr, status, err) {
            console.log(xhr, status, err);
          }.bind(this)
      });
    },

    updateFileBrowser: function(folder_path) {
        if (folder_path == '..') {  // Go to parent directory
            folder_path = this.state.currentWorkingDirectory.substring(0, this.state.currentWorkingDirectory.lastIndexOf('/'));
        }
        else if (this.state.currentWorkingDirectory != '') {
            if (folder_path != '') {
                folder_path = this.state.currentWorkingDirectory + "/" + folder_path;
            }
            else {
                folder_path = this.state.currentWorkingDirectory;
            }
        }
        this.setState({"currentWorkingDirectory": folder_path});

        var url = '/api/bundles/content/' + this.state.uuid + '/' + folder_path;
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                if (this.isMounted())
                  this.setState({'fileBrowserData': data});
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
      //console.log('BundleDetailSidePanel.render');
      var bundle_info = this.state;

      var fileBrowser = '';
      if (bundle_info.type == 'directory') {
        fileBrowser = (<FileBrowser
          bundle_uuid={this.state.uuid}
          fileBrowserData={this.state.fileBrowserData}
          updateFileBrowser={this.updateFileBrowser}
          currentWorkingDirectory={this.state.currentWorkingDirectory}/>);
      }

      return (<div id="panel_content">
        {renderHeader(bundle_info)}
        {renderDependencies(bundle_info)}
        {renderContents(bundle_info)}
        {fileBrowser}
        {renderMetadata(bundle_info, this.props.bundleMetadataChanged)}
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

function renderMetadata(bundle_info, bundleMetadataChanged) {
/*
In the current implementaiton, refreshWorksheet method of worksheet_content
is passed in as bundleMetadataChanged and is just called inorder to reflect
changes made in the side-panel on the main page.
TODO: The response object contains the uuid of the modified object.
      Use that to update the main view instead of refrsehing the
      entire worksheet.
*/
  var metadata = bundle_info.metadata;
  var metadata_list_html = [];

  // Sort the metadata by key.
  var keys = [];
  var editableMetadataFields = bundle_info.editable_metadata_fields;
  for (var property in metadata) {
    if (metadata.hasOwnProperty(property))
      keys.push(property);
  }
  keys.sort();
  for (var i = 0; i < keys.length; i++) {
    var property = keys[i];
    if (bundle_info.edit_permission && editableMetadataFields && editableMetadataFields.indexOf(property) >= 0){
      metadata_list_html.push(<tr>
        <th>{property}</th>
        <td><a href="#" className='editable-field' id={property} data-type="text" data-url={"/api/bundles/"+bundle_info.uuid+"/"}>{metadata[property]}</a></td>
      </tr>);
    }
    else{
      metadata_list_html.push(<tr>
        <th>{property}</th>
        <td><span>{metadata[property]}</span></td>
      </tr>);
    }
  }
  $.fn.editable.defaults.mode = 'inline';
  $(document).ready(function() {
    $('.editable-field').editable({
      send: 'always',
      params: function(params) {
        var data = {};
        metadata[params.name] = params.value;
        data['metadata'] = metadata;
       return JSON.stringify(data);
      },
      success: function(response, newValue) {
          if(response.error) return response.error;
          if (bundleMetadataChanged != undefined) {
            bundleMetadataChanged();
        }
      }
    });
  });

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
    bundle_name = <h3 className="bundle-name"><a href="#" id='title' className='editable-field' data-value={bundle_info.metadata.name} data-type="text" data-url="/api/worksheets/command/">{bundle_info.metadata.name}</a></h3>
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
      {bundle_name}
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
        <pre>{bundle_info.stdout}</pre>
      </div>
    </span>);
  }

  var stderr_html = '';
  if (bundle_info.stderr) {
    var stderr_url = '/api/bundles/filecontent/' + bundle_info.uuid + '/stderr';
    stderr_html = (<span>
      <h4><a href={stderr_url} target="_blank">stderr</a></h4>
      <div className="bundle-meta">
        <pre>{bundle_info.stderr}</pre>
      </div>
    </span>);
  }

  var contents_html = '';
  if (bundle_info.type == 'file') {
    contents_html = (<span>
      <h4>contents</h4>
      <div className="bundle-meta">
        <pre>{bundle_info.file_contents}</pre>
      </div>
    </span>);
  }

  return (<div>
    {contents_html}
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
          if (this.props.currentWorkingDirectory) {
            items.push(<FileBrowserItem key=".." index=".."type=".." updateFileBrowser={this.props.updateFileBrowser} currentWorkingDirectory={this.props.currentWorkingDirectory} />);
          }

          // Sort by name
          var entities = this.props.fileBrowserData.contents;
          entities.sort(function(a, b) {
            if (a.name < b.name) return -1;
            if (a.name > b.name) return +1;
            return 0;
          });
          var self = this;

          // Show directories
          entities.forEach(function(item) {
            if (item.type == 'directory')
              items.push(<FileBrowserItem key={item.name} index={item.name} type={item.type} updateFileBrowser={self.props.updateFileBrowser} currentWorkingDirectory={self.props.currentWorkingDirectory}  />);
          });

          // Show files
          entities.forEach(function(item) {
            if (item.type == 'file')
              items.push(<FileBrowserItem bundle_uuid={self.props.bundle_uuid} key={item.name} index={item.name} type={item.type} size={item.size} size_str={item.size_str} updateFileBrowser={self.props.updateFileBrowser} currentWorkingDirectory={self.props.currentWorkingDirectory} />);
          });

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
              {bread_crumbs}
              <div className="panel-body">
                  {file_browser}
              </div>
          </div>
        </div>);
    }
});

var FileBrowserBreadCrumbs = React.createClass({
    breadCrumbClicked: function(path) {
      this.props.updateFileBrowser(path);
    },
    render: function() {
      var links = [];
      var splitDirs = this.props.currentWorkingDirectory.split('/');
      var currentDirectory = '';

      // Generate list of breadcrumbs separated by ' / '
      for (var i=0; i < splitDirs.length; i++) {
        if (i > 0)
          currentDirectory += '/';
        currentDirectory += splitDirs[i];
        links.push(<span key={splitDirs[i]} index={splitDirs[i]} onClick={this.breadCrumbClicked.bind(null, currentDirectory)}> / {splitDirs[i]}</span>);
      }

      return <div className="panel-heading">{links}</div>;
    }
});

var FileBrowserItem = React.createClass({
    browseToFolder: function(type) {
        this.props.updateFileBrowser(this.props.index);
    },
    render: function() {
        // Type can be 'file' or 'folder'
        var icon = "glyphicon-folder-open";
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
        if (this.props.hasOwnProperty('size_str'))
          size = this.props['size_str'];
        return (
            <tr>
                <td>
                    <div className={this.props.type} onClick={this.props.type != 'file' ? this.browseToFolder : null}>
                        <span className={icon} alt="More"></span>
                        <a href={this.props.type == 'file' ? file_link : null} target="_blank" className='sidepanel-file-viewer-contents'>{this.props.index}</a>
                        <span className="pull-right">{size}</span>
                    </div>
                </td>
            </tr>
        );
    }
});
