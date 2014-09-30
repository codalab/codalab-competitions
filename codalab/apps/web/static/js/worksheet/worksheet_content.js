// 'class' to manage a worksheet and its items.
// gets created in worksheet/details.html
var WorksheetContent = function() {
    //init
    function WorksheetContent(url) {
        this.url = url;
        this.needs_cleanup = false;
        this.state = {
            edit_permission: false,
            last_item_id: 0,
            name: '',
            owner: null,
            owner_id: 0,
            uuid: 0,
            items: [],
            raw: []
        };
    }
    //add functions and calls below
    WorksheetContent.prototype.getState = function() {
        if(this.needs_cleanup){
            this.cleanUp(); // removes any blank/null/undefined from our list of items
            this.needs_cleanup = false;
        }
        return this.state;
    };
    WorksheetContent.prototype.cleanUp = function() {
        //removes any falsy value, from the items array which should be only WorksheetItems
        //usfeull when deleting out items, we set to null and cleanup
        var newArray = [];
        for(var i = 0; i < this.state.items.length; i++){
            if (this.state.items[i]){
                newArray.push(this.state.items[i]);
            }
        }
        this.state.items = newArray;
    };
    WorksheetContent.prototype.updateItemsIndex = function() {
        //loop through and update all items to there raw index











    };
    WorksheetContent.prototype.deleteItem = function(index) {
        //update raw
        //deleting items at index, raw_index+raw_size

        //now update the list
        var ws1 = this.state.items.slice(0,newIndex);
        var ws2 = this.state.items.slice(newIndex);
        ws1.push(undefined);
        this.state.items = ws1.concat(ws2);
        this.cleanup();
    };
    WorksheetContent.prototype.insertItem = function(newIndex, newItem) {
        //update raw
        //insert new item at index, raw_index+raw_size
        var ws1 = this.state.items.slice(0,newIndex);
        var ws2 = this.state.items.slice(newIndex);
        ws1.push(newItem);
        this.state.items = ws1.concat(ws2);
    };
    WorksheetContent.prototype.setItem = function(index, newItem) {
        this.state.items[index] = newItem;
        this.needs_cleanup = true; // newItems can be undefined. Lets cross our t's
    };
    WorksheetContent.prototype.moveItem = function(oldIndex, newIndex){
        var items = this.state.items;
        items.splice(newIndex, 0, items.splice(oldIndex, 1)[0]);
        this.state.items = items;
    };
    WorksheetContent.prototype.getRaw = function(){
        var raw = {
            content: this.state.raw.join('\n'),
            lines: this.state.raw.length
        };
        return raw;
    };
    WorksheetContent.prototype.consolidateMarkdownBundles = function(ws_items) {
        var consolidatedWorksheet = [];
        var markdownChunk         = '';
        ws_items.map(function(item, index){
            var mode        = item.state.mode;
            var interpreted = item.state.interpreted;
            if(mode == 'markup' && index <= ws_items.length - 1){
                var content = interpreted + '\n';
                markdownChunk += content;
                if(index == ws_items.length - 1){
                    newMarkdownItem = new WorksheetItem(markdownChunk, item.state.bundle_info, 'markup');
                    consolidatedWorksheet.push(newMarkdownItem);
                }
            }else {
                if(markdownChunk.length){
                    newMarkdownItem = new WorksheetItem(markdownChunk, item.state.bundle_info, 'markup');
                    consolidatedWorksheet.push(newMarkdownItem);
                    markdownChunk = '';
                }
                consolidatedWorksheet.push(item);
            }
        });
        return consolidatedWorksheet;
    };
    WorksheetContent.prototype.fetch = function(props) {
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};

        $.ajax({
            type: "GET",
            url: this.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("WorksheetContent: setting worksheet state:");
                console.log(data);
                console.log('');
                ws_obj.state = data;
                var ws_items = [];
                data.items.map(function(item){
                    var ws_item = new WorksheetItem(item.interpreted, item.bundle_info, item.mode);
                    ws_items.push(ws_item);
                });
                consolidatedWorksheetItems = this.consolidateMarkdownBundles(ws_items);
                ws_obj.state.items = consolidatedWorksheetItems;
                props.success(ws_obj.state);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    WorksheetContent.prototype.saveWorksheet = function(props) {
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};
        console.log('------ save the worksheet here ------');
        var postdata = {
            'name': this.state.name,
            'uuid': this.state.uuid,
            'owner_id': this.state.owner_id,
            'lines': this.state.raw
        };
        $.ajax({
            type: "POST",
            cache: false,
            url: this.url,
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            data: JSON.stringify(postdata),
            success: function(data) {
                console.log('Saved worksheet');
                console.log(data);
                console.log('');
                props.success(data);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    return WorksheetContent;
}();


// 'class' to manage a worksheet's items
// gets created in worksheet/details.html
var WorksheetItem = function() {
    //init
    function WorksheetItem(interpreted, bundle_info, mode) {
        this.state = {
            interpreted: interpreted,
            bundle_info: bundle_info,
            mode: mode,
            raw_index: 30,
            raw_size: 5
        };
    }

    WorksheetItem.prototype.updateIndex = function() {





        //todo





    };


    return WorksheetItem;
}();