/** @jsx React.DOM */

/*
Main worksheet page, which displays information about a single worksheet.
Consists of three main components:
- action bar (web terminal)
- list of worksheets
- side panel
*/

var HOME_WORKSHEET = '/';

var Worksheet = React.createClass({
    getInitialState: function() {
        return {
            refresh: false,
            ws: new WorksheetContent(this.props.uuid),
            activeComponent: 'list',  // Where the focus is (action, list, or side_panel)
            editMode: false,  // Whether we're editing the worksheet
            showActionBar: true,  // Whether the action bar is shown
            focusIndex: -1, // Which worksheet items to be on (-1 is none)
            subFocusIndex: -1,  // For tables, which row in the table
            editorEnabled: false, // by default, editor is disabled
            editorCursorPosition: 1, // by default, editor starts on line 1
        };
    },
    _setfocusIndex: function(index) {
        this.setState({focusIndex: index});
    },
    _setWorksheetSubFocusIndex: function(index) {
        this.setState({subFocusIndex: index});
    },
    componentWillMount: function() {
        this.state.ws.fetch({async: false});
    },
    componentDidMount: function() {
        this.bindEvents();
        $('body').addClass('ws-interface');
        $.fn.editable.defaults.mode = 'inline';
        $('.editable-field').editable({
            send: 'always',
            type: 'text',
            params: function(params) {
              var data = {};
              var rawCommand = {}
              data['worksheet_uuid'] = this.state.ws.info.uuid;
              rawCommand['k'] = params['name'];
              rawCommand['v'] = params['value'];
              rawCommand['action'] = 'worksheet-edit';
              data['raw_command'] = rawCommand;
             return JSON.stringify(data);
            }.bind(this),
            success: function(response, newValue) {
                if(response.error){
                    return response.error;
                }
                this.state.ws.fetch({async: false});
                this.setState({refresh: !this.state.refresh});

            }.bind(this)
        });
    },
    componentWillUnmount: function() {
        this.unbindEvents();
    },
    bindEvents: function() {
    },
    unbindEvents: function() {
        // window.removeEventListener('keydown');
    },
    canEdit: function() {
        var info = this.state.ws.info;
        return info && info.edit_permission;
    },
    viewMode: function() {
        this.toggleEditMode(false);
    },
    discardChanges: function() {
        this.toggleEditMode(false, false);
    },
    editMode: function() {
        this.toggleEditMode(true);
    },
    handleActionBarFocus: function(event) {
        this.setState({activeComponent: 'action'});
        // just scroll to the top of the page.
        // Add the stop() to keep animation events from building up in the queue
        // See also scrollTo* methods
        $('#worksheet_panel').addClass('actionbar-focus');
        $('#command_line').data('resizing', null);
        $('body').stop(true).animate({scrollTop: 0}, 250);
    },
    handleActionBarBlur: function(event) {
        // explicitly close term because we're leaving the action bar
        // $('#command_line').terminal().focus(false);
        this.setState({activeComponent: 'list'});
        $('#command_line').data('resizing', null);
        $('#worksheet_panel').removeClass('actionbar-focus').removeAttr('style');
        $('#ws_search').removeAttr('style');
    },
    capture_keys: function() {
        Mousetrap.reset();  // reset, since we will call children, let's start fresh.

        if (this.state.activeComponent == 'action') {
            // no need for other keys, we have the action bar focused
            return;
        }

        // No keyboard shortcuts are active in edit mode
        if (this.state.editMode) {
            Mousetrap.bind(['ctrl+enter', "meta+enter"], function(e) {
                this.toggleEditMode();
            }.bind(this));
            return;
        }

        Mousetrap.bind(['?'], function(e) {
            $('#glossaryModal').modal('show');
        });

        Mousetrap.bind(['esc'], function(e) {
            if ($('#glossaryModal').hasClass('in')) {
                $('#glossaryModal').modal('hide');
            }
        });

        Mousetrap.bind(['shift+r'], function(e) {
            this.refreshWorksheet();
            return false;
        }.bind(this));

        // Show/hide web terminal
        Mousetrap.bind(['shift+c'], function(e) {
            this.toggleActionBar();
        }.bind(this));

        // Focus on web terminal (action bar)
        Mousetrap.bind(['c'], function(e) {
            this.focusActionBar();
        }.bind(this));

        // Toggle edit mode
        Mousetrap.bind(['e'], function(e) {
            this.toggleEditMode();
            return false;
        }.bind(this));
    },
    toggleEditMode: function(editMode, saveChanges) {
        if (editMode === undefined)
          editMode = !this.state.editMode;  // Toggle by default

        if (typeof saveChanges === 'undefined')
            saveChanges = true;

        if (!editMode) {
          // Going out of raw mode - save the worksheet.
          if (this.canEdit()) {
            // TODO: This should be done by the editing control in WorksheetItemList
            var editor = ace.edit('worksheet-editor');
            if (saveChanges) {
                this.state.ws.info.raw = editor.getValue().split('\n');
            }
            this.setState({editMode: editMode, editorEnabled: false, editorCursorPosition: editor.getCursorPosition().row});  // Needs to be after getting the raw contents
            this.saveAndUpdateWorksheet(true);
          } else {
            // Not allowed to save worksheet (shouldn't happen).
          }
        } else {
          // Go into edit mode.
          this.setState({editMode: editMode});  // Needs to be before focusing
          $("#worksheet-editor").focus();
        }
    },
    componentDidUpdate: function(props,state,root) {
        try {
            if (this.state.editMode && !this.state.editorEnabled) {
                this.setState({editorEnabled: true});
                var editor = ace.edit('worksheet-editor');
                editor.$blockScrolling = Infinity;
                editor.session.setUseWrapMode(false);
                editor.setShowPrintMargin(false);
                editor.session.setMode('ace/mode/markdown');
                editor.commands.addCommand({
                    name: 'save',
                    bindKey: {win: 'Ctrl-Enter', mac: 'Command-Enter'},
                    exec: function(editor) {
                        this.toggleEditMode();
                    }.bind(this),
                    readOnly: true
                });
                editor.focus();

                var index = this.state.focusIndex + ',' + this.state.subFocusIndex;
                var defaultIndex = this.state.focusIndex + ',' + '-1';
                var cursorRowPosition = this.state.ws.info.interpreted_raw_map[index] || this.state.ws.info.interpreted_raw_map[defaultIndex];
                if (cursorRowPosition === undefined) {
                    console.error("Cannot find element with focusIndex: %d subFocusIndex: %d in interpreted_raw_map", this.state.focusIndex, this.state.subFocusIndex);
                    return;
                }
                var cursorColumnPosition = editor.session.getLine(cursorRowPosition).length;
                editor.gotoLine(cursorRowPosition + 1, cursorColumnPosition);
                editor.renderer.scrollToRow(cursorRowPosition);
            }
        }
        catch(error) {
        }
    },
    toggleActionBar: function() {
        this.setState({showActionBar: !this.state.showActionBar});
    },
    focusActionBar: function() {
        this.setState({activeComponent: 'action'});
        this.setState({showActionBar: true});
        $('#command_line').terminal().focus();
    },
    refreshWorksheet: function() {
        $('#update_progress').show();
        this.setState({updating: true});
        this.state.ws.fetch({
            success: function(data) {
                $('#update_progress, #worksheet-message').hide();
                $('#worksheet_content').show();
                this.setState({updating:false});
                var focusIndex = this.state.ws.info.raw_interpreted_map[this.state.editorCursorPosition] || [0, -1];
                if (focusIndex[0] >= this.state.ws.info.items.length) {
                    // maps empty trailing lines to the last interpreted_item
                    focusIndex[0] = this.state.ws.info.items.length - 1;
                    this.refs.list.setFocus(focusIndex[0], 'end');
                }
                else {
                    this.refs.list.setFocus(focusIndex[0], focusIndex[1]);
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.state.ws.url, status, err);
                this.setState({updating:false});

                if (xhr.status == 404) {
                    $("#worksheet-message").html('Worksheet was not found.').addClass('alert-danger alert');
                } else {
                    var error_msg = xhr.responseJSON.error;
                    if (error_msg) err = error_msg;
                    $("#worksheet-message").html('Worksheet error: ' + err).addClass('alert-danger alert');
                }
                $('#update_progress').hide();
                $('#worksheet_container').hide();
            }.bind(this)
        });
    },

    openWorksheet: function(uuid) {
      window.location = '/worksheets/' + uuid + '/';
      // TODO: need to update the URL in the action bar (need to probably
      // switch over to #), and make sure everything gets updated.
      //this.setState({ws: new WorksheetContent(uuid)});
    },

    saveAndUpdateWorksheet: function(from_raw) {
        $("#worksheet-message").hide();
        // does a save and a update
        this.setState({updating: true});
        this.state.ws.saveWorksheet({
            success: function(data) {
                this.setState({updating:false});
                if ('error' in data) { // TEMP REMOVE FDC
                    $('#update_progress').hide();
                    $('#save_error').show();
                    $("#worksheet-message").html("A save error occurred: <em>" + data.error + "</em> <br /> Please try refreshing the page or saving again").addClass('alert-danger alert').show();
                    if (from_raw) {
                        this.toggleEditMode(true);
                    }
                }else {
                    this.refreshWorksheet();
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(xhr, status, err);
                this.setState({updating: false});
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-danger alert').show();
                } else if (xhr.status == 401) {
                    $("#worksheet-message").html("You do not have permission to edit this worksheet.").addClass('alert-danger alert').show();
                } else {
                    $("#worksheet-message").html('Saving failed: ' + err).addClass('alert-danger alert').show();
                }
            }
        });
    },

    // Go to the home worksheet
    myHomeWorksheet: function() {
      // Make sure the worksheet exists
      this.refs.action.executeCommand(['cl', 'new', '-p', HOME_WORKSHEET]).then(function() {
        this.refs.action.executeCommand(['cl', 'work', HOME_WORKSHEET]);
      }.bind(this));
    },

    uploadBundle: function() {
      this.refs.action.executeCommand(['cl', 'upload']);
    },

    render: function() {
        //console.log('WorksheetInterface.render');
        this.capture_keys();
        var info = this.state.ws.info;
        var rawWorksheet = info && info.raw.join('\n');
        var editPermission = info && info.edit_permission;
        var canEdit = this.canEdit() && this.state.editMode;

        var searchClassName     = !this.state.showActionBar ? 'search-hidden' : '';
        var editableClassName   = canEdit ? 'editable' : '';
        var viewClass           = !canEdit && !this.state.editMode ? 'active' : '';
        var rawClass            = this.state.editMode ? 'active' : '';

        var sourceStr = editPermission ? 'Edit source' : 'View source';
        var editFeatures = (
            <div className="edit-features">
                <label>Mode:</label>
                <div className="btn-group">
                    <button className={viewClass} onClick={this.viewMode}>View</button>
                    <button className={rawClass} onClick={this.editMode}>{sourceStr}</button>
                </div>
            </div>
        );

        var editModeFeatures = (
            <div className="edit-features">
                <label>Mode:</label>
                <div className="btn-group">
                    <button className={viewClass} onClick={this.viewMode}>Save</button>
                    <button className={viewClass} onClick={this.discardChanges}>Discard</button>
                </div>
            </div>
        );

        if (info && info.items.length) {
            // Non-empty worksheet
        } else {
            $('.empty-worksheet').fadeIn();
        }

        var raw_display = <div>
            Press ctrl-enter to save.
            See <a href="https://github.com/codalab/codalab/wiki/User_Worksheet-Markdown">markdown syntax</a>.
            <div id='worksheet-editor'>{rawWorksheet}</div>
            </div>;

        var action_bar_display = (
                <WorksheetActionBar
                    ref={"action"}
                    canEdit={this.canEdit()}
                    ws={this.state.ws}
                    handleFocus={this.handleActionBarFocus}
                    handleBlur={this.handleActionBarBlur}
                    active={this.state.activeComponent == 'action'}
                    show={this.state.showActionBar}
                    focusIndex={this.state.focusIndex}
                    subFocusIndex={this.state.subFocusIndex}
                    refreshWorksheet={this.refreshWorksheet}
                    openWorksheet={this.openWorksheet}
                    editMode={this.editMode}
                />
            );

        var items_display = (
                <WorksheetItemList
                    ws={this.state.ws}
                    ref={"list"}
                    active={this.state.activeComponent == 'list'}
                    canEdit={canEdit}
                    updateWorksheetFocusIndex={this._setfocusIndex}
                    updateWorksheetSubFocusIndex={this._setWorksheetSubFocusIndex}
                    refreshWorksheet={this.refreshWorksheet}
                    focusActionBar={this.focusActionBar}
                />
            );

        var worksheet_side_panel = (
                <WorksheetSidePanel
                    ws={this.state.ws}
                    ref={"side_panel"}
                    active={this.state.activeComponent == 'side_panel'}
                    focusIndex={this.state.focusIndex}
                    subFocusIndex={this.state.subFocusIndex}
                    myHomeWorksheet={this.myHomeWorksheet}
                    uploadBundle={this.uploadBundle}
                    bundleMetadataChanged={this.refreshWorksheet}
                />
            );

        var upload_modal = (
                <UploadModal
                    ws={this.state.ws}
                    ref={"modal"}
                    refreshWorksheet={this.refreshWorksheet}
                />
            );

        var worksheet_display = this.state.editMode ? raw_display : items_display;
        var editButtons = this.state.editMode ? editModeFeatures: editFeatures;
        return (
            <div id="worksheet" className={searchClassName}>
                {action_bar_display}
                <div id="worksheet_panel" className="actionbar-focus">
                    {worksheet_side_panel}
                    <div className="ws-container">
                        <div className="container-fluid">
                            <div id="worksheet_content" className={editableClassName}>
                                <div className="header-row">
                                    <div className="row">
                                        <h4 className='worksheet-title'><a href="#" id='title' className='editable-field' data-value={info && info.title} data-type="text" data-url="/api/worksheets/command/">{info && info.title}</a></h4>
                                        <div className="col-sm-6 col-md-8">
                                            <div className="worksheet-name">
                                                <div className="worksheet-detail"><b>name: </b><a href="#" id='name' className='editable-field' data-value={info && info.name} data-type="text" data-url="/api/worksheets/command/">{info && info.name}</a></div>
                                                <div className="worksheet-detail"><b>uuid: </b>{info && info.uuid}</div>
                                                <div className="worksheet-detail"><b>owner: </b>{info && info.owner_name}</div>
                                                <div className="worksheet-detail"><b>permissions: </b>{info && render_permissions(info)}</div>
                                            </div>
                                        </div>
                                        <div className="col-sm-6 col-md-4">
                                            <div className="controls">
                                                <a href="#" data-toggle="modal" data-target="#glossaryModal" className="glossary-link"><code>?</code> Keyboard Shortcuts</a>
                                                {editButtons}
                                            </div>
                                        </div>
                                    </div>
                                    <hr />
                                </div>
                                {worksheet_display}
                            </div>
                        </div>
                        {upload_modal}
                    </div>
                </div>
                <div id="dragbar_vertical" className="dragbar"></div>
            </div>
        )
    }
});
