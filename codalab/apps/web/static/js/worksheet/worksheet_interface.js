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
    handleSearchFocus: function(event){
        this.setState({activeComponent:'search'});
        window.scrollTo(0, 0);
    },
    handleSearchBlur: function(event){
        this.setState({activeComponent:'list'});
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        var activeComponent = this.refs[this.state.activeComponent];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'fslash':
                    event.preventDefault();
                    this.handleSearchFocus();
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
                <WorksheetSearch handleFocus={this.handleSearchFocus} handleBlur={this.handleSearchBlur} ref={"search"} active={this.state.activeComponent=='search'}/>
                <WorksheetItems items={this.state.worksheetItems} ref={"list"} active={this.state.activeComponent=='list'} />
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

var WorksheetItems = React.createClass({
    getInitialState: function(){
        return {
            focusIndex: -1,
            editingIndex: -1 
        }
    },
    componentDidUpdate: function(){
        if(this.props.items.length){
            var fIndex = this.state.focusIndex;
            if(fIndex >= 0){
                var itemNode = this.refs['item' + fIndex].getDOMNode();
                if(itemNode.offsetTop > window.innerHeight / 2){
                    window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
                }
            }
            else {
                return false;
            }
        }
        else {
            $('.empty-worksheet').fadeIn('fast');
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
                        if(fIndex <= 0){
                            fIndex = -1;
                        }else {
                            fIndex = Math.max(this.state.focusIndex - 1, 0);
                        }
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
            worksheet_items.push(WorksheetItemFactory(item, ref, focused, editing, i))
        });
        return (
            <div id="worksheet_content">
                {worksheet_items}
            </div>
        )
    }
});

var WorksheetItemFactory = function(item, ref, focused, editing, i){
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle key={i} item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'inline':
            return <InlineBundle key={i} item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'table':
            return <TableBundle key={i} item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'contents':
            return <ContentsBundle key={i} item={item} ref={ref} focused={focused} editing={editing} />
            break;
        case 'record':
            return <RecordBundle key={i} item={item} ref={ref} focused={focused} editing={editing} />
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
