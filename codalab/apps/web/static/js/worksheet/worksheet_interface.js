/** @jsx React.DOM */
var isMac = window.navigator.platform.toString().indexOf('Mac') >= 0;

var keyMap = {
    13: "enter",
    27: "esc",
    69: "e",
    38: "up",
    40: "down",
    74: "j",
    75: "k",
    88: "x"
};

var Worksheet = React.createClass({
    getInitialState: function(){
        return {
            content: ws_obj.state,
            interactions: ws_interactions.state
        };
    },
    bindEvents: function(){
        var _this = this; // maintain context
        // listen for all keyboard shortcuts
        window.addEventListener('keydown', this.handleKeyboardShortcuts);
        // register a listener with the broker
        ws_broker.register('updateState', function(){
            // when the broker says to update our state, do it
            _this.updateState();
        });
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.handleKeyboardShortcuts);
        ws_broker.unregister('updateState', function(){
            _this.updateState();
        });
    },
    updateState: function(){
        // thanks to React, this is actually very efficient. Only the parts of the state that are
        // affected will update themselves, even though we appear to be resetting the whole object.
        this.setState({
            content:ws_obj.state,
            interactions:ws_interactions.state
        });
    },
    handleKeyboardShortcuts: function(event) {
        var content = this.state.content;
        var focusedItem = content.items[this.state.interactions.worksheetFocusIndex];
        if(this.state.interactions.worksheetKeyboardShortcuts && focusedItem.state.mode !== 'table'){
            var key = keyMap[event.keyCode];
            var index = this.state.interactions.worksheetFocusIndex;
            if(typeof key !== 'undefined'){
                switch (key) {
                    case 'up':
                    case 'k':
                        event.preventDefault();
                        index = Math.max(this.state.interactions.worksheetFocusIndex - 1, 0);
                        ws_interactions.state.worksheetFocusIndex = index;
                        break;
                    case 'down':
                    case 'j':
                        event.preventDefault();
                        index = Math.min(this.state.interactions.worksheetFocusIndex + 1, content.items.length - 1);
                        ws_interactions.state.worksheetFocusIndex = index;
                        break;
                    case 'e':
                        event.preventDefault();
                        ws_interactions.state.worksheetEditingIndex = index;
                        // TODO: we only need to disable keyboard shortcuts if the focused item CAN be edited.
                        // Is there a better way to do this?
                        if(focusedItem.state.mode == 'markup'){
                            this.toggleKeyboardShortcuts(false);
                        }
                        break;
                    default:
                        return true;
                    }
                this.updateState();
            } else {
                return true;
            }
        } else {
            if(focusedItem.state.mode == 'table'){
                focusedItem.state.handleKeyboardShortcuts(event);
            }
            return true;
        }
    },
    toggleKeyboardShortcuts: function(event, direction){
        if(typeof direction == 'undefined'){
            ws_interactions.state.worksheetKeyboardShortcuts = !ws_interactions.state.worksheetKeyboardShortcuts;
        }else {
            ws_interactions.state.worksheetKeyboardShortcuts = direction;
        }
        this.updateState();
    },
    exitEditMode: function(){
        ws_interactions.state.worksheetEditingIndex = -1;
        ws_interactions.state.worksheetKeyboardShortcuts = true;
        this.updateState();
    },
    saveEditedItem: function(){
        var itemNode = this.refs['item' + this.state.interactions.worksheetFocusIndex].getDOMNode();
        var newContent = itemNode.children[0].value;
        alert('Save this content: ' + newContent);
    },
    componentWillMount: function() {  // once on the page lets get the ws info
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide();
                // as successful fetch will update our state data on the ws_obj.
                this.updateState();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.");
                } else {
                    $("#worksheet-message").html("An error occurred. Please try refreshing the page.");
                }
            }.bind(this)
        });
        this.bindEvents();
    },
    componentDidUpdate: function(){
        var focusIndex = this.state.interactions.worksheetFocusIndex; // shortcut
        var itemNode = this.refs['item' + focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    render: function() {
        var content = this.state.content;
        var focusIndex = this.state.interactions.worksheetFocusIndex;
        var editingIndex = this.state.interactions.worksheetEditingIndex;
        var keyboardShortcutsClass = this.state.interactions.worksheetKeyboardShortcuts ? 'shortcuts-on' : 'shortcuts-off';
        var onExitEdit = this.exitEditMode;
        var listBundles = this.state.content.items.map(function(item, index) {
            var focused = focusIndex === index;
            var editing = editingIndex === index;
            var itemID = 'item' + index;
            return <WorksheetItemFactory item={item} focused={focused} ref={itemID} editing={editing} key={index} onExitEdit={onExitEdit} />;
        });
        // listBundles is now a list of react components that each el is
        return (
            <div id="worksheet-content" className={keyboardShortcutsClass}>
                <div className="worksheet-name">
                    <h1 className="worksheet-icon">{this.state.content.name}</h1>
                    <div className="worksheet-author">{this.state.content.owner}</div>
                    <label>
                        <input type="checkbox" onChange={this.toggleKeyboardShortcuts} checked={this.state.interactions.worksheetKeyboardShortcuts} />
                            Keyboard Shortcuts <small> for example on/off </small>
                    </label>
                    {
                        /*  COMMENTING OUT EXPORT BUTTON UNTIL WE DETERMINE ASSOCIATED ACTION
                            <a href="#" className="right">
                                <button className="med button">Export</button>
                            </a<
                        */
                    }
                </div>
                <div className="worksheet-items">{listBundles}</div>
            </div>
        );
    },
});


var WorksheetItemFactory = React.createClass({
    focusOnThis: function(){
        ws_interactions.state.worksheetFocusIndex = this.props.key;
        this._owner.updateState();
    },
    render: function() {
        var item          = this.props.item;
        var focusedClass  = this.props.focused ? ' focused' : '';
        var editing       = this.props.editing;
        var itemIndex     = this.props.ref;
        var mode          = item.state.mode;
        var classString   = 'type-' + mode + focusedClass;
        var rendered_bundle = (
                <div> </div>
            );
        //based on the mode create the correct isolated component
        switch (mode) {
            case 'markup':
                rendered_bundle = (
                    <MarkdownBundle item={item} editing={editing} />
                );
                break;

            case 'inline':
                rendered_bundle = (
                    <InlineBundle item={item} />
                );
                break;

            case 'table':
                rendered_bundle = (
                    <TableBundle item={item} />
                );
                break;

            default: // render things we don't know in bold for now
                rendered_bundle = (
                    <div>
                        <strong>{ mode }</strong>
                    </div>
                )
                break;
        }
        return(
            <div className={classString} key={this.props.ref} editing={this.props.editing} onClick={this.focusOnThis}>
                {rendered_bundle}
            </div>
        );
    } // end of render function
}); // end of WorksheetItemFactory


var worksheet_react = <Worksheet />;
React.renderComponent(worksheet_react, document.getElementById('worksheet-body'));
