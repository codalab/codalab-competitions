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
    getInitialState: function(){
        return {
            activeComponent: 'list',
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
        $('html,body').animate({scrollTop: 0}, 250);
    },
    handleSearchBlur: function(event){
        $('#search').select2('close');
        this.setState({activeComponent:'list'});
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var activeComponent = this.refs[this.state.activeComponent];
        if(key === 'fslash' && event.shiftKey){
            event.preventDefault();
            this.handleSearchBlur();
            $('#glossaryModal').foundation('reveal', 'open');
        }else if(activeComponent.hasOwnProperty('handleKeydown')){
            activeComponent.handleKeydown(event);
        }else {
            return true;
        }
    },
    render: function(){
        var canEdit = ws_obj.getState().edit_permission;
        return (
            <div id="worksheet">
                <WorksheetSearch handleFocus={this.handleSearchFocus} handleBlur={this.handleSearchBlur} ref={"search"} active={this.state.activeComponent=='search'}/>
                <WorksheetItemList ref={"list"} active={this.state.activeComponent=='list'} canEdit={canEdit} />
            </div>
        )
    }
});

var WorksheetSearch = React.createClass({
    mixins: [Select2SearchMixin],
    handleKeydown: function(event){
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
            worksheet: {
                last_item_id: 0,
                name: '',
                owner: null,
                owner_id: 0,
                uuid: 0,
                items: []
            }
        }
    },
    componentDidMount: function() {
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide().removeClass('alert-box alert');
                if(this.isMounted()){
                    this.setState({worksheet: ws_obj.getState()});
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.").addClass('alert-box alert');
                } else {
                    $("#worksheet-message").html("An error occurred. Please try refreshing the page.").addClass('alert-box alert');
                }
                $('#worksheet_container').hide();
            }.bind(this)
        });
    },
    componentDidUpdate: function(){
        if(!this.state.worksheet.items.length){
            $('.empty-worksheet').fadeIn('fast');
        }
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var fIndex = this.state.focusIndex;
        var eIndex = this.state.editingIndex;
        var focusedItem = this.refs['item' + fIndex];
        if(focusedItem && focusedItem.hasOwnProperty('keysToHandle') && focusedItem.keysToHandle().indexOf(key) != -1){
            focusedItem.handleKeyboardShortcuts(event);
        }else if(focusedItem && fIndex === eIndex && focusedItem.hasOwnProperty('handleKeydown')){
            focusedItem.handleKeydown(event);
        }else {
            switch (key) {
                case 'fslash':
                    event.preventDefault();
                    this._owner.setState({activeComponent: 'search'});
                    break;
                case 'up':
                case 'k':
                    event.preventDefault();
                    if(event.shiftKey){
                        this.moveItem(-1);
                    }else {
                        if(fIndex <= 0){
                            fIndex = -1;
                        }else {
                            fIndex = Math.max(this.state.focusIndex - 1, 0);
                        }
                        this.setState({focusIndex: fIndex});
                        this.scrollToItem(fIndex);
                    }
                    break;
                case 'down':
                case 'j':
                    event.preventDefault();
                    if(event.shiftKey){
                        this.moveItem(1);
                    }else {
                        fIndex = Math.min(this.state.focusIndex + 1, document.querySelectorAll('#worksheet_content .ws-item').length - 1);
                        this.setState({focusIndex: fIndex});
                        this.scrollToItem(fIndex);
                    }
                    break;
                case 'e':
                    if(this.props.canEdit){
                        event.preventDefault();
                        this.setState({editingIndex: fIndex});
                    }
                    break;
                case 'x':
                    event.preventDefault();
                    if(focusedItem){
                        focusedItem.setState({checked: !focusedItem.state.checked});
                    }
                    break;
                case 'd':
                    if(this.props.canEdit){
                        event.preventDefault();
                        this.deleteChecked();
                    }
                    break;
                case 'i':
                    if(this.props.canEdit){
                        event.preventDefault();
                        this.insertItem(key);
                    }
                    break;
                case 'a':
                    if(event.shiftKey && this.props.canEdit){
                        event.preventDefault();
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
            offsetTop = this.refs['item' + index].getDOMNode().offsetTop - 100;
        }
        $('html,body').animate({scrollTop: offsetTop}, 250);
    },
    saveItem: function(textarea){
        var item = ws_obj.state.items[this.state.editingIndex];
        item.state.interpreted = textarea.value;
        var unconsolidated = ws_obj.getState();
        var consolidated = ws_obj.consolidateMarkdownBundles(unconsolidated.items);
        ws_obj.state.items = consolidated;
        this.setState({
            editingIndex: -1,
            worksheet: ws_obj.getState()
        });
        console.log('------ save the worksheet here ------');
    },
    unInsert: function(){
        ws_obj.setItem(this.state.focusIndex, undefined);
        this.setState({worksheet: ws_obj.getState()});
    },
    deleteChecked: function(){
        var reactItems = this.refs;
        var worksheet = this.state.worksheet;
        for(var k in reactItems){
            if(reactItems[k].state.checked){
                // we know the key of the item is the same as the index. We set it. 
                // see WorksheetItemFactory. This will change but always match. 
                var index = reactItems[k].props.key; 
                ws_obj.setItem(index, undefined) 
                // when called gets a edited flag, when you getState
                // does a clean before setting it's state
            }
        }
        this.setState({worksheet: ws_obj.getState()});
        this.unCheckItems();
    },
    unCheckItems: function(){
        var reactItems = this.refs;
        for(var k in reactItems){
            reactItems[k].setState({checked: false});
        }
    },
    insertItem: function(keyPressed){
        var pos = keyPressed === 'i' ? 0 : 1;
        var newIndex = this.state.focusIndex + pos;
        var newItem = new WorksheetItem('', {}, 'markup');
        ws_obj.insertItem(newIndex, newItem);
        this.setState({
            worksheet: ws_obj.getState(),
            focusIndex: newIndex,
            editingIndex: newIndex
        });
    },
    moveItem: function(delta){
        var oldIndex = this.state.focusIndex;
        var newIndex = oldIndex + delta;
        if(0 <= newIndex && newIndex < this.state.worksheet.items.length){
            ws_obj.moveItem(oldIndex, newIndex);
            this.setState({focusIndex: newIndex}, this.scrollToItem(newIndex));
        }else {
            return false;
        }
    },
    setFocus: function(child){
        this.setState({focusIndex: child.props.key});
    },
    render: function(){
        var focusIndex = this.state.focusIndex;
        var editingIndex = this.state.editingIndex;
        var canEdit = this.props.canEdit;
        var className = canEdit ? 'editable' : '';
        var worksheet_items = [];
        var handleSave = this.saveItem;
        var setFocus = this.setFocus;
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
        return (
            <div id="worksheet_content" className={className}>
                <a href="#" className="glossary-link" data-reveal-id="glossaryModal"><code>?</code> Keyboard Shortcuts</a>
                <div className="worksheet-name">
                    <h1 className="worksheet-icon">{ws_obj.state.name}</h1>
                    <div className="worksheet-author">{ws_obj.state.owner}</div>
                {
                /*  COMMENTING OUT EXPORT BUTTON UNTIL WE DETERMINE ASSOCIATED ACTION
                <a href="#" className="right">
                <button className="med button">Export</button>
                </a<
                */
                }
                </div>
                {worksheet_items}
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
            return <TableBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
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
        case 'worksheet':
            return <WorksheetBundle key={i} item={item} ref={ref} focused={focused} editing={editing} canEdit={canEdit} setFocus={setFocus} />
        default:
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
