/** @jsx React.DOM */

/*
Main worksheet page, which displays information about a single worksheet.
Consists of three main components:
- action bar (web terminal)
- list of worksheets
- side panel
*/

var keyMap = {
    13: "enter",
    27: "esc",
    69: "e",
    70: "f",
    38: "up",
    40: "down",
    65: "a",
    66: "b",
    68: "d",
    73: "i",
    74: "j",
    75: "k",
    79: "o",
    88: "x",
    191: "fslash"
};

var Worksheet = React.createClass({
    getInitialState: function() {
        return {
            refresh: false,
            ws: new WorksheetContent(this.props.url),
            activeComponent: 'list',  // Where the focus is (action, list, or side_panel)
            editMode: false,  // Whether we're editing the worksheet
            showActionBar: true,  // Whether the action bar is shown
            focusIndex: -1, // Which worksheet items to be on (-1 is none)
            subFocusIndex: -1,  // For tables, which row in the table
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
              data['worksheet_uuid'] = this.state.ws.state.uuid;
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
                this.state.ws.fetch({async:false});
                this.setState({refresh:!this.state.refresh});

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
        return this.state.ws.getState().edit_permission;
    },
    viewMode: function() {
        this.toggleEditMode(false);
    },
    editMode: function() {
        this.toggleEditMode(true);
    },
    handleActionBarFocus: function(event) {
        this.setState({activeComponent:'action'});
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
        this.setState({activeComponent:'list'});
        $('#command_line').data('resizing', null);
        $('#worksheet_panel').removeClass('actionbar-focus').removeAttr('style');
        $('#ws_search').removeAttr('style');
    },
    capture_keys: function() {
        Mousetrap.reset();  // reset, since we will call children, let's start fresh.

        var activeComponent = this.refs[this.state.activeComponent];
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

        Mousetrap.bind(['shift+r',], function(e) {
            this.refreshWorksheet();
            return false;
        }.bind(this));

        // Show/hide web terminal
        Mousetrap.bind(['shift+c'], function(e) {
            this.toggleActionBar();
        }.bind(this));

        // Focus on web terminal (action bar)
        Mousetrap.bind(['c'], function(e) {
            this.showActionBar();
            this.setState({activeComponent: 'action'});
            $('#command_line').terminal().focus();
        }.bind(this));

        // Toggle edit mode
        Mousetrap.bind(['e'], function(e) {
            this.toggleEditMode();
            return false;
        }.bind(this));
    },
    toggleEditMode: function(editMode) {
        if (typeof(editMode) == 'undefined')
          editMode = !this.state.editMode;  // Toggle by default

        if (!editMode) {
          // Going out of raw mode - save the worksheet.
          if (this.canEdit()) {
            // TODO: grab val the react way
            this.state.ws.state.raw = $("#raw-textarea").val().split('\n');
            this.setState({editMode: editMode});  // Needs to be after getting the raw contents
            this.saveAndUpdateWorksheet(true);
          } else {
            // Not allowed to save worksheet.
          }
        } else {
          // Go into edit mode.
          this.setState({editMode: editMode});  // Needs to be before focusing
          this.setState({activeComponent: 'textarea'});
          // TODO: set cursor intelligently rather than just leaving it at the beginning.
          $("#raw-textarea").focus();
        }
    },
    toggleActionBar: function() {
        this.setState({showActionBar: !this.state.showActionBar});
    },
    showActionBar: function() {
        this.setState({showActionBar: true});
    },
    hideActionBar: function() {
        this.setState({showActionBar: false});
    },
    refreshWorksheet: function() {
        $('#update_progress').show();
        this.setState({updating: true});
        this.state.ws.fetch({
            success: function(data) {
                if (this.isMounted()) {
                    // TODO: change this so that it doesn't modify refs.
                    this.refs.list.setState({worksheet: this.state.ws.getState()});
                }
                $('#update_progress, #worksheet-message').hide();
                $('#worksheet_content').show();
                if (this.state.ws.getState().items.length === 0) {
                    this.refs.list.resetFocusIndex();
                }
                this.setState({updating:false});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.state.ws.url, status, err);
                this.setState({updating:false});

                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-danger alert');
                } else {
                    var error_msg = xhr.responseJSON.error;
                    if (error_msg) err = error_msg;
                    $("#worksheet-message").html("An error occurred: <code>'" + status + "' " + err + " (" + xhr.status + ")</code>. Please try refreshing the page.").addClass('alert-danger alert');
                }
                $('#update_progress').hide();
                $('#worksheet_container').hide();
            }.bind(this)
        });
    },
    saveAndUpdateWorksheet: function(from_raw) {
        $("#worksheet-message").hide();
        // does a save and a update
        this.setState({updating:true});
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
                this.setState({updating:false});
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-danger alert').show();
                } else if (xhr.status == 401) {
                    $("#worksheet-message").html("You do not have permission to edit this worksheet.").addClass('alert-danger alert').show();
                } else {
                    $("#worksheet-message").html("A save error occurred: <em>" + err.string() + "</em> <br /> Please try refreshing the page or saving again.").addClass('alert-danger alert').show();
                }
            }
        });
    },

    // Go to the home worksheet
    myHomeWorksheet: function() {
      // Make sure the worksheet exists (
      this.refs.action.executeCommand(['cl', 'new', '-p', home_worksheet_name]).then(function() {
        this.refs.action.executeCommand(['cl', 'work', home_worksheet_name]);
      }.bind(this));
    },

    uploadBundle: function() {
      this.refs.action.executeCommand(['cl', 'upload', 'dataset']);
    },

    render: function() {
        //console.log('WorksheetInterface.render');
        this.capture_keys();
        var rawWorksheet = this.state.ws.getRaw();
        var editPermission = this.state.ws.getState().edit_permission;
        var canEdit = this.canEdit() && this.state.editMode;
        var checkboxEnabled = this.state.checkboxEnabled;

        var searchClassName     = !this.state.showActionBar ? 'search-hidden' : '';
        var editableClassName   = canEdit ? 'editable' : '';
        var viewClass           = !canEdit && !this.state.editMode ? 'active' : '';
        var editClass           = canEdit && !this.state.editMode ? 'active' : '';
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

        if (this.state.ws.state.items.length) {
            // Non-empty worksheet
        } else {
            $('.empty-worksheet').fadeIn();
        }

        // http://facebook.github.io/react/docs/forms.html#why-textarea-value
        var raw_display = <div>
            Press ctrl-enter to save.
            <textarea
                id="raw-textarea"
                ws={this.state.ws}
                className="form-control mousetrap"
                defaultValue={rawWorksheet.content}
                rows={30}
                ref="textarea"
            />
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
                                        <h4 className='worksheet-title'><a href="#" id='title' className='editable-field' data-value={this.state.ws.state.title} data-type="text" data-url="/api/worksheets/command/">{this.state.ws.state.title}</a></h4>
                                        <div className="col-sm-6 col-md-8">
                                            <div className="worksheet-name">
                                                <div className="worksheet-detail"><b>name: </b><a href="#" id='name' className='editable-field' data-value={this.state.ws.state.name} data-type="text" data-url="/api/worksheets/command/">{this.state.ws.state.name}</a></div>
                                                <div className="worksheet-detail"><b>uuid: </b>{this.state.ws.state.uuid}</div>
                                                <div className="worksheet-detail"><b>owner: </b>{this.state.ws.state.owner_name}</div>
                                                <div className="worksheet-detail"><b>permissions: </b>{render_permissions(this.state.ws.state)}</div>
                                            </div>
                                        </div>
                                        <div className="col-sm-6 col-md-4">
                                            <div className="controls">
                                                <a href="#" data-toggle="modal" data-target="#glossaryModal" className="glossary-link"><code>?</code> Keyboard Shortcuts</a>
                                                {editFeatures}
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
