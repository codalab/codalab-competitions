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
    componentDidMount: function(){
        // https://github.com/jcubic/jquery.terminal
        var self = this;
        $('#dragbar_horizontal').mousedown(function(e){
            self.resizePanel(e);
        });

        var tab_count = 0;
        var paused = false;
        var term = $('#command_line').terminal(
            // 1st argument is handle commands entered
            function(entered, term) {
                // lets clean and cut up what the enterd
                var command = entered.trim(); // cut of any extra whitespace
                var args;
                var last;
                args = command.split(' '); //command.get_command().split(' ')
                command = args[1]; // the command they enterd, minus cl
                args = args.splice(1, args.length-1)
                last = args[args.length-1];

                // console.log("entered command");
                // console.log(command);
                // console.log(args);
                // console.log("******* PARSE AND RUN *********");

                if(typeof(command) == 'undefined'){  // no command
                    term.echo("<span style='color:red'>Error: not a CodaLab command. Try 'cl help'.</a>", {raw: true});
                    return;
                }

                var ws_action_command = ws_actions.checkAndReturnCommand(command);
                if(typeof(ws_action_command) == 'undefined'){  // no command
                    // didnt find anything take all extra text throw it in cl command and hope for the best
                    ws_action_command = ws_actions.checkAndReturnCommand('cl');
                }
                var executefn = ws_action_command.executefn(args, term, self)
                // lets lock the term, do the command enterd and unlock stops the user from typing
                // executefn is a promise
                term.pause();
                paused = true;
                executefn.always(function (data) {
                    term.resume();
                    paused = false;
                    // console.log(data);
                });


            },
            // 2nd is helpers and options. Take note of keydown for tab completion
            {
                greetings: '[CodaLab web terminal] Press \'c\' to focus, ESC to unfocus.  Type \'cl help\' to see all commands.',
                name: 'command_line',
                height: ACTIONBAR_MINIMIZE_HEIGHT,
                // width: 700,
                prompt: '> ',
                history: true,
                keydown: function(event, terminal){
                    if (event.keyCode === 27) { //esc
                        terminal.focus(false);
                    }
                },
                onBlur: function(term){
                    if(term.data('resizing')){
                        self.props.handleFocus();
                        return false;
                    }
                    term.resize(term.width(), ACTIONBAR_MINIMIZE_HEIGHT);
                    self.props.handleBlur();
                },
                onFocus: function(term){
                    if(!term.data('resizing')){
                        term.resize(term.width(), ACTIONBAR_DRAGHEIGHT);
                    }
                    self.props.handleFocus();
                },
                completion: function(terminal, lastToken, callback) {
                    var command = terminal.get_command();
                    console.log(lastToken, command);

                    ws_actions.completeCommand(command).then(function(completions) {
                        callback(completions);
                    });
                }
            }
        );
        //turn off focus by default
        term.focus(false);

    },
    current_focus: function(){  //get current focus of the user in the worksheet item list
        var focus = '';
        if(this.props.focusIndex > -1){
            focus = ws_obj.state.items[this.props.focusIndex].state;
            if(focus.mode == "markup" || focus.mode == "worksheet" || focus.mode == "search"){
                this.focustype = 'worksheet';
                if(focus.mode != "worksheet"){ // are we not looking at a sub worksheet
                     //for lets default it back to the main worksheet info
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
