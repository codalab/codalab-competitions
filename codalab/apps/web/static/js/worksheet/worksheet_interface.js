/** @jsx React.DOM */
var isMac = window.navigator.platform.toString().indexOf('Mac') >= 0;

var keyMap = {
    13: "enter",
    27: "esc",
    69: "e",
    74: "j",
    75: "k"
};

var Worksheet = React.createClass({
    getInitialState: function(){
        ws_obj.state.focusIndex = 0;
        ws_obj.state.editingIndex = -1;
        ws_obj.state.keyboardShortcuts = true;
        return ws_obj.state;
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.handleKeyboardShortcuts);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.handleKeyboardShortcuts);
    },
    handleKeyboardShortcuts: function(event) {
        if(this.state.keyboardShortcuts){
            var key = keyMap[event.keyCode];
            var index = this.state.focusIndex;
            if(typeof key !== 'undefined'){
                switch (key) {
                    case 'k':
                        event.preventDefault();
                        index = Math.max(this.state.focusIndex - 1, 0);
                        this.setState({focusIndex: index});
                        break;
                    case 'j':
                        event.preventDefault();
                        index = Math.min(this.state.focusIndex + 1, this.state.items.length - 1);
                        this.setState({focusIndex: index});
                        break;
                    case 'e':
                        event.preventDefault();
                        this.setState({editingIndex: index});
                        break;
                    default:
                        return true;
                    }
            } else {
                return true;
            }
        } else {
        return true;
        }
    },
    toggleKeyboardShortcuts: function(event, direction){
        if(typeof direction == 'undefined'){
            this.setState({keyboardShortcuts: !this.state.keyboardShortcuts});
        }else {
            this.setState({keyboardShortcuts: direction});
        }
        console.log('keyboard shortuts: ' + this.state.keyboardShortcuts ? 'on' : 'off');
    },
    exitEditMode: function(){
        this.setState({editingIndex:-1, keyboardShortcuts: true});
    },
    saveEditedItem: function(){
        var itemNode = this.refs['item' + this.state.focusIndex].getDOMNode();
        var newContent = itemNode.children[0].value;
        alert('Save this content: ' + newContent);
    },
    componentWillMount: function() {  // once on the page lets get the ws info
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide();
                // as successful fetch will update our state data on the ws_obj.
                this.setState(ws_obj.state);
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
        var itemNode = this.refs['item' + this.state.focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    render: function() {
        var focusIndex = this.state.focusIndex;
        var editingIndex = this.state.editingIndex;
        var keyboardShortcutsClass = this.state.keyboardShortcuts ? 'shortcuts-on' : 'shortcuts-off';
        var onExitEdit = this.exitEditMode;
        var listBundles = this.state.items.map(function(item, index) {
            var focused = focusIndex === index;
            var editing = editingIndex === index;
            var itemID = 'item' + index;
            return <WorksheetItemFactory item={item} focused={focused} ref={itemID} editing={editing} key={index} onExitEdit={onExitEdit} />;
        });
         // listBundles is now a list of react components that each el is
        return (
            <div id="worksheet-content" className={keyboardShortcutsClass}>
                <div className="worksheet-name">
                    <h1 className="worksheet-icon">{this.state.name}</h1>
                    <div className="worksheet-author">{this.state.owner}</div>
                    <label>
                        <input type="checkbox" onChange={this.toggleKeyboardShortcuts} checked={this.state.keyboardShortcuts} />
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
                <div>{listBundles}</div>
            </div>
        );
    },
});


var WorksheetItemFactory = React.createClass({
    render: function() {
        var item          = this.props.item;
        var focused       = this.props.focused ? ' focused' : '';
        var editing       = this.props.editing;
        var itemIndex     = this.props.ref;
        var mode          = item.state.mode;
        var classString   = 'type-' + mode + focused;
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
            <div className={classString} key={this.props.ref} editing={this.props.editing}>
                {rendered_bundle}
            </div>
        );
    } // end of render function
}); // end of WorksheetItemFactory


var MarkdownBundle = React.createClass({
    getInitialState: function(){
        this.props.item.state.lines = this.props.item.state.interpreted.split(/\r\n|\r|\n/).length;
        return this.props.item.state;
    },
    handleMarkdownKeyboardShortcuts: function(event){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    this._owner.props.onExitEdit();
                    break;
                case 'enter':
                    if(event.ctrlKey || (isMac && event.metaKey)){
                        event.preventDefault();
                        this.saveEditedItem(event.target);
                    }
                    break;
                default:
                    return true;
            }
        } else {
            return true;
        }
    },
    saveEditedItem: function(textarea){
        console.log('------ save the worksheet here ------');
        var newVal = textarea.value;
        this.state.interpreted = newVal;
        // Callback to <Worksheet /> to reset editing
        this._owner.props.onExitEdit();
    },
    componentDidMount: function() {
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
    },
    componentDidUpdate: function(){
        if(this.props.editing){
            this.getDOMNode().focus();
        }
    },
    render: function() {
        if (this.props.editing){
            return(
                <textarea rows={this.state.lines} onKeyDown={this.handleMarkdownKeyboardShortcuts}>{this.state.interpreted}</textarea>
            )
        }else {
        var text = marked(this.state.interpreted);
        // create a string of html for innerHTML rendering
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        return(
            <span dangerouslySetInnerHTML={{__html: text}} onKeyDown={this.handleMarkdownKeyboardShortcuts} />
        );
        }
    } // end of render function
}); //end of  MarkdownBundle


var InlineBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        return(
            <em>
                {this.state.interpreted}
            </em>
        );
    } // end of render function
}); //end of  InlineBundle

var TableBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        // var info = this.props.info;  //shortcut naming
        var bundle_url = "/bundles/" + this.state.bundle_info.uuid + "/"

        var header_items = this.state.interpreted[0]
        var header_html = header_items.map(function(item, index) {
                return <th key={index}> {item} </th>;
            });

        var row_items = this.state.interpreted[1];
        var body_rows_html = row_items.map(function(row_item, index) {
            var row_cells = header_items.map(function(header_key, index){
                if(header_key == 'name'){
                    return (
                        <td key={index}>
                            <a href={bundle_url} className="bundle-link">
                                {row_item[header_key]}
                            </a>
                        </td>
                    )
                } else {
                    return <td key={index}> {row_item[header_key]}</td>
                }
            });
            return (
                <tr key={index}>
                    {row_cells}
                </tr>
            );
        });

        return(
            <table className="table table-responsive">
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {body_rows_html}
                </tbody>
            </table>
        );
    } // end of render function
}); //end of  InlineBundle

var worksheet_react = <Worksheet />;
React.renderComponent(worksheet_react, document.getElementById('worksheet-body'));
