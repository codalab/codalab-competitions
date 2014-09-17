/** @jsx React.DOM */

var keyMap = {
    13: "enter",
    27: "esc",
    69: "e",
    38: "up",
    40: "down",
    68: "d",
    74: "j",
    75: "k",
    88: "x",
    220: "bslash"
};

var Worksheet = React.createClass({
    getInitialState: function(){
        return {
            activeComponent: 'list',
            worksheetItems: []
        }
    },
    componentWillMount: function() {
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide();
                this.setState({worksheetItems: data});
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
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.handleKeydown);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown');
    },
    handleFocus: function(event){
        console.log('handlefocus');
        if(event.type=="focus"){
            this.setState({activeComponent:'search'});
        }else if(event.type=="blur"){
            this.setState({activeComponent:'list'});
        }
        console.log('set active component to ' + this.state.activeComponent);
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var activeComponent = this.refs[this.state.activeComponent];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'bslash':
                    event.preventDefault();
                    this.refs.search.getDOMNode().focus();
                    break;
                default:
                    if(activeComponent.hasOwnProperty('handleKeydown')){
                        activeComponent.handleKeydown(event);
                    }else {
                        return true;
                    }
            }
        }
    },
    render: function(){
        return (
            <div id="worksheet">
                <div id="ws_search">
                    <WorksheetSearch handleFocus={this.handleFocus} ref={"search"} active={this.state.activeComponent=='search'}/>
                </div>
                <WorksheetItems items={this.state.worksheetItems} ref={"list"} active={this.state.activeComponent=='list'} />
            </div>
        )
    }
});

var WorksheetSearch = React.createClass({
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var focusedItem = this.refs[this.state.focus];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    event.preventDefault();
                    this.getDOMNode().blur();
            }
        }
    },
    render: function(){
        return (
            <input type="text" placeholder="General search" onFocus={this.props.handleFocus} onBlur={this.props.handleFocus} />
        )
    }
});

var WorksheetItems = React.createClass({
    getInitialState: function(){
        return {
            focusIndex: -1,
            editingIndex: -1 
        }
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            var fIndex = this.state.focusIndex;
            var eIndex = this.state.editingIndex;
            var focusedItem = this.refs['item' + fIndex];
            if(focusedItem && focusedItem.hasOwnProperty('handleKeyboardShortcuts')){
                focusedItem.handleKeyboardShortcuts(event);
            }
            else if(focusedItem && fIndex === eIndex && focusedItem.hasOwnProperty('handleKeydown')){
                focusedItem.handleKeydown(event);
            } else {
                switch (key) {
                    case 'up':
                    case 'k':
                        event.preventDefault();
                        fIndex = Math.max(this.state.focusIndex - 1, 0);
                        this.setState({focusIndex: fIndex});
                        break;
                    case 'down':
                    case 'j':
                        event.preventDefault();
                        fIndex = Math.min(this.state.focusIndex + 1, this.props.items.length - 1);
                        this.setState({focusIndex: fIndex});
                        break;
                    case 'e':
                        event.preventDefault();
                        this.setState({editingIndex: fIndex});
                        break;
                }
            }
        }
    },
    render: function(){
        var focusIndex = this.state.focusIndex;
        var editingIndex = this.state.editingIndex;
        var worksheet_items = []
        this.props.items.forEach(function(item, i){
            var ref = 'item' + i;
            var focused = i === focusIndex;
            var editing = i === editingIndex;
            worksheet_items.push(WorksheetItemFactory(item, ref, focused, editing))
        });
        return (
            <div id="worksheet_content">
                {worksheet_items}
            </div>
        )
    }
});

var WorksheetItemFactory = function(item, ref, focused, editing){
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'inline':
            return <InlineBundle item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'table':
            return <TableBundle item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'contents':
            return <ContentsBundle item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'record':
            return <RecordBundle item={item} ref={ref} focused={focused} editing={editing} />
            break;
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
