/** @jsx React.DOM */

var WorksheetActionBar = React.createClass({
    // ********************************************
    // please see ws_actions the goal of WorksheetSearch
    // is to be a generic front end for all actions and select2
    // for all new actions please add in ws_actions.
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

                console.log("entered command");
                console.log(command);
                console.log(args);
                console.log("******* PARSE AND RUN *********");

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
                greetings: 'Worksheet Interface: A codalab cli lite interface. Please enter a command or help to see list of commands',
                name: 'command_line',
                height: 45,
                width: 700,
                prompt: '> ',
                history: true,
                keydown: function(event, terminal){
                    if(event.keyCode == 27){ //esc
                        terminal.focus(false);
                    }
                    if (event.keyCode == 9){ //Tab
                        ++tab_count;
                        var command;  // the ws_action command
                        var entered = term.get_command();
                        var args = entered.split(' '); //term.get_command().split(' ')
                        var last = args[args.length-1];
                        console.log('completion')
                        console.log(entered);
                        console.log(args);
                        console.log(last);
                        console.log('-------------------');

                        if(args[0] != 'cl'){ // shove in cl, just some helpful sugar
                            term.set_command('cl ' + entered);
                        }

                        var fetch_auto_complete_list;
                        if(args.length > 2 && args[1]){
                            command = ws_actions.checkAndReturnCommand(args[1]);
                            if(command){
                                fetch_auto_complete_list = command.autocomplete(args)
                                if(!paused){
                                    term.echo('fetching list ....');
                                }
                            }else{ // nothing found just return an empty list
                                var empty_defer = jQuery.Deferred();
                                empty_defer.resolve([])
                                fetch_auto_complete_list = empty_defer.promise()
                            }
                        }else{
                            fetch_auto_complete_list = ws_actions.getCommands(self.props.canEdit, true);
                        }

                        // lets lock the term, do the lookup
                        // fetch_auto_complete_list is a promise
                        term.pause();
                        paused = true;
                        fetch_auto_complete_list.always(function(auto_complete_list){
                            term.resume(); // unblock since we are doing stuff to the term
                            paused = false;
                            var regex = new RegExp('^' + $.terminal.escape_regex(last));
                            var matched = [];
                            var matched_pos = []; // autocomplete will sometimes return array of objects, which ones match which

                            // push all found auto_complete_list in to matched for more tricks later
                            for (var i=auto_complete_list.length; i--;) {
                                var is_obj = false
                                var test_match_text = auto_complete_list[i]
                                // can be returned as array or an obj {'text': auto-coplete text , "display": fancy display text }
                                if(typeof(test_match_text) == "object"){
                                    test_match_text = auto_complete_list[i].text;
                                    is_obj = true
                                }
                                // check the text and push it to the list
                                if(regex.test(test_match_text)) {
                                    matched.push(test_match_text);
                                    if(is_obj){
                                        is_obj  // so we can match it later
                                        matched_pos.push(i);
                                    }

                                }
                            }
                            // now for the insert or print out
                            if(matched.length === 1){ // we found an exact match, just put in in the term
                                term.insert(matched[0].replace(regex, '') + ' ');
                            }else if (matched.length > 1) {
                                if (tab_count >= 2) {
                                    if(matched_pos.length > 0){
                                        // we have fancy output sync back up with auto_coplete and print it
                                        for(var i=matched_pos.length; i--;) {
                                            // todo : pre and post display?
                                            var display = auto_complete_list[matched_pos[i]].display
                                            term.echo(display, {raw: true});
                                        }
                                    }else{ // nothing fancy just spit it out with a tab
                                        term.echo(matched.join('\t'));
                                    }


                                    tab_count = 0;
                                } else {
                                    // lets find what matches and fill in as much as we can if not a full match
                                    // example: test123 and testabc are comp words, type `te`, hit tab,
                                    //          we can complete to `test` based on matchs
                                    var found = false;
                                    var found_index;
                                    var j;
                                    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/label
                                    loop: // dont stop till found, because it is guaranteed from before, thanks matched
                                        for (j=last.length; j<matched[0].length; ++j) {
                                            for (i=1; i<matched.length; ++i) {
                                                if (matched[0].charAt(j) !== matched[i].charAt(j)) {
                                                    break loop;
                                                }
                                            }
                                            found = true;
                                        }
                                        if (found) {
                                            term.insert(matched[0].slice(0, j).replace(regex, ''));
                                        }
                                }// end of if tab_count
                            } // end if else if
                        }); // end of then

                        return false; // dont really hit tab
                    }else{// end if 9 aka tab, reset the counter
                        tab_count = 0;
                    }

                },
                onBlur: function(term){
                    term.resize(term.width(), 45);
                    self.props.handleBlur();
                },
                onFocus: function(term){
                    term.resize(term.width(), 170);
                    self.props.handleFocus();
                },
            }
        );
        //turn off focus by default
        term.focus(false);
        term.focus(true); // todo remove

    },
    componentWillUnmount: function(){},
    componentDidUpdate: function(){},
    resizePanel: function(e){
        var worksheet = $('#worksheet');
        var actionbar = $('#ws_search');
        var topOffset = actionbar.offset().top;
        var worksheetHeight = $('#worksheet').height();
        var worksheetPanel = $('#worksheet_panel');
        var commandLine = $('#command_line');
        $(document).mousemove(function(e){
            e.preventDefault();
            var actionbarHeight = e.pageY - topOffset;
            var actionbarHeightPercentage = actionbarHeight / worksheetHeight * 100;
            if(35 < actionbarHeight && actionbarHeightPercentage < 90){ // minimum height: 35px; maximum height: 90% of worksheet height
                worksheetPanel.removeClass('actionbar-focus').addClass('actionbar-resized');;
                actionbar.css('height', actionbarHeight);
                $('#command_line').terminal().resize(commandLine.width(), actionbarHeight - 20);
                worksheetPanel.css('padding-top', actionbarHeight);
            }
        });
    },
    render: function(){
        return (
            <div id="ws_search">
                <div className="container">
                    <div id="command_line"></div>
                </div>
                <div id="dragbar_horizontal" className="dragbar"></div>
            </div>
        )
    }
});
