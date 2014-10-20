/** @jsx React.DOM */

var keyMap = {
    13: "enter",
    27: "esc",
    69: "e",
    38: "up",
    40: "down",
    65: "a",
    68: "d",
    73: "i",
    74: "j",
    75: "k",
    88: "x",
    191: "fslash"
};

// Dictionary of terms that can be entered into the search bar and the names of
// functions they call. See search_actions.js
var fakedata = {
    red: 'doRed',
    green: 'doGreen',
    blue: 'doBlue',
    orange: 'doOrange',
    yellow: 'doYellow',
    save: 'doSave'
};

var Worksheet = React.createClass({
    // master parent that controls the page
    getInitialState: function(){
        return {
            activeComponent: 'list',
            editMode: false
        }
    },
    componentDidMount: function() {
        this.bindEvents();
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.handleKeydown);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown');
    },
    handleSearchFocus: function(event){
        this.setState({activeComponent:'search'});
        // just scroll to the top of the page.
        // Add the stop() to keep animation events from building up in the queue
        // See also scrollTo* methods
        $('body').stop(true).animate({scrollTop: 0}, 250);
    },
    handleSearchBlur: function(event){
        // explicitly close the select2 dropdown because we're leaving the search bar
        $('#search').select2('close');
        this.setState({activeComponent:'list'});
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var activeComponent = this.refs[this.state.activeComponent];
        // At this top level, the only keypress the parent cares about is ? to open
        // the keyboard shortcuts modal, and then only if we're not actively editing something
        if(key === 'fslash' && event.shiftKey){
            event.preventDefault();
            this.handleSearchBlur(); // blur the search bar to avoid select2 z-index conflicts
            $('#glossaryModal').foundation('reveal', 'open');
            return false;
        }else if(key === 'e' && (event.metaKey || event.ctrlKey)){
            this.toggleEditing();
            return false;
        }else if(activeComponent.hasOwnProperty('handleKeydown')){
            // pass the event along to children
            activeComponent.handleKeydown(event);
            return false;
        }else {
            return true;
        }
    },
    toggleEditing: function(){
        this.setState({editMode:!this.state.editMode});
    },
    render: function(){
        var canEdit = ws_obj.getState().edit_permission && this.state.editMode;
        return (
            <div id="worksheet">
                <WorksheetSearch handleFocus={this.handleSearchFocus} handleBlur={this.handleSearchBlur} ref={"search"} active={this.state.activeComponent=='search'}/>
                <WorksheetItemList ref={"list"} active={this.state.activeComponent=='list'} canEdit={canEdit} toggleEditing={this.toggleEditing} />
            </div>
        )
    }
});

var WorksheetSearch = React.createClass({
    mixins: [Select2SearchMixin],
    handleKeydown: function(event){
        // the only key the searchbar cares about is esc. Otherwise we're just typing in the input.
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    event.preventDefault();
                    this.props.handleBlur();
                    break;
                default:
                    return true;
            }
        }
    },
    render: function(){
        return (
            <div className="ws-search">
                <input id="search" type="text" placeholder="General search" onFocus={this.props.handleFocus} onBlur={this.props.handleBlur} />
            </div>
        )
    }
});

