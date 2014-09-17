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
    handleKeydown: function(event){
        if(typeof keyMap[event.keyCode] !== 'undefined'){
            console.log('worksheet list received ' + keyMap[event.keyCode]);
        }
    },
    render: function(){
        var worksheet_items = []
        this.props.items.forEach(function(item){
            var classString = 'type-' + item.state.mode;
            worksheet_items.push(
                <div className={classString}>
                    {WorksheetItemFactory(item)}
                </div>
            );
        });
        return (
            <div id="worksheet_content">
                {worksheet_items}
            </div>
        )
    }
});

var WorksheetItemFactory = function(item){
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle item={item} />
            break;
        case 'inline':
            return <InlineBundle item={item} />
            break;
        case 'table':
            return <TableBundle item={item} />
            break;
        case 'contents':
            return <ContentsBundle item={item} />
            break;
        case 'record':
            return <RecordBundle item={item} />
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


var worksheet = <Worksheet />;
React.renderComponent(worksheet, document.getElementById('worksheet_container'));
