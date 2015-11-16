/** @jsx React.DOM */

var ACTIONBAR_MINIMIZE_HEIGHT = 25;
var ACTIONBAR_DRAGHEIGHT = 170

var WorksheetActionBar = React.createClass({
    focustype: 'worksheet', // keep track of what the user has focused on worksheet item
    // ********************************************
    // please see ws_actions The goal of WorksheetActionbar
    // is to be a generic front end link for all actions and jqueryterminal
    // for all new actions please add in ws_actions.js
    // ********************************************
    componentDidMount: function() {
        var self = this;
        $('#dragbar_horizontal').mousedown(function(e){
            self.resizePanel(e);
        });

        // See JQuery Terminal API reference for more info about this plugin:
        // http://terminal.jcubic.pl/api_reference.php
        var term = $('#command_line').terminal(function(command, terminal) {
            terminal.pause();
            self.executeCommand(command).then(function(data) {
                if (data.output) {
                    terminal.echo(data.output);
                }

                if (data.exception) {
                    terminal.error(data.exception);
                }

                // Patch in hyperlinks to bundles
                if (data.structured_result && data.structured_result.refs) {
                    self.renderHyperlinks(data.structured_result.refs);
                }
            }).fail(function(error) {
                terminal.error("Unexpected error when executing request.");
            }).always(function() {
                terminal.resume();
                self.props.refreshWorksheet();
            });
        }, {
            greetings: "[CodaLab web terminal] Press 'c' to focus, ESC to unfocus.  Type 'cl help' to see all commands.",
            name: 'command_line',
            height: ACTIONBAR_MINIMIZE_HEIGHT,
            prompt: '> ',
            history: true,
            keydown: function(event, terminal) {
                if (event.keyCode === 27) { // esc
                    terminal.focus(false);
                }
            },
            onBlur: function(term) {
                if (term.data('resizing')) {
                    self.props.handleFocus();
                    return false;
                }
                term.resize(term.width(), ACTIONBAR_MINIMIZE_HEIGHT);
                self.props.handleBlur();
            },
            onFocus: function(term) {
                if (!term.data('resizing')) {
                    term.resize(term.width(), ACTIONBAR_DRAGHEIGHT);
                }
                self.props.handleFocus();
            },
            completion: function(terminal, lastToken, callback) {
                var command = terminal.get_command();

                self.completeCommand(command).then(function(completions) {
                    callback(completions);
                });
            }
        });

        // Start with terminal focus off.
        term.focus(false);
    },
    renderHyperlinks: function(references) {
        Object.keys(references).forEach(function(key) {
            $(".terminal-output div div:contains(" + key + ")").html(function(idx, html) {
                var hyperlink_info = references[key];
                if (hyperlink_info.uuid) {
                    if (hyperlink_info.type === 'bundle' || hyperlink_info.type === 'worksheet') {
                        var link = '/' + hyperlink_info['type'] + 's/' + hyperlink_info['uuid'];
                        return html.replace(key, "<a href=" + link + " target='_blank'>" + key + "</a>");
                    } else {
                        console.warn("Couldn't create hyperlink for ", hyperlink_info.uuid, " . Type is neither 'worksheet' nor 'bundle'");
                    }
                } else {
                    console.warn("Complete uuid not available for ", key, " to create hyperlink");
                }
            });
        });
    },
    doUIAction: function(action, parameter) {
        // Possible actions and parameters:
        // 'openWorksheet', WORKSHEET_UUID  => load worksheet
        // 'setEditMode', true|false        => set edit mode
        // 'openBundle', BUNDLE_UUID]       => load bundle info in new tab
        // 'upload', null                   => open upload modal
        var self = this;
        ({
            openWorksheet: function(uuid) {
                self.props.openWorksheet(uuid);
            },
            setEditMode: function(editMode) {
                self.props.editMode();
            },
            openBundle: function(uuid) {
                window.open('/bundles/' + uuid + '/', '_blank');
            },
            upload: function() {
                $("#ws-bundle-upload").modal();
            }
        })[action](parameter);
    },
    executeCommand: function(command) {
        var self = this;

        // returns a jQuery Promise
        return $.ajax({
            type: 'POST',
            cache: false,
            url: '/api/worksheets/command/',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'worksheet_uuid': this.props.ws.info.uuid,
                'command': command
            })
        }).done(function(data) {
            // data := {
            //     structured_result: { ... },
            //     output: string,
            //     exception: string
            // }

            // The bundle service can respond with instructions back to the UI.
            // These come in the form of an array of 2-arrays, with the first element
            // representing the type of action, and the second element parameterizing
            // that action.
            if (data.structured_result && data.structured_result.ui_actions) {
                _.each(data.structured_result.ui_actions, function(action) {
                    self.doUIAction(action[0], action[1]);
                });
            }
        }).fail(function(jqXHR, status, error){
            // Some exception occurred outside of the CLI
            console.error("CLI command request failed:");
            console.error("Status code:", status);
            console.error("Error:", error);
            return error;
        });
    },
    completeCommand: function(command) {
        var deferred = jQuery.Deferred();
        $.ajax({
            type:'POST',
            cache: false,
            url:'/api/worksheets/command/',
            contentType:"application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'worksheet_uuid': this.props.ws.info.uuid,
                'command': command,
                'autocomplete': true,
            }),
            success: function(data, status, jqXHR) {
                deferred.resolve(data.completions);
            },
            error: function(jqHXR, status, error) {
                console.error(error);
                deferred.reject();
            }
        });
        return deferred.promise();
    },
    current_focus: function(){  //get current focus of the user in the worksheet item list
        var focus = '';
        if(this.props.focusIndex > -1){
            focus = this.props.ws.info.items[this.props.focusIndex];
            if(focus.mode == "markup" || focus.mode == "worksheet" || focus.mode == "search"){
                this.focustype = 'worksheet';
                if(focus.mode != "worksheet"){ // are we not looking at a sub worksheet
                     //for lets default it back to the main worksheet info
                     focus = this.props.ws.info;
                }
            }else{
                this.focustype = 'bundle';
            }// end of if focus.modes
        }else{// there is no focus index, just show the worksheet infomation
            focus = this.props.ws.info;
            this.focustype = 'worksheet';
        }
        return  focus;
    },
    componentWillUnmount: function(){},
    componentDidUpdate: function(){},
    resizePanel: function(e){
        var actionbar = $('#ws_search');
        var topOffset = actionbar.offset().top;
        var worksheetHeight = $('#worksheet').height();
        var worksheetPanel = $('#worksheet_panel');
        var commandLine = $('#command_line');
        $(document).mousemove(function(e){
            e.preventDefault();
            $('#command_line').data('resizing', 'true');
            var actionbarHeight = e.pageY - topOffset;
            var actionbarHeightPercentage = actionbarHeight / worksheetHeight * 100;
            if(65 < actionbarHeight && actionbarHeightPercentage < 90){ // minimum height: 65px; maximum height: 90% of worksheet height
                worksheetPanel.removeClass('actionbar-focus').addClass('actionbar-resized');;
                actionbar.css('height', actionbarHeight);
                ACTIONBAR_DRAGHEIGHT = actionbarHeight - 20
                commandLine.terminal().resize(commandLine.width(), ACTIONBAR_DRAGHEIGHT);
                worksheetPanel.css('padding-top', actionbarHeight);
            }
        });
    },
    render: function(){
        return (
            <div id="ws_search">
                <div className="">
                    <div id="command_line"></div>
                </div>
                <div id="dragbar_horizontal" className="dragbar"></div>
            </div>
        )
    }
});
