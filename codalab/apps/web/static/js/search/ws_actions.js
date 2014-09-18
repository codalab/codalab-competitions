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

    instance.doRed = function(){
        alert('CODE RED!\nFunction for red executed');
    };
    instance.doGreen = function(){
        console.log('--------');
        console.log('Execute the action for GREEN');
        console.log('--------');
    };
    instance.doBlue = function(){
        if(confirm('Did you choose blue?')){
            alert('That is correct.');
        }
    };
    instance.doOrange = function(){
        $('h1.worksheet-icon').addClass("orange").delay(1000).queue(function(next){
            $(this).removeClass("orange");
            next();
        });
    };
    instance.doYellow = function(){
        $('body').addClass("yellow").delay(1000).queue(function(next){
            $(this).removeClass("yellow");
            next();
        });
    };
    instance.doSave = function(){
        $('.content').addClass("saving").delay(2000).queue(function(next){
            $(this).removeClass("saving");
            next();
        });
    };

    return instance;
}