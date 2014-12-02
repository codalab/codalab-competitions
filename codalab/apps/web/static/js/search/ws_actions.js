// Singleton class to manage actions triggered by the general search bar
var WorksheetActions =  function() {
    function WorksheetActions() {
        this.commands = {
            // Dictionary of terms that can be entered into the search bar
            // and the names of functions they call.
            // ------------------------------------
            // Example (* starred are required)
            // 'commandname'{  // what the user enters
            //  *  executefn: function that happens when they hit execute or cmd/ctrl + enter,
            //  *  helpText: shows up when they are search commands
            //
            //     data_url: does this command have an auto complete after it is entered
            //     type: type for above data_url call
            //     get_data: data that needs to get passed to data_url call. will haev a query param of what the user has entered
            //
            //     searchChoice: called if we want a custom search or help tex insead of json/ajax data_url
            //
            //     minimumInputLength: min length before doin get for search choices
            // }
            // ------------------------------------
            'add': {
                helpText: 'add - add a bundle to this worksheet name or uuid',
                minimumInputLength: 3,
                queryfn: function(query){
                    var get_data = {
                        search_string: query.term
                    };
                    $.ajax({
                        type: 'GET',
                        url: '/api/bundles/search/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR){
                            // select2 wants its options in a certain format, so let's make a new
                            // list it will like
                            query.callback({
                                results: ws_actions.AjaxBundleDictToOptions(data)
                            });
                        },
                        error: function(jqHXR, status, error){
                            console.error(status + ': ' + error);
                        }
                    });
                },
                executefn: function(params, command, callback){
                    var bundle_uuid = params[1];
                    var worksheet_uuid = ws_obj.state.uuid;
                    if(params.length === 2 && params[0] === 'add'){
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
                                callback();
                            },
                            error: function(jqHXR, status, error){
                                console.error("error: " + status + ': ' + error);
                            }
                        });
                    }else {
                        alert('wnew command syntax must be "wnew [worksheetname]"');
                    }
                }
            },// end off add
            'info': {
                helpText: 'info - go to a bundle\'s info page',
                minimumInputLength: 3,
                queryfn: function(query){
                    var get_data = {
                        search_string: query.term
                    };
                    $.ajax({
                        type: 'GET',
                        url: '/api/bundles/search/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR, callback){
                            // select2 wants its options in a certain format, so let's make a new
                            // list it will like
                            query.callback({
                                results: ws_actions.AjaxBundleDictToOptions(data)
                            });
                        },
                        error: function(jqHXR, status, error){
                            console.error(status + ': ' + error);
                        }
                    });
                },
                executefn: function(params, command, callback){
                    window.location = '/bundles/' + params[1] + '/';
                },
            }, // end off info
            'wnew': {
                helpText: 'wnew - add and go to a new worksheet by naming it',
                minimumInputLength: 0,
                searchChoice: function(input, term){
                    return {
                        id: term,
                        text: 'New worksheet name: ' + term
                    };
                },
                executefn: function(params, command, callback){
                    if(params.length === 2 && params[0] === 'wnew'){
                        var postdata = {
                            'name': params[1]
                        };
                        $.ajax({
                            type:'POST',
                            cache: false,
                            url:'/api/worksheets/',
                            contentType:"application/json; charset=utf-8",
                            dataType: 'json',
                            data: JSON.stringify(postdata),
                            success: function(data, status, jqXHR){
                                window.location = '/worksheets/' + data.uuid + '/';
                            },
                            error: function(jqHXR, status, error){
                                console.error(status + ': ' + error);
                            }
                        });
                    }else {
                        alert('wnew command syntax must be "wnew [worksheetname]"');
                    }
                }, // end of executefn
            },// end of wnew
            'run': {
                helpText: 'run - Create a run bundle INPROGRESS',
                minimumInputLength: 0,
                maximumSelectionSize: function(){
                    // jquery isnt supposed to be in here but there is no other way way to get the value in this function
                    $('#search').val();
                    //TODO
                },
                searchChoice: function(input, term){
                    // jquery isnt supposed to be in here but there is no other way way to get the value in this function
                    if(ws_actions.checkRunCommandDone($('#search').val())){
                        return {};
                    }
                    if(term.lastIndexOf('\'', 0) === 0){
                        return {
                            id: term,
                            text: 'Command: ' + term
                        };
                    }
                    if(term.lastIndexOf(":", 0) === -1){
                        return {
                            id: term,
                            text: 'target_spec  [<key>:](<uuid>|<name>)  ' + term
                        };
                    }
                },
                queryfn: function(query){
                    if(ws_actions.checkRunCommandDone(query.element.val())){
                        return;
                    }
                    if(query.term.lastIndexOf('\'', 0) === 0){
                        query.callback({
                                results: []
                            });
                        return;
                    }else if(query.term.lastIndexOf(":") === -1){
                        query.callback({
                                results: []
                            });
                        return;
                    }
                    // we are after a command
                    var get_data = {
                        // only get stuff after the :
                        search_string: query.term.slice(query.term.lastIndexOf(':')+1)
                    };
                    $.ajax({
                        type: 'GET',
                        url: '/api/bundles/search/',
                        dataType: 'json',
                        data: get_data,
                        success: function(data, status, jqXHR){
                            // select2 wants its options in a certain format, so let's make a new
                            // list it will like
                            var newOptions = [];
                            for(var k in data){
                                newOptions.push({
                                    'id': query.term + k, // UUID
                                    'text': data[k].metadata.name + ' | ' + k
                                });
                            }
                            query.callback({
                                results: newOptions
                            });
                        },
                        error: function(jqHXR, status, error){
                            console.error(status + ': ' + error);
                        }
                    });
                },
                executefn: function(params, command, callback){
                    console.log("createing run bundle");
                    console.log(params);
                    worksheet_uuid = ws_obj.state.uuid;
                    var postdata = {
                        'worksheet_uuid': worksheet_uuid,
                        'data': params.splice(1)
                    };
                    $.ajax({
                        type:'POST',
                        cache: false,
                        url:'/api/bundles/create/',
                        contentType:"application/json; charset=utf-8",
                        dataType: 'json',
                        data: JSON.stringify(postdata),
                        success: function(data, status, jqXHR){
                            console.log('run bundles');
                            console.log(data);
                            callback();
                        },
                        error: function(jqHXR, status, error){
                            console.error(status + ': ' + error);
                        }
                    });
                },
            }, // end of run
            'upload': {
                helpText: 'upload - upload a dataset via a url',
                minimumInputLength: 0,
                searchChoice: function(input, term){
                    return {
                        id: term,
                        text: 'dataset url: ' + term
                    };
                },
                executefn: function(params, command, callback){
                    if(params.length === 2 && params[0] === 'upload'){
                        worksheet_uuid = ws_obj.state.uuid;
                        var postdata = {
                            'worksheet_uuid': worksheet_uuid,
                            'url': params[1]
                        };
                        $.ajax({
                            type:'POST',
                            cache: false,
                            url:'/api/bundles/upload_url/',
                            contentType:"application/json; charset=utf-8",
                            dataType: 'json',
                            data: JSON.stringify(postdata),
                            success: function(data, status, jqXHR){
                                callback();
                            },
                            error: function(jqHXR, status, error){
                                console.error(status + ': ' + error);
                            }
                        });
                    }else {
                        alert('wnew command syntax must be "upload http://example.com/file"');
                    }
                }, // end of executefn
            },// end of wnew
        };// end of commands
    }// endof worksheetActions() init

    //helper commands
    WorksheetActions.prototype.getCommands = function(){
        // The select2 autocomplete expects its data in a certain way, so we'll turn
        // relevant parts of the command dict into an array it can work with
        var commandDict = this.commands;
        var commandList = [];
        for(var key in commandDict){
            commandList.push({
                'id': key,
                'text': commandDict[key].helpText
            });
        }
        return commandList;
    };

    WorksheetActions.prototype.checkAndReturnCommand = function(input){
        var command_dict;
        var command = _.first(input.split(','));
        if(this.commands.hasOwnProperty(command)){
            command_dict = ws_actions.commands[command];
        }
        return command_dict;
    };

    WorksheetActions.prototype.AjaxBundleDictToOptions = function(data){
        var newOptions = [];
        for(var k in data){
            newOptions.push({
                'id': k, // UUID
                'text': data[k].metadata.name + ' | ' + k
            });
        }
        console.log(newOptions.length + ' results');
        return newOptions;
    };

    WorksheetActions.prototype.checkRunCommandDone = function(val){
        var current_values = val.split(',');
        console.log('current_values.length')
        console.log(current_values.length);
        if(val.lastIndexOf('\'', 4) !== -1){
            return true;
        }
        return false;
    };

    return WorksheetActions;
}();