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
        $('body').addClass('ws-interface');
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
            $('#glossaryModal').modal('show');
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
                <div className="container">
                    <WorksheetItemList ref={"list"} active={this.state.activeComponent=='list'} canEdit={canEdit} toggleEditing={this.toggleEditing} />
                </div>
            </div>
        )
    }
});

var WorksheetSearch = React.createClass({
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        _this = this;
        // get our static list of commands and store it in this var
        var optionsList = ws_actions.getCommands();
        $('#search').select2({
            multiple:true,
            minimumInputLength: 3,
            // Note: it's totally possible to dynamically change the minimum input length, ie, for it to be zero
            // initially and 3 when we're going to make an ajax call, but it requires changing or
            // overwriting the select2 plugin code.
            formatSelection: function(item){
                return item.id
                // When you search for a command, you should see its name and a description of what it
                // does. This comes from the command's helpText in the command dict.
                // But after you make a selection, we only want to show the relevant command in the command line
            },
            // custom query method, called on every keystroke over the min length
            // see http://ivaynberg.github.io/select2/#doc-query
            query: function(query){

                // Select2 is masking the actual #search field. Its value only changes when something new is entered
                // via select2. So when the value of #search changes, we know we need to reevaluate the context
                // in which select2 is being used (eg, we've gone from entering a command to looking up a bundle)
                var input = query.element.val();

                // if there's something in the commandline AND
                // if the last thing entered in the command line is in our known list of commands,
                // we know we need to start hitting the API for results
                if(input.length && ws_actions.commands.hasOwnProperty(_.last(input.split(',')))){
                    // get our action object that tells us what to do (ajax url)
                    var command = ws_actions.commands[input];
                    console.log('searching for options related to the "' + input + '" command with the term "' + query.term + '"');
                    $.ajax({
                        type:'GET',
                        url: command.url,
                        dataType: 'json',
                        data: {
                            search_string: query.term // built into the query object
                        },
                        success: function(data, status, jqXHR){
                            // select2 wants its options in a certain format, so let's make a new
                            // list it will like
                            newOptions = [];
                            for(var k in data){
                                newOptions.push({
                                    'id': k,
                                    'text': data[k].metadata.name + ' | ' + k
                                });
                            };
                            console.log(newOptions.length + ' results');
                            // callback is also built into the query object. It expects a list of
                            // results. See http://ivaynberg.github.io/select2/#doc-query again.
                            query.callback({
                                results: newOptions
                            });
                        },
                        error: function(jqHXR, status, error){
                            console.error(status + ': ' + error);
                        }
                    });
                }else {
                    // either a command hasn't been entered or it wasn't one we support, so
                    // let's make a list of our known commands
                    console.log('searching commands...');
                    var matchedOptions = []
                    optionsList.map(function(item){
                        // we need to make our own matcher function because we're doing this
                        // custom thing. This is just a reimplementation of select2's default
                        // matcher. See http://ivaynberg.github.io/select2/#doc-matcher
                        if(item.id.toUpperCase().indexOf(query.term.toUpperCase())>=0){
                            matchedOptions.push(item);
                        }
                    });
                    console.log(matchedOptions.length + ' results');
                    // now pass back these results the same way we did the ajax ones
                    query.callback({
                        results: matchedOptions
                    });
                }
            }
        }).on('select2-open', function(){
            // because select2 is masking the actual #search field, we need to manually trigger
            // its focus event when select2 is invoked
            _this.props.handleFocus();
        });

        $('#s2id_search').on('keydown', '.select2-input', function(e){
            // add some custom key events for working with the search bar
            switch(e.keyCode){
                case 9:
                    // usually the Tab key would move focus off the search input, so
                    // we want to prevent that
                    e.preventDefault();
                    break;
                case 13:
                    // cmd-enter or ctrl-enter triggers execution of whatever is
                    // in the search input
                    if(e.ctrlKey || e.metaKey){
                        e.preventDefault();
                        _this.executeCommands();
                    }
                    break;
                default:
                    return true;
            }
        });
    },
    componentWillUnmount: function(){
        // when the component unmounts, destroy the select2 instance
        $('#search').select2('destroy');
    },
    componentDidUpdate: function(){
        if(this.props.active){
            $('#s2id_autogen1').focus();
        }else {
            $('#s2id_autogen1').blur();
        }
    },
    executeCommands: function(){
        // parse and execute the contents of the search input
        var input = $('#search').select2('val'); // this comes in as an array
        // customization can be done here, depending on the desired syntax of commands.
        // currently, this just calls all of the functions named in the input
        var command = input[0];
        if(ws_actions.commands.hasOwnProperty(command)){
            ws_actions[ws_actions.commands[command].functionName](input, ws_actions.commands[command]);
        } else {
            console.error('The command \'' + command + '\' was not recognized');
        }
    },
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
                <div className="container">
                    <div className="input-group">
                        <input id="search" type="hidden" placeholder="General search/command line" onFocus={this.props.handleFocus} onBlur={this.props.handleBlur} />
                        <span className="input-group-btn">
                            <button className="btn btn-default" type="button" onClick={this.executeCommands}>Execute</button>
                        </span>
                    </div>
                </div>
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
            checkboxEnabled: true,
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
                $("#worksheet-message").hide().removeClass('alert-danger alert');
                if(this.isMounted()){
                    this.setState({worksheet: ws_obj.getState()});
                }
                $('#update_progress').hide();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(ws_obj.url, status, err);
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-danger alert');
                } else {
                    $("#worksheet-message").html("An error occurred: <code>'" + status + "' " + err + " (" + xhr.status + ")</code>. Please try refreshing the page.").addClass('alert-danger alert');
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
                            $('body').stop(true).animate({scrollTop: 0}, 250);
                        }else {
                            fIndex = Math.max(this.state.focusIndex - 1, 0);
                        }
                        this.setFocus(fIndex);
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
                        this.setFocus(fIndex);
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
            var item = this.refs['item' + index];
            var node = item.getDOMNode();
            var offset = node.offsetTop;
            if(this.state.worksheet.items[index].state.mode === 'table' &&
                keyMap[event.keyCode] == 'k' ||
                keyMap[event.keyCode] == 'up' ){
                offset += ($(node).innerHeight() - 30);
            }
            // find the item's position on the page, and offset it from the top of the viewport
            offsetTop = offset - 200;
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
    setFocus: function(index){
        this.setState({focusIndex: index});
        if(index >= 0){
            var mode = ws_obj.state.items[index].state.mode;
            if(mode === 'table'){
                this.toggleCheckboxEnable(false);
            }else {
                this.toggleCheckboxEnable(true);
            }
            this.scrollToItem(index);
        }
    },
    toggleRawMode: function(){
        if(this.state.rawMode){
            ws_obj.state.raw = $("#raw-textarea").val().split('\n');
            this.saveAndUpdateWorksheet();
        }
        this.setState({rawMode: !this.state.rawMode})
    },
    toggleCheckboxEnable: function(enabled){
        this.setState({checkboxEnabled: enabled})
    },
    saveAndUpdateWorksheet: function(){
        $("#worksheet-message").hide();
        // does a save and a update
        ws_obj.saveWorksheet({
            success: function(data){
                this.fetch_and_update();
                if('error' in data){ // TEMP REMOVE FDC
                     $("#worksheet-message").html(data['error']).addClass('alert-danger alert');
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(xhr, status, err);
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-danger alert').show();
                } else if (xhr.status == 401){
                    $("#worksheet-message").html("You do not have permission to edit this worksheet.").addClass('alert-danger alert').show();
                } else {
                    $("#worksheet-message").html("An error occurred: " + err.string() + "<br /> Please try refreshing the page.").addClass('alert-danger alert').show();
                }
            }
        });
    },

    render: function(){
        var focusIndex = this.state.focusIndex;
        var editingIndex = this.state.editingIndex;
        var canEdit = this.props.canEdit;
        var checkboxEnabled = this.state.checkboxEnabled;
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
                worksheet_items.push(WorksheetItemFactory(item, ref, focused, editing, i, handleSave, setFocus, canEdit, checkboxEnabled))
            });
        }else {
            $('.empty-worksheet').fadeIn();
        }
        var worksheet_items_display;
        if(this.state.rawMode){
            // http://facebook.github.io/react/docs/forms.html#why-textarea-value
            worksheet_items_display = <textarea id="raw-textarea" className="form-control" defaultValue={getRaw.content} rows={getRaw.lines} ref="textarea" />;
        }else {
            worksheet_items_display = worksheet_items;
        }
        return (
            <div id="worksheet_content" className={className}>
                <div className="header-row">
                    <div className="row">
                        <div className="col-sm-6">
                            <div className="worksheet-name">
                                <h1 className="worksheet-icon">{ws_obj.state.name}</h1>
                                <div className="worksheet-author">{ws_obj.state.owner}</div>
                            </div>
                        </div>
                        <div className="col-sm-6">
                            <div className="controls">
                                <a href="#" data-toggle="modal" data-target="#glossaryModal" className="glossary-link"><code>?</code> Keyboard Shortcuts</a>
                                {editFeatures}
                            </div>
                        </div>
                    </div>
                    <hr />
                </div>
                {worksheet_items_display}
                <p className="empty-worksheet">This worksheet is empty</p>
            </div>
        )
    }
});


var WorksheetItemFactory = function(item, ref, focused, editing, i, handleSave, setFocus, canEdit, checkboxEnabled){
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} handleSave={handleSave} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'inline':
            return <InlineBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'table':
            return <TableBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} handleSave={handleSave} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'contents':
            return <ContentsBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'html':
            return <HTMLBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'record':
            return <RecordBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'image':
            return <ImageBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
            break;
        case 'worksheet':
            return <WorksheetBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} checkboxEnabled={checkboxEnabled} />
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
