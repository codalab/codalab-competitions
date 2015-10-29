/*
Information about the current worksheet and its items.
Main challenge is to maintain the connection between the raw worksheet markdown
and the worksheet items which are actually displayed.
*/

var WorksheetContent = function() {
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
            raw: [],
            group_permissions: [],
            permission_str: ''
        };
    }

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
        //clean up raw undefineds
        newArray = [];
        for(var i = 0; i < this.state.raw.length; i++){
            if (this.state.raw[i] !== undefined ){
                newArray.push(this.state.raw[i]);
            }
        }
        this.state.raw = newArray;

    };
    WorksheetContent.prototype.updateItemsIndex = function() {
        // loop through and update all items to their raw index
        // we use this to keep track of the items to their raw conter part
        // when updates/edits happen we both update the item list and the raw list.
        var items =  this.state.items;
        var raw = this.state.raw;
        items.map(function(ws_item, index){
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
                    if(raw[i].lastIndexOf('//', 0) === 0){
                        last_raw_index = i+1;
                    }else{
                        break; // break out, we are done with comments
                    }
                }
            }
            ws_item.state.raw_index = last_raw_index;

            // now how many elements does it take up
            raw_size = raw.length - last_raw_index; //default to the end
            if(!below_item){
                ws_item.state.raw_size = raw_size;
                return;
            }

            // we are in the middle of a ws,
            // what are you? Then let's find where you begin and end
            switch (ws_item.state.mode) {
                case 'markup':
                    // grab the first bundle's info following you.
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
                        case 'search':
                            for(i=last_raw_index; i < raw.length; i++){
                                //a line that begins with %, which means another bundle display type
                                if((raw[i].lastIndexOf('%', 0) === 0)){
                                    raw_size = i - last_raw_index;
                                    break;
                                }else{
                                    //??
                                }
                            }
                            break
                        case 'markup': // this case only happens when moving around items
                            // init markup is consolidated.
                            // will be consolidated after save and update so
                            // set to self we already know how large you are
                            raw_size = ws_item.state.raw_size;
                            break;
                        default: // the other case is always followed by some sort of bundle or display type
                            // the bundle_info may be an object or an array of objects
                            var bundle = below_item.state.bundle_info;
                            if(_.isArray(bundle)){
                                bundle = bundle[0]
                            }
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
                case 'image':
                case 'record':
                    var bundle_info = ws_item.state.bundle_info;
                    // find the last bundle in the table etc. that is ref
                    // that's the end of the display

                    var bundle;
                    if(_.isArray(bundle_info)){
                        bundle = bundle_info[bundle_info.length-1];
                    }else{
                        bundle = bundle_info;
                    }

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
                case 'search':
                    // we default ws_item.state.raw_size to 0. worksheet is 1 line always aka size 0
                    break;
                default:
                    console.error("Got an item mode index does not handle. Please update raw size for this item mode");
            }// end of swtich statment
        });// end of  items.map(function(ws_item, index){

    };

    WorksheetContent.prototype.getRaw = function(){
        // get string rep and line count for text area
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
        if (props.async === undefined){
            props.async = true;
        }

        $.ajax({
            type: "GET",
            url: this.url,
            async: props.async,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.state = data;
                var ws_items = [];
                data.items.forEach(function(item){
                    var ws_item = new WorksheetItem(item.interpreted, item.bundle_info, item.mode, item.properties, item.subworksheet_info);
                    ws_items.push(ws_item);
                });
                this.state.items = ws_items;
                //consolidated
                consolidatedWorksheetItems = this.consolidateMarkdownBundles();
                this.state.items = consolidatedWorksheetItems;
                //update raw to item indexs
                this.updateItemsIndex();
                props.success(this.state);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    WorksheetContent.prototype.saveWorksheet = function(props) {
        $('#update_progress').show();
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};
        var postdata = {
            'name': this.state.name,
            'uuid': this.state.uuid,
            'owner_id': this.state.owner_id,
            'lines': this.state.raw
        };
        $('#save_error').hide();
        $.ajax({
            type: "POST",
            cache: false,
            url: this.url,
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            data: JSON.stringify(postdata),
            success: function(data) {
                console.log('Saved worksheet ' + this.state.uuid);
                props.success(data);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    return WorksheetContent;
}();

////////////////////////////////////////////////////////////

var WorksheetItem = function() {
    function WorksheetItem(interpreted, bundle_info, mode, properties, subworksheet_info) {
        this.state = {
            interpreted: interpreted,
            bundle_info: bundle_info,
            properties: properties,
            subworksheet_info: subworksheet_info,
            mode: mode,
            raw_index: 0,
            raw_size: 0,
        };
    }

    return WorksheetItem;
}();
