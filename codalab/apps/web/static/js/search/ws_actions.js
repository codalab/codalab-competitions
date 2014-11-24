// Singleton class to manage actions triggered by the general search bar
function WorksheetActions() {
    var instance;
    WorksheetActions = function WorksheetActions(){
        return instance;
    };
    WorksheetActions.prototype = this;
    instance = new WorksheetActions();
    instance.constructor = WorksheetActions();

    instance.commands = {
        // Dictionary of terms that can be entered into the search bar
        // and the names of functions they call.
        // ------------------------------------
        // Example (* starred are required)
        // 'commandname'{  // what the user enters
        //  *  executefunctionName: function that happens when they hit execute or cmd/ctrl + enter,
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
            executefunctionName: 'doAdd',
            helpText: 'add - add a bundle to this worksheet name or uuid',
            data_url: '/api/bundles/search/',
            type: 'GET',
            get_data: function(query){ return { search_string: query.term }; },
            minimumInputLength: 3,
        },
        'info': {
            executefunctionName: 'doInfo',
            helpText: 'info - go to a bundle\'s info page',
            data_url: '/api/bundles/search/',
            type: 'GET',
            get_data: function(query){ return { search_string: query.term }; },
            minimumInputLength: 3,
        },
        'wnew': {
            executefunctionName: 'doNewWorksheet',
            helpText: 'wnew - add and go to a new worksheet by naming it',
            minimumInputLength: 0,
            searchChoice: function(input, term){
                return {
                    id: term,
                    text: 'New worksheet name: ' + term
                };
            }

        }
    };


    instance.getCommands = function(){
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

    instance.checkAnReturnCommand = function(command){
        var command;
        if(instance.commands.hasOwnProperty(command)){
            command = ws_actions.commands[command];
        }
        return command;
    };


    //actions
    instance.doAdd = function(params, command){
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
                    WorksheetItemList.fetch_and_update();
                },
                error: function(jqHXR, status, error){
                    console.error("error: " + status + ': ' + error);
                }
            });
        }else {
            alert('wnew command syntax must be "wnew [worksheetname]"');
        }
    };

    instance.doInfo = function(params, command){
        window.location = '/bundles/' + params[1] + '/';
    };

    instance.doNewWorksheet = function(params, command){
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
    };

    return instance;
}