// Singleton class to manage actions triggered by the general search bar
var WorksheetActions =  function() {
    function formatHelp(usage, description) {
      return usage + ' : ' + description;
    }
    var bundleKeywordsHelp = 'Bundle keywords (example: test name=nlp.* type=run state=running .mine .last ...)';
    var worksheetKeywordsHelp = 'Worksheet keywords (example: test name=nlp.* .mine .last ...)';
    var displayError = function(jqHXR, status){
        error = jqHXR.responseJSON['error'];
        $("#worksheet-message").html("Action bar error: " + error).addClass('alert-danger alert').show();
        console.error(status + ': ' + error);
    }

    function WorksheetActions() {
        this.not_implemented_commands = [
        // this is a list of commands that are no front end implmented but we sill want to show
        // for action bar autocomplete
            'help',
            'upload',
            'make',
            'run',
            // 'detach',
            // 'rm',
            'search',
            'ls',
            // 'info', // overrode see below
            // 'cat',
            // 'wait',
            'cp',
            'mimic',
            // 'macro',
            'kill',
            // Commands for worksheets:
            // 'new',  // overrode see below
            // 'add',  // overrode see below
            // 'work', // overrode see below
            'wadd',
            'wrm',
            'wls',
            'wcp',
            // Commands for groups and permissions:
            'gls',
            'gnew',
            'grm',
            'ginfo',
            'uadd',
            'urm',
            'perm',
            'wperm',
            'chown',
        ];

        // If we override a command, sometimes we want to fall back to 'cl' depending on what the arguments are.
        var self = this;
        function cl(options, term, action_bar) {
          self.commands['cl'].executefn(options, term, action_bar);
        }
        this.temp_holder = undefined, // used for other temp info from the aciton bar. Can be a multitude of things, alway reset to undefined.
        this.commands = {
            // Dictionary of terms that can be entered and acted
            // and the names of functions they call.
            // ------------------------------------
            // Example (* starred are required)
            // 'commandname'{  // what the user enters
            //  *  executefn: a promise function that happens when they hit enter
            //  *  edit_enabled: is this a command that is only allowed when able to edit
            //  *  autocomplete: a promise function that returns either a dict {"test" : autocompletetext, "display": displaytet}
            //                   or an array of just things you wish to match vs what the user has typed
            // }
            // ------------------------------------
            'cl': { // default lets just run abrary commands commands fall back to this if no other command is found
                helpText: formatHelp('cl <command>', 'run CLI command'),
                minimumInputLength: 0,
                edit_enabled: false,
                executefn: function(options, term, action_bar){ // is a promise must resolve and return a promise
                    var defer = jQuery.Deferred();
                    if(options.length) {
                        options = options.join(' ');
                        worksheet_uuid = ws_obj.state.uuid;
                        var postdata = {
                            'worksheet_uuid': worksheet_uuid,
                            'command': options
                        };

                        $.ajax({
                            type:'POST',
                            cache: false,
                            url:'/api/worksheets/command/',
                            contentType:"application/json; charset=utf-8",
                            dataType: 'json',
                            data: JSON.stringify(postdata),
                            success: function(data, status, jqXHR){
                                console.log('===== Output of command: ' + options);
                                if (data.data.exception){
                                    console.error(data.data.exception);
                                    term.echo("<span style='color:red'>Error: " + data.data.exception +"</span>", {raw: true});
                                }
                                if (data.data.stdout){
                                    console.log(data.data.stdout);
                                    term.echo(data.data.stdout);
                                    var references = data.data.structured_result['refs'];
                                    Object.keys(references).forEach(function(k) {
                                        $(".terminal-output div div:contains(" + k + ")").html(function(idx, html) {
                                            var link = '/' + references[k]['type'] + 's/' + references[k]['uuid'];
                                            return html.replace(k, "<a href=" + link + " target='_blank'>" + k + "</a>");
                                        });
                                    }, this);
                                }
                                if (data.data.stderr){
                                    console.error(data.data.stderr);
                                    var err;
                                    err = data.data.stderr.replace(/\n/g, "<br>&emsp;"); // new line and a tab in
                                    // 200 is ok response, this is a false flag due to how output is getting defined.
                                    if(err.indexOf("200") === -1){ //-1 is not found
                                        term.echo("<span style='color:red'>" + err +"</span>", {raw: true});
                                    }

                                }
                                console.log('=====');
                                defer.resolve();
                                action_bar.props.refreshWorksheet();
                            },
                            error: function(jqHXR, status, error){
                                term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                                // displayError(jqHXR, status);
                                defer.reject();
                            }
                        });
                    }else {
                        alert('invalid syntax');
                        defer.reject();
                    }
                    return defer.promise();
                }, // end of executefn
            }, // end of cl

            // real commands  and implementation start here
            'work': {
                helpText: formatHelp('work <worksheet>', 'go to worksheet'),
                minimumInputLength: 0,
                edit_enabled: false,
                autocomplete: function(options){ // is a promise must resolve and return a promise
                    var defer = jQuery.Deferred();
                    var get_data = {
                        search_string: options[options.length-1]
                    };
                    $.ajax({
                        type: 'GET',
                        url: '/api/worksheets/search/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR, callback){
                            var autocomplete_list = [];
                            for (var i = 0; i < data.worksheets.length; i++) {
                                var worksheet = data.worksheets[i];
                                var text = '';
                                if(data.search_string.indexOf('0x') === 0){
                                    text = worksheet.uuid
                                }else{
                                    text = worksheet.name
                                }
                                autocomplete_list.push({
                                    'text': text,
                                    'display': worksheet.uuid.slice(0, 10)  + " | " +  worksheet.name + ' | Owner: ' + worksheet.owner_name,
                                });
                            }
                            defer.resolve(autocomplete_list)
                        },
                        error: function(jqHXR, status, error){
                            defer.resolve([]);
                            var error;
                            if(jqHXR.responseJSON){
                                error = jqHXR.responseJSON['error'];
                            }else{
                                error = error
                            }
                            term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                        }
                    });
                    return defer.promise();
                },
                executefn: function(options, term, action_bar){
                    var defer = jQuery.Deferred();

                    if(options[1]){
                        if(options[1].length > 33){ // a full uuid
                            defer.resolve()
                            term.echo("Loading worksheet...", {raw: true});
                            window.location = '/worksheets/' + options[1] + '/';
                        }else{
                            var get_data = {
                                "spec": options[1]
                            }
                            $.ajax({
                                type: 'GET',
                                url: '/api/worksheets/get_uuid/',
                                dataType: 'json',
                                data: get_data,
                                success: function(data, status, jqXHR, callback){
                                    defer.resolve()
                                    term.echo("Loading worksheet...", {raw: true});
                                    window.location = '/worksheets/' + data.uuid + '/';

                                },
                                error: function(jqHXR, status, error){
                                    defer.resolve([]);
                                    var error;
                                    if(jqHXR.responseJSON){
                                        error = jqHXR.responseJSON['error'];
                                    }else{
                                        error = error
                                    }
                                    term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                                    defer.resolve()
                                }
                            });
                            // term.echo("<span style='color:red'>Error: Please enter a full uuid. (note you can press tab to autocomplete a uuid if valid)</span>", {raw: true});
                        }
                    }else{// no options, resolve
                        defer.resolve()
                    }
                    return defer.promise();
                },
            }, // end off work

            'new': {
                helpText: formatHelp('new <name>', 'create new worksheet with given name'),
                minimumInputLength: 0,
                edit_enabled: false,
                autocomplete: function(options){ // is a promise must resolve and return a promise
                    var defer = jQuery.Deferred();
                    defer.resolve([])
                    return defer.promise();
                },
                executefn: function(options, term, action_bar){
                    var defer = jQuery.Deferred();
                    var postdata = {
                        name: options[options.length-1]
                    };
                    $.ajax({
                        type:'POST',
                        cache: false,
                        url:'/api/worksheets/',
                        contentType:"application/json; charset=utf-8",
                        dataType: 'json',
                        data: JSON.stringify(postdata),
                        success: function(data, status, jqXHR){
                            defer.resolve([])
                            window.location = '/worksheets/' + data.uuid + '/';
                        },
                        error: function(jqHXR, status, error){
                            defer.resolve([])
                            var error;
                            if(jqHXR.responseJSON){
                                error = jqHXR.responseJSON['error'];
                            }else{
                                error = error
                            }
                            term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                        }
                    });
                    return defer.promise();
                }, // end of executefn
            }, // end of new

            'add': {
                edit_enabled: true,
                autocomplete: function(options){ // is a promise must resolve and return a promise
                    var defer = jQuery.Deferred();
                    var get_data = {
                        search_string: options[options.length-1]
                    };
                    $.ajax({
                        type: 'GET',
                        url: '/api/bundles/search/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR){
                            var autocomplete_list = [];
                            for(var uuid in data.bundles){
                                var bundle = data.bundles[uuid];
                                var user = bundle.owner_name; // owner is a string <username>(<user_id>)
                                var created_date = new Date(0); // The 0 there is the key, which sets the date to the epoch
                                created_date.setUTCSeconds(bundle.metadata.created);
                                created_date = created_date.toLocaleDateString() + " at " + created_date.toLocaleTimeString();
                                autocomplete_list.push({
                                    'text': uuid,
                                    'display': uuid.slice(0, 10)  + " | " +  bundle.metadata.name + ' | Owner: ' + user + ' | Created: ' + created_date,
                                });
                            }
                            defer.resolve(autocomplete_list)
                        },
                        error: function(jqHXR, status, error){
                            defer.resolve([])
                            var error;
                            if(jqHXR.responseJSON){
                                error = jqHXR.responseJSON['error'];
                            }else{
                                error = error
                            }
                            term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                            console.error(status + ': ' + error);
                        }
                    });
                    return defer.promise();
                },
                executefn: function(options, term, action_bar){
                    var defer = jQuery.Deferred();
                    var bundle_uuid = options[options.length-1]
                    var worksheet_uuid = ws_obj.state.uuid;
                    var postdata = {
                        'bundle_uuid': bundle_uuid,
                        'worksheet_uuid': worksheet_uuid
                    };
                    $.ajax({
                        type:'POST',
                        cache: false,
                        url:'/api/worksheets/add/',
                        contentType:"application/json; charset=utf-8",
                        dataType: 'json',
                        data: JSON.stringify(postdata),
                        success: function(data, status, jqXHR){
                            defer.resolve([])
                            action_bar.props.refreshWorksheet();
                        },
                        error: function(jqHXR, status, error){
                            defer.resolve()
                            var error;
                            if(jqHXR.responseJSON){
                                error = jqHXR.responseJSON['error'];
                            }else{
                                error = error
                            }
                            term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                            console.error(status + ': ' + error);
                        }
                    });
                    return defer.promise();
                }
            }, // end off add

            'info': {
                helpText: formatHelp('info <bundle>', 'go to info page of bundle'),
                edit_enabled: true,
                autocomplete: function(options){ // is a promise must resolve and return a promise
                    var defer = jQuery.Deferred();
                    var search_string = '';
                    var worksheet_uuid = ws_obj.state.uuid;

                    if(options.length == 3){
                        search_string = options[options.length-1]
                    }else{
                        return defer.resolve([]); // return nothing they already have a bundle uuid
                    }
                    var get_data = {
                        worksheet_uuid: worksheet_uuid
                    };

                    $.ajax({
                        type: 'GET',
                        url: '/api/worksheets/bundle_list/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR){
                            var autocomplete_list = [];
                            self.temp_holder = data.bundles
                            data.bundles.forEach(function(bundle){
                                var user = bundle.owner_name;  // owner is a string <username>(<user_id>)
                                var created_date = new Date(0);  // The 0 there is the key, which sets the date to the epoch
                                created_date.setUTCSeconds(bundle.metadata.created);
                                created_date = created_date.toLocaleDateString() + " at " + created_date.toLocaleTimeString();
                                var text = '';
                                if(search_string.indexOf("0x") == 0){
                                    text = bundle.uuid
                                }else{ // search a word, lets match on that word
                                    text = bundle.metadata.name
                                }
                                autocomplete_list.push({
                                    'text': text,
                                    'display':  bundle.uuid.slice(0, 10)  + " | " + bundle.metadata.name + ' | Owner: ' + user + ' | Created: ' + created_date,
                                });
                            });  // end of forEach
                            defer.resolve(autocomplete_list)
                        },
                        error: function(jqHXR, status, error){
                            defer.resolve([])
                            var error;
                            if(jqHXR.responseJSON){
                                error = jqHXR.responseJSON['error'];
                            }else{
                                error = error
                            }
                            term.echo("<span style='color:red'>Error: " + error +"</span>", {raw: true});
                            console.error(status + ': ' + error);
                        }
                    });
                    return defer.promise();
                },
                executefn: function(options, term, action_bar){
                    var defer = jQuery.Deferred();
                    var bundle_uuid = options[options.length-1]
                    defer.resolve([])
                    var output = undefined;
                    if(bundle_uuid){
                        // ^x will open info on user selected bundle from worksheet list
                        if(bundle_uuid.toLocaleLowerCase() === "^x"){
                            var current_focus = action_bar.current_focus(); // will update focustype
                            var subFocusIndex = action_bar.props.subFocusIndex;
                            if(action_bar.focustype == 'bundle'){
                                var bundle_info;
                                if(current_focus.bundle_info instanceof Array){ //tables are arrays
                                    bundle_info = current_focus.bundle_info[action_bar.props.subFocusIndex]
                                }else{ // content/images/ect. are not
                                    bundle_info = current_focus.bundle_info
                                }
                                if(bundle_info){
                                    bundle_uuid = bundle_info.uuid; // set bundle_uuid will fall through and open bundle
                                }
                            }else{
                                 output = output || "<span style='color:red'>Error: Please select a valid bundle</span>";
                            }
                        }// end of if ^x

                        // default handlers
                        if(self.temp_holder){ // go set from name in lookup
                            // if we have a temp_holder we have a list of bundles in the ws from autocomplete
                            // bundle_uuid is reallly a name of the bundle.
                            // need to match it
                            var temp_bundle_uuid;
                            for (var i = 0; i < self.temp_holder.length; ++i) {
                                var bundle = self.temp_holder[i];
                                if(bundle.metadata.name === bundle_uuid ){
                                    temp_bundle_uuid = bundle.uuid
                                    break;
                                }
                            }
                            if(temp_bundle_uuid){ // did we match?
                                bundle_uuid = temp_bundle_uuid
                            }else{// no match found
                                output = output || "<span style='color:red'>No bundle match found</span>";
                            }
                            self.temp_holder = undefined;
                        }
                        if(bundle_uuid.length > 33){ // a full uuid
                                var location = '/bundles/' + bundle_uuid + '/';
                                window.open(location,'_blank');
                                output = "loading info page..."
                        }else{
                            // find uuid
                            output = output || "<span style='color:red'>Error: Please enter a full uuid or a name. (note you can press tab to autocomplete a uuid or name if valid)</span>";
                        }

                    }
                    term.echo(output, {raw: true});
                    return defer.promise();
                }
            }, // end off info

            'upload': {
                helpText: formatHelp('upload', 'upload a program or dataset'),
                edit_enabled: true,
                executefn: function(options, term, action_bar) {
                    var defer = jQuery.Deferred();
                    defer.resolve([]);
                    if (options.length == 1) {
                      // If no arguments specified, then launch modal to select.
                      $("#ws-bundle-upload").modal();
                    } else {
                      // Else, backoff to a regular cl call.
                      cl(options, term, action_bar);
                    }
                    return defer.promise();
                }, // end of executefn
            }, // end of upload

            'wedit': {
                helpText: formatHelp('wedit', 'edit the worksheet'),
                edit_enabled: true,
                executefn: function(options, term, action_bar) {
                    var defer = jQuery.Deferred();
                    defer.resolve([]);
                    action_bar.props.rawMode();
                    return defer.promise();
                }, // end of executefn
            }, // end of wedit

            // 'run': {   // TODO
            //     minimumInputLength: 0,
            //     edit_enabled: true,
            //     maximumSelectionSize: function(){
            //         // jquery isnt supposed to be in here but there is no other way way to get the value in this function
            //         $('#search').val();
            //         //TODO
            //     },
            //     searchChoice: function(input, term){
            //         // jquery isnt supposed to be in here but there is no other way way to get the value in this function
            //         if(ws_actions.checkRunCommandDone($('#search').val())){
            //             return {};
            //         }
            //         if(term.lastIndexOf('\'', 0) === 0){
            //             return {
            //                 id: term,
            //                 text: 'Command: ' + term
            //             };
            //         }
            //         if(term.lastIndexOf(":", 0) === -1){
            //             return {
            //                 id: term,
            //                 text: 'Dependencies (<key>:<bundle>) ' + term
            //             };
            //         }
            //     },
            //     queryfn: function(query){
            //         if(ws_actions.checkRunCommandDone(query.element.val())){
            //             return;
            //         }
            //         if(query.term.lastIndexOf('\'', 0) === 0){
            //             query.callback({
            //                     results: []
            //                 });
            //             return;
            //         }else if(query.term.lastIndexOf(":") === -1){
            //             query.callback({
            //                     results: []
            //                 });
            //             return;
            //         }
            //         // we are after a command
            //         var get_data = {
            //             // only get stuff after the :
            //             search_string: query.term.slice(query.term.lastIndexOf(':')+1)
            //         };
            //         $.ajax({
            //             type: 'GET',
            //             url: '/api/bundles/search/',
            //             dataType: 'json',
            //             data: get_data,
            //             success: function(data, status, jqXHR){
            //                 // select2 wants its options in a certain format, so let's make a new
            //                 // list it will like
            //                 var newOptions = [];
            //                 for(var k in data){
            //                     newOptions.push({
            //                         'id': query.term.split(':')[0] + ":" + k, // UUID
            //                         'text': data[k].metadata.name + ' | ' + k
            //                     });
            //                 }
            //                 query.callback({
            //                     results: newOptions
            //                 });
            //             },
            //             error: function(jqHXR, status, error){
            //                 displayError(jqHXR, status);
            //             }
            //         });
            //     },
            //     executefn: function(params, command, callback){
            //         console.log("creating run bundle");
            //         console.log(params);
            //         worksheet_uuid = ws_obj.state.uuid;
            //         var postdata = {
            //             'worksheet_uuid': worksheet_uuid,
            //             'data': params.splice(1)
            //         };
            //         $.ajax({
            //             type:'POST',
            //             cache: false,
            //             url:'/api/bundles/create/',
            //             contentType:"application/json; charset=utf-8",
            //             dataType: 'json',
            //             data: JSON.stringify(postdata),
            //             success: function(data, status, jqXHR){
            //                 console.log('run bundles');
            //                 console.log(data);
            //                 callback();
            //             },
            //             error: function(jqHXR, status, error){
            //                 displayError(jqHXR, status);
            //             }
            //         });
            //     },
            // }, // end of run


        }; // end of commands
    }// endof worksheetActions() init

    // helper commands ----------- helper commands ------------ helper commands
    WorksheetActions.prototype.getCommands = function(can_edit, all){
        all = all || false
        // grab relevant parts of the command dict into an array it can work with
        // this is derfered since getCommands is used for autocomplete.
        // if used else where don't forget your .then()
        var defer = jQuery.Deferred();

        can_edit = typeof can_edit !== 'undefined' ? can_edit : true;
        var commandDict = this.commands;
        var commandList = [];
        for(var key in commandDict) {
            if (can_edit || !commandDict[key].edit_enabled) {
                commandList.push(key);
            }
        }
        commandList = _.without(commandList, 'cl'); // no need for cl
        if(all){
            commandList = commandList.concat(this.not_implemented_commands)
        }
        defer.resolve(commandList); // resolve immediately since this isnt ajax
        return defer.promise();
    }; // end of getCommands

    WorksheetActions.prototype.checkAndReturnCommand = function(command){
        var command_dict;
        if(this.commands.hasOwnProperty(command)){
            command_dict = ws_actions.commands[command];
        }
        return command_dict;
    };

    return WorksheetActions;
}();
