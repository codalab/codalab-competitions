// 'class' to manage a worksheet's interactions
// gets created in worksheet/details.html
var WorksheetInteractions = function() {
    var instance;
    function init(self) {
        self.state = {
            worksheetKeyboardShortcuts: true,
            worksheetEditingIndex: -1,
            worksheetFocusIndex: 0
        };
        return self;
    }
    return {
        getInstance: function(){
            if(!instance){
                instance = init(this);
            }
            return instance;
        }
    };
}();
