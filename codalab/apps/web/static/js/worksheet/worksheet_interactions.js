// Singleton class  to manage a worksheet's interactions
// gets created in worksheet/details.html

function WorksheetInteractions(){
    var instance;
    WorksheetInteractions = function WorksheetInteractions(){
        return instance;
    };
    WorksheetInteractions.prototype = this;
    instance = new WorksheetInteractions();
    instance.constructor = WorksheetInteractions;

    instance.state = {
        worksheetKeyboardShortcuts: true,
        worksheetEditingIndex: -1,
        worksheetFocusIndex: 0
    };

    return instance;
}