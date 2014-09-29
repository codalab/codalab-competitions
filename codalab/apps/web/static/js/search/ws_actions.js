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

    instance.doSave = function(){
        $('.content').addClass("saving").delay(2000).queue(function(next){
            $(this).removeClass("saving");
            next();
        });
    };
    instance.doAdd = function(params){
        var bundleID = params[1];
        var worksheetID = ws_obj.state.uuid;
        console.log('Make a call to the cli to add the bundle with UUID ' + bundleID + 
            ' to this worksheet, which has the UUID ' + worksheetID);
        ws_obj.fetch();
        // $.ajax({
        //     type: "POST",
        //     url: '',
        //     dataType: 'json',
        //     cache: false,
        //     success: function(data) {
        //         ws_obj.fetch();
        //     },
        //     error: function(xhr, status, err) {
        //         console.error(xhr, status, err)
        //     }
        // });
    };

    return instance;
}