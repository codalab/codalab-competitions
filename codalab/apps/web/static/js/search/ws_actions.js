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

    instance.doAdd = function(params){
        var bundleID = params[1];
        var worksheetID = ws_obj.state.uuid;
        alert('Make a call to the cli to add the bundle with UUID ' + bundleID +
            ' to this worksheet, which has the UUID ' + worksheetID);
    };

    return instance;
}