var WorksheetItemList = React.createClass({
    getInitialState: function(){
        return {
            focusIndex: -1,
            editingIndex: -1,
            rawMode: false,
            worksheet: {
                last_item_id: 0,
                name: '',
                owner: null,
                owner_id: 0,
                uuid: 0,
                items: [],
                edit_permission: false,
                raw: []
            }
        }
    },
    componentDidMount: function() {
        this.fetch_and_update();
        // Set up the debounced version of the save method here so we can call it later
        this.slowSave = _.debounce(this.saveAndUpdateWorksheet, 1000);
    },
    componentDidUpdate: function(){
        if(!this.state.worksheet.items.length){
            $('.empty-worksheet').fadeIn('fast');
        }
    },
    fetch_and_update: function(){
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide().removeClass('alert-box alert');
                if(this.isMounted()){
                    this.setState({worksheet: ws_obj.getState()});
                }
                $('#update_progress').hide();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(ws_obj.url, status, err);
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-box alert');
                } else {
                    $("#worksheet-message").html("An error occurred: <code>'" + status + "' " + err + " (" + xhr.status + ")</code>. Please try refreshing the page.").addClass('alert-box alert');
                }
                $('#worksheet_container').hide();
            }.bind(this)
        });
    },
    handleKeydown: function(event){
        // No keyboard shortcuts are active in raw mode
        if(this.state.rawMode){
            return true;
        }
        var key = keyMap[event.keyCode];
        var fIndex = this.state.focusIndex;
        var eIndex = this.state.editingIndex;
        var focusedItem = this.refs['item' + fIndex];
        // if the focused item wants to handle certain keys, and this is one of them, pass it along
        if( focusedItem &&
            focusedItem.hasOwnProperty('keysToHandle') &&
            focusedItem.keysToHandle().indexOf(key) != -1
            ){
                focusedItem.handleKeydown(event);
        // Otherwise, if we're in edit mode (fIndex === eIndex is a sanity check)(so is the hasOwnProperty)
        }else if( focusedItem &&
                  fIndex === eIndex &&
                  focusedItem.hasOwnProperty('handleKeydown')
                ){
            focusedItem.handleKeydown(event);
        }else { // we have failed the other tests, let the worksheet handle the key
            switch (key) {
                case 'fslash': // Move focus to search bar
                    event.preventDefault();
                    // reach back up and change to search bar
                    this._owner.setState({activeComponent: 'search'});
                    break;
                case 'up': // move up
                case 'k':
                    event.preventDefault();
                    if(event.shiftKey && this.props.canEdit){
                        this.moveItem(-1);
                    }else {
                        if(fIndex <= 0){
                            // if we're already at the top of the worksheet, we can't go higher
                            fIndex = -1;
                        }else {
                            fIndex = Math.max(this.state.focusIndex - 1, 0);
                        }
                        this.setState({focusIndex: fIndex});
                        this.scrollToItem(fIndex);
                    }
                    break;
                case 'down': // move down
                case 'j':
                    event.preventDefault();
                    if(event.shiftKey && this.props.canEdit){
                        this.moveItem(1);
                    }else {
                        // Don't allow moving past the last item. Because the number of ws-item divs might
                        // not be the same as the number of item objects because of editing/inserting/whatever,
                        // count the actual divs instead
                        fIndex = Math.min(this.state.focusIndex + 1, $('#worksheet_content .ws-item').length - 1);
                        this.setState({focusIndex: fIndex});
                        this.scrollToItem(fIndex);
                    }
                    break;
                case 'e':  // edit item
                    event.preventDefault();
                    if(this.props.canEdit){
                        this.setState({editingIndex: fIndex});
                    }
                    break;
                case 'x': // select item
                    event.preventDefault();
                    if(focusedItem && this.props.canEdit){
                        focusedItem.setState({checked: !focusedItem.state.checked});
                    }
                    break;
                case 'd': // delete selected items
                    event.preventDefault();
                    if(this.props.canEdit){
                        this.deleteChecked();
                    }
                    break;
                case 'i': //insert
                    event.preventDefault();
                    if(this.props.canEdit){
                        this.insertItem(key);
                    }
                    break;
                case 'a': // really a cap A for instert After, like vi
                    event.preventDefault();
                    if(event.shiftKey && this.props.canEdit){
                        this.insertItem(key);
                    }
                    break;
                default:
                    return true;
            }
        }
    },
    scrollToItem: function(index){
        // scroll the window to keep the focused element in view
        var offsetTop = 0;
        if(index > -1){
            // find the item's position on the page, and offset it from the top of the viewport
            offsetTop = this.refs['item' + index].getDOMNode().offsetTop - 200;
        }
        $('body').stop(true).animate({scrollTop: offsetTop}, 250);
    },
    saveItem: function(index, interpreted){ // aka handleSave
        if(typeof index !== 'undefined' && typeof interpreted !== 'undefined'){
            var item = ws_obj.state.items[index];
            var mode = item.state.mode;
            var newItem = this.refs['item' + index].state.new_item;
            // because we need to distinguish between items that have just been inserted and items
            // that were edited, we have a 'new_item' flag on markdown items' state
            if(newItem){
                // if it's a new item, it hasn't been added to the raw yet, so do that.
                ws_obj.insertRawItem(index, interpreted);
            }else {
                ws_obj.state.items[index].state.interpreted = interpreted;
                ws_obj.setItem(index, ws_obj.state.items[index]);
            }
            // we duplicate this here so the edits show up right away, instead of after the save + update
            item.state.interpreted = interpreted;
            if(mode==='markup'){
                // we may have added contiguous markdown bundles, so we need to reconsolidate
                var unconsolidated = ws_obj.getState();
                var consolidated = ws_obj.consolidateMarkdownBundles(unconsolidated.items);
                ws_obj.state.items = consolidated;
            }
            this.setState({
                editingIndex: -1,
                worksheet: ws_obj.getState()
            });
            //reset the 'new_item' flag to false so it doesn't get added again if we edit and save it later
            this.refs['item' + this.state.editingIndex].setState({new_item:false});
        }
        this.saveAndUpdateWorksheet();
    },
    unInsert: function(){
        // this gets called when we insert an item then esc without saving it
        // set the item to undefined so it gets cleaned up
        ws_obj.setItem(this.state.focusIndex, undefined);
        var newFocusIndex = this.state.focusIndex;
        // Handle the special case of a bundle being added at the very end of the worksheet,
        // then cancelled (hit esc without saving). In this case we need to set the focus index
        // back one, to the last item in the worksheet. Otherwise the ghost of the cancelled item
        // retains focus and throws off the indices if insert is called again
        if(this.state.focusIndex === this.state.worksheet.items.length - 1){
            newFocusIndex--;
        }
        this.setState({
            worksheet: ws_obj.getState(),
            focusIndex: newFocusIndex
        });
    },
    deleteChecked: function(){
        var reactItems = this.refs;
        var worksheet = this.state.worksheet;
        var item_indexes =[];
        for(var k in reactItems){
            if(reactItems[k].state.checked){
                // we know the key of the item is the same as the index. We set it.
                // see WorksheetItemFactory. This will change but always match.
                var index = reactItems[k].props.key;
                item_indexes.push(index)
                // when called gets a edited flag, when you getState
            }
        }
        if(item_indexes.length){
            // only proceed if it turns out that one or more items were actually checked
            ws_obj.deleteItems(item_indexes)
            // does a clean before setting it's state and updating
            this.saveAndUpdateWorksheet();
            this.unCheckItems();
        }
    },
    unCheckItems: function(){
        var reactItems = this.refs;
        for(var k in reactItems){
            reactItems[k].setState({checked: false});
        }
    },
    insertItem: function(keyPressed){
        // insert before or after?
        var pos = keyPressed === 'i' ? 0 : 1;
        var newIndex = this.state.focusIndex + pos;
        var newItem = new WorksheetItem('', {}, 'markup');
        ws_obj.insertItem(newIndex, newItem);
        this.setState({
            worksheet: ws_obj.getState(),
            focusIndex: newIndex,
            editingIndex: newIndex
        });
        // Set the new_item flag so we know to add it to raw on save
        this.refs['item' + newIndex].setState({new_item: true});
        // we are inserting the item and switching to edit mode. The markup interface will handle
        // editing the raw/items if need and do the call back to save.
    },
    moveItem: function(delta){
        // delta is currently either +1 or -1
        // but in theory an item could be moved by any number of steps
        var oldIndex = this.state.focusIndex;
        var newIndex = oldIndex + delta;
        if(0 <= newIndex && newIndex < this.state.worksheet.items.length){
            ws_obj.moveItem(oldIndex, newIndex);
            this.setState({focusIndex: newIndex}, this.scrollToItem(newIndex));
            // wrap save in a debouce to slow it down
            // will happen after they stop moving items
            this.slowSave();

        }else {
            return false;
        }
    },
    setFocus: function(child){
        this.setState({focusIndex: child.props.key});
    },
    toggleRawMode: function(){
        if(this.state.rawMode){
            ws_obj.state.raw = $("#raw-textarea").val().split('\n');
            this.saveAndUpdateWorksheet();
        }
        this.setState({rawMode: !this.state.rawMode})
    },
    saveAndUpdateWorksheet: function(){
        $("#worksheet-message").hide();
        // does a save and a update
        ws_obj.saveWorksheet({
            success: function(data){
                this.fetch_and_update();
                if('error' in data){ // TEMP REMOVE FDC
                     $("#worksheet-message").html(data['error']).addClass('alert-box alert');
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(xhr, status, err);
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-box alert').show();
                } else if (xhr.status == 401){
                    $("#worksheet-message").html("You do not have permission to edit this worksheet.").addClass('alert-box alert').show();
                } else {
                    $("#worksheet-message").html("An error occurred: " + err.string() + "<br /> Please try refreshing the page.").addClass('alert-box alert').show();
                }
            }
        });
    },

    render: function(){
        var focusIndex = this.state.focusIndex;
        var editingIndex = this.state.editingIndex;
        var canEdit = this.props.canEdit;
        var className = canEdit ? 'editable' : '';
        var editPermission = ws_obj.getState().edit_permission;
        var editFeatures;
        var worksheet_items = [];
        var handleSave = this.saveItem;
        var setFocus = this.setFocus;
        var getRaw = ws_obj.getRaw();
        if(editPermission){
            var editStatus = canEdit ? 'on' : 'off';
            var editFeatures =
                    <div className="edit-features">
                        <div>
                            <label htmlFor="editing">
                                <input type="checkbox" checked={this.props.canEdit} name="editing" id="editing" onChange={this.props.toggleEditing} /> Editing {editStatus}
                            </label>
                        </div>
                        <div>
                            <label htmlFor="rawMode">
                                <input type="checkbox" checked={this.state.rawMode} name="rawMode" id="rawMode" onChange={this.toggleRawMode} /> Raw mode
                            </label>
                        </div>
                    </div>
        }
        if(ws_obj.state.items.length){
            ws_obj.state.items.forEach(function(item, i){
                var ref = 'item' + i;
                var focused = i === focusIndex;
                var editing = i === editingIndex;
                worksheet_items.push(WorksheetItemFactory(item, ref, focused, editing, i, handleSave, setFocus, canEdit))
            });
        }else {
            $('.empty-worksheet').fadeIn();
        }
        var worksheet_items_display;
        if(this.state.rawMode){
            // http://facebook.github.io/react/docs/forms.html#why-textarea-value
            worksheet_items_display = <textarea id="raw-textarea" defaultValue={getRaw.content} rows={getRaw.lines}  ref="textarea" />;
        }else {
            worksheet_items_display = worksheet_items;
        }
        return (
            <div id="worksheet_content" className={className}>
                <div className="row header-row">
                    <div className="large-6 columns">
                        <div className="worksheet-name">
                            <h1 className="worksheet-icon">{ws_obj.state.name}</h1>
                            <div className="worksheet-author">{ws_obj.state.owner}</div>
                        </div>
                    </div>
                    <div className="large-6 columns controls">
                        <div>
                            <a href="#" className="glossary-link" data-reveal-id="glossaryModal"><code>?</code> Keyboard Shortcuts</a>
                        </div>
                        {editFeatures}
                    </div>
                    <hr />
                </div>
                {worksheet_items_display}
                <p className="empty-worksheet">This worksheet is empty</p>
            </div>
        )
    }
});


var WorksheetItemFactory = function(item, ref, focused, editing, i, handleSave, setFocus, canEdit){
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} handleSave={handleSave} setFocus={setFocus} />
            break;
        case 'inline':
            return <InlineBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        case 'table':
            return <TableBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} handleSave={handleSave} setFocus={setFocus} />
            break;
        case 'contents':
            return <ContentsBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        case 'html':
            return <HTMLBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        case 'record':
            return <RecordBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        case 'image':
            return <ImageBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        case 'worksheet':
            return <WorksheetBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
            break;
        default:  // something new or something we dont yet handle
            return (
                <div>
                    <strong>
                        {item.state.mode}
                    </strong>
                </div>
            )
    }
}


var worksheet_react = <Worksheet />;
React.renderComponent(worksheet_react, document.getElementById('worksheet_container'));
