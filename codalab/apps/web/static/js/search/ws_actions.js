// Singleton class to manage actions triggered by the
// general search bar
function WorksheetActions() {
    var instance;
    WorksheetActions = function WorksheetActions(){
        return instance;
    };
    WorksheetActions.prototype = this;
    instance = new WorksheetActions();
    instance.constructor = WorksheetActions();

    instance.doAdd = function(params, command){
        var bundleID = params[1];
        var worksheetID = ws_obj.state.uuid;
        alert('Make a call to the cli to add the bundle with UUID ' + bundleID +
            ' to this worksheet, which has the UUID ' + worksheetID);
    };
    instance.doInfo = function(params, command){
        // ATL replace with 'bundle' link
        window.location = '/worksheets/' + params[1] + '/';
    };
    // Dictionary of terms that can be entered into the search bar and the names of
    // functions they call.
    instance.commands = {
        'add': {
            functionName: 'doAdd',
            helpText: 'add - add a bundle to this worksheet name or uuid',
            url: '/api/worksheets/'
        },
        'info': {
            functionName: 'doInfo',
            helpText: 'info - go to a bundle\'s info page',
            url: '/api/worksheets/'
        }
    };
    // the select2 autocomplete expects its data in a certain way, so we'll turn
    // the relevant parts of the command dict. into an array it can work with
    instance.getCommands = function(){
        commandDict = this.commands;
        commandList = [];
        for(var key in commandDict){
            commandList.push({
                'id': key,
                'text': commandDict[key].helpText
            });
        }
        return commandList;
    };
    return instance;
}