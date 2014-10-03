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
        console.log('%c CALL UPDATE ITEMS ', 'background: green; color: white;');
        // loop through and update all items to their raw index
        // console.log('updateItemsIndex');
        // console.log('~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-');
        var items =  this.state.items;
        var raw = this.state.raw;
        items.map(function(ws_item, index){
            // console.log('%c----------------------------------updateIndex----------------------------------', 'background: #333; color: #dad');
            // console.log(ws_item.state.interpreted);
            // console.log(ws_item.state.bundle_info);
            // console.log('%c'+ws_item.state.mode, 'background: #fff; color: #a8b');
            // console.log('');

            var above_item = items[index-1];
            var below_item = items[index+1];
            var last_raw_index = -1;
            var raw_size = -1;
            var i = 0; // counter

            if(above_item){
                var size = 0;
                if(above_item.state.raw_size){// a non 0
                    size = above_item.state.raw_size;
                }else{
                    // the last items size was 0, but we need to add one to move to the next index.
                    size = 1;
                }
                last_raw_index = above_item.state.raw_index + size; //sub one for 0 index/size
            }else{
                // this is the first item. Let's get the index after the comments stop
                // and the real worksheet begins
                for(i=0; i < raw.length; i++){
                    if(raw[i].lastIndexOf('//', 0) === 0 || raw[i].lastIndexOf('%', 0) === 0){
                        last_raw_index = i+1;
                    }else{
                        break; // break out, we are done with comments
                    }
                }
            }
            ws_item.state.raw_index = last_raw_index;

            raw_size = raw.length - last_raw_index; //default to the end
            if(!below_item){
                // end of worksheet
                ws_item.state.raw_size = raw_size;
                return;
            }
            // we are in the middle of a ws,
            // what are you? Then let's find where you begin and end
            switch (ws_item.state.mode) {
                case 'markup':
                    // grab the first bundle's info following you.
                    // debugger;
                    switch (below_item.state.mode) {
                        case 'worksheet':
                            for(i=last_raw_index; i < raw.length; i++){
                                // that bundle may be the start of the next non-markdown block
                                // or a line that begins with %, which means another bundle display type
                                if((raw[i].lastIndexOf('[worksheet', 0) === 0)){
                                    raw_size = i - last_raw_index;
                                    break;
                                }else{
                                    //??
                                }
                            }
                            break;
                        default:
                            var bundle = below_item.state.bundle_info[0];
                            for(i=last_raw_index; i < raw.length; i++){
                                // that bundle may be the start of the next non-markdown block
                                // or a line that begins with %, which means another bundle display type
                                if(bundle){
                                    if(raw[i].search(bundle.uuid) > -1 || (raw[i].lastIndexOf('%', 0) === 0)){
                                        raw_size = i - last_raw_index;
                                        break;
                                    }else{
                                        //??
                                    }
                                }else {
                                    break;
                                }
                            }
                            break;
                    }// end of switch (below_item.state.mode)

                    ws_item.state.raw_size = raw_size;
                    break; //break out of case 'markup':
                case 'inline':
                case 'table':
                case 'contents':
                case 'html':
                case 'record':
                    var bundle_info = ws_item.state.bundle_info;
                    // find the last bundle in the table etc. that is ref
                    // that's the end of the display
                    var bundle = ws_item.state.bundle_info[bundle_info.length-1];
                    var found = false;
                    for(i=last_raw_index; i < raw.length; i++){
                        if(raw[i].search(bundle.uuid) > -1){
                            raw_size = i - last_raw_index + 1;
                            found = true;
                        }else{
                            if(found){ // we found the last instance of it in this chunk. Quit out
                                break;
                            }
                        }
                    }
                    ws_item.state.raw_size = raw_size;
                    break;
                case 'worksheet':
                    // we default ws_item.state.raw_size to 0. worksheet is 1 line always aka size 0
                    break;
                default:
                    console.error("Got an item mode index does not handle.");
            }
        });
        console.log('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-');

        items.map(function(ws_item, index){
            console.log('%c oooooooooooooooooooooooooooooooooooo', 'background: #fff; color: #fad');
            console.log(ws_item.state.interpreted);
            console.log(ws_item.state.bundle_info);
            console.log(ws_item.state.raw_index);
            console.log(ws_item.state.raw_size);
            console.log('');
        });
        console.log('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-');
        console.log(this.state.raw);



    };
    WorksheetContent.prototype.deleteItem = function(index) {
        //update raw
        //deleting items at index, raw_index+raw_size
        var ri = this.state.items[index].state.raw_index;
        var rs = this.state.items[index].state.raw_size;
        this.state.raw.splice(ri, rs);

        //now update the list
        var ws1 = this.state.items.slice(0,index);
        var ws2 = this.state.items.slice(index + 1);
        ws1.push(undefined);
        this.state.items = ws1.concat(ws2);
        this.cleanUp();
    };
    WorksheetContent.prototype.insertRawItem = function(index, item){
        //update raw
        //the item is the value of the textarea, so we need to split it into an array by linebreaks
        var item_array = item.split('\n');
        var items = this.state.items;
        var above_item = items[index-1];
        var below_item = items[index+1];
        // because this is a new item has been inserted into this.state.items,
        // we can't trust the raw_index of this item so we need to derive it from its neighbors
        var raw_index = -1;
        if(below_item){
            // its' easiest to do this using the next item, because we're going to take its place
            raw_index = below_item.state.raw_index;
        }else {
            // but if we're at the end of the worksheet, we need to use the preceeding item to calculate the raw index
            raw_index = above_item.state.raw_index + above_item.state.raw_size + 1;
        }
        //now that we know where to insert, do the same split, insert, and concat business we do elsewhere
        var raw1 = this.state.raw.slice(0,raw_index);
        //account for the extra blank line we've inserted
        var raw2 = this.state.raw.slice(raw_index);
        // set the raw. the WorksheetItems will take care of themselves
        this.state.raw = raw1.concat(item_array, raw2);
    };
    WorksheetContent.prototype.insertItem = function(newIndex, newItem) {
        //insert new item at index, raw_index+raw_size
        var ws1 = this.state.items.slice(0,newIndex);
        var ws2 = this.state.items.slice(newIndex);
        ws1.push(newItem);
        this.state.items = ws1.concat(ws2);
    };
    WorksheetContent.prototype.setItem = function(index, item) {
        //update raw
        //the item here is a WorksheetItem, so we need to get its interpreted value and split it into an array
        var item_array = item.state.interpreted.split('\n');
        //because we're editing an item that already exists, we can use its raw_index and assume it's correct...
        var ri = this.state.items[index].state.raw_index;
        var rs = this.state.items[index].state.raw_size;
        var raw1 = this.state.raw.slice(0,ri);
        var raw2 = this.state.raw.slice(ri + rs);
        this.state.raw = raw1.concat(item_array, raw2);
        //now update items
        this.state.items[index] = item;
        this.needs_cleanup = true; // newItems can be undefined. Lets cross our t's
    };
    WorksheetContent.prototype.moveItem = function(oldIndex, newIndex){
        //update raw
        // are we moving forward or backward?
        var delta = newIndex - oldIndex;
        // see how many raw items we need to jump by getting the size of the previous or next item
        var jump_size = this.state.items[oldIndex+delta].state.raw_size === 0 ? 1 : this.state.items[oldIndex+delta].state.raw_size;
        // raw index and size of the item we're moving
        var ri = this.state.items[oldIndex].state.raw_index;
        var rs = this.state.items[oldIndex].state.raw_size === 0 ? 1 : this.state.items[oldIndex].state.raw_size;
        // the new position will be the old position minus the size of the previous item OR
        // the old position plus the size of the next item
        var newPos = ri + (jump_size * delta);
        // pop out the raw lines of the item we're moving
        var raw_items = this.state.raw.splice(ri, rs);
        // if it's a table or a record bundle, add a blank line of padding so bundles don't get
        // automatically consolidated
        switch(this.state.items[oldIndex].state.mode){
            case 'table':
            case 'record':
                raw_items = [''].concat(raw_items, ['']);
        }
        // split the list where we want to reinsert
        var raw1 = this.state.raw.slice(0,newPos);
        var raw2 = this.state.raw.slice(newPos);
        // combine the front of the list, the moved items, and the back of the list
        this.state.raw = raw1.concat(raw_items, raw2);
    };
    WorksheetContent.prototype.getRaw = function(){
        var raw = {
            content: this.state.raw.join('\n'),
            lines: this.state.raw.length
        };
        return raw;
    };
    WorksheetContent.prototype.consolidateMarkdownBundles = function() {
        var consolidatedWorksheet = [];
        var markdownChunk         = '';
        var ws_items = this.state.items; // shortcut naming
        ws_items.map(function(item, index){
            var mode        = item.state.mode;
            var interpreted = item.state.interpreted;
            if(mode == 'markup' && index <= ws_items.length - 1){
                var content = interpreted + '\n';
                markdownChunk += content;
                if(index == ws_items.length - 1){ // we have reached the end, add it and call it a day
                    // markdown bundles do not have a bundle_info
                    newMarkdownItem = new WorksheetItem(markdownChunk, undefined, 'markup');
                    consolidatedWorksheet.push(newMarkdownItem);
                }
            }else { // not markdown
                if(markdownChunk.length){
                    // add in the markdown as one single item
                    newMarkdownItem = new WorksheetItem(markdownChunk, undefined, 'markup');
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
                this.state = data;
                var ws_items = [];
                data.items.map(function(item){
                    var ws_item = new WorksheetItem(item.interpreted, item.bundle_info, item.mode);
                    ws_items.push(ws_item);
                });
                this.state.items = ws_items;
                //consolidated
                consolidatedWorksheetItems = this.consolidateMarkdownBundles();
                this.state.items = consolidatedWorksheetItems;
                this.updateItemsIndex();
                props.success(this.state);
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

        $('#save_error').hide();
        $('#save_progress').fadeIn('fast');
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
                $('#save_progress').fadeOut('fast');
                props.success(data);
            }.bind(this),
            error: function(xhr, status, err) {
                $('#save_progress').hide();
                $('#save_error').show();
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
            raw_index: 0,
            raw_size: 0,
        };
    }

    return WorksheetItem;
}();