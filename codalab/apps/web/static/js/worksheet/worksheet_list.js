/** @jsx React.DOM */
var keyMap = {
    13: "enter",
    38: "up",
    40: "down",
    74: "j",
    75: "k",
    88: "x",
    220: "bslash"
};

var Worksheets = React.createClass({
    getInitialState: function(){
        return {
            activeComponent:"list",
            filter: "",
        }
    },
    handleFocus: function(event){
        if(event.type=="focus"){
            this.setState({activeComponent:"search"});
        }else if(event.type=="blur"){
            this.setState({activeComponent:"list"});
        }
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.handleKeyboardShortcuts);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.handleKeyboardShortcuts);
    },
    setFilter: function(event){
        this.setState({filter:event.target.value})
    },
    componentDidMount: function(){
        this.bindEvents();
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    handleKeyboardShortcuts: function(event){
        if(keyMap[event.keyCode] == 'bslash'){
            event.preventDefault();
            this.refs.search.getDOMNode().focus();
        }
        // dispatch the keycode to the active component
        var activeComponent = this.refs[this.state.activeComponent];
        if(activeComponent.hasOwnProperty('handleKeyboardShortcuts')){
            activeComponent.handleKeyboardShortcuts(event);
        }else {
            return true;
        }
    },
    render: function(){
        return(
            <div>
                <WorksheetSearch setFilter={this.setFilter} handleFocus={this.handleFocus} ref={"search"} active={this.state.activeComponent=='search'} />
                <WorksheetList handleFocus={this.handleFocus} ref={"list"} active={this.state.activeComponent=='list'} filter={this.state.filter} />
            </div>
        )
    }
});

var WorksheetList = React.createClass({
    getInitialState: function(){
        return {
            worksheets: [],
            focusIndex: 0,
            myWorksheets: false
        };
    },
    componentDidMount: function() {
        $.ajax({
            type: "GET",
            url: "/api/worksheets",
            dataType: 'json',
            cache: false,
            success: function(data) {
                if(this.isMounted()){
                    this.setState({worksheets: data});
                }
                $("#worksheet-message").hide();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                $("#worksheet_list").html("Couldn\'t retrieve worksheets - Try refreshing the page");
            }.bind(this)
        });
    },
    componentDidUpdate: function(){
        var itemNode = this.refs['ws' + this.state.focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    goToFocusedWorksheet: function(){
        window.location.href += this.state.worksheets[this.state.focusIndex].uuid;
    },
    toggleMyWorksheets: function(){
        this.setState({myWorksheets: !this.state.myWorksheets});
    },
    handleKeyboardShortcuts: function(event) {
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            event.preventDefault();
            if(key == 'k' || key == 'up'){
                this.setState({focusIndex: Math.max(this.state.focusIndex - 1, 0)});
            }else if (key == 'j' || key == 'down'){
                this.setState({focusIndex: Math.min(this.state.focusIndex + 1, this.state.worksheets.length - 1)});
            }else if (key == 'x' || key == 'enter'){
                this.goToFocusedWorksheet();
            }else {
                return false;
            }
        }
    },
    filterWorksheets:function(filter){
        var worksheets = this.state.worksheets;
        if(this.state.myWorksheets){
            worksheets = worksheets.filter(function(ws){ return ws.owner_id === user_id; });
        }
        if(this.props.filter.length){
            console.log('filtering by: ' + filter);
            worksheets = worksheets.filter(function(ws){ 
                return (ws.name.indexOf(filter) > -1);
            });
        }
        return worksheets;
    },
    render: function() {
        var worksheets = this.filterWorksheets(this.props.filter);
        var focusIndex = worksheets.length > 1 ? this.state.focusIndex : 0;
        var worksheetList = worksheets.map(function(worksheet, index){
            var wsID = 'ws' + index;
            var focused = focusIndex === index;
            return <Worksheet details={worksheet} focused={focused} ref={wsID} key={index} />
        });
        return (
            <div id="worksheet-list">
                <label className="my-worksheets-toggle">
                    <input type="checkbox" onChange={this.toggleMyWorksheets} checked={this.state.myWorksheets} />
                    Show my worksheets only
                </label>
                {worksheetList}
            </div>
        );
    }
});

var Worksheet = React.createClass({
    goToWorksheet: function(){
        window.location.href += this.props.details.uuid;
    },
    render: function(){
        var ws = this.props.details;
        var focused = this.props.focused ? ' focused' : '';
        var classString = 'worksheet-tile' + focused;
        var byline = '';
        if(ws.owner){
            byline += 'by ' + ws.owner;
            if(ws.permission == 1){
                byline += ' (read-only)';
            }
        }
        return (
            <div className={classString} onClick={this.goToWorksheet}>
                <div className="worksheet-inner">
                    <h3>{ws.name}</h3>
                    <div>{byline}</div>
                </div>
            </div>
        );
    }
});

var WorksheetSearch = React.createClass({
    render: function(){
        return (      
            <input id="search" className="ws-search" type="text" placeholder="Search worksheets" onChange={this.props.setFilter} onFocus={this.props.handleFocus} onBlur={this.props.handleFocus}/>
        )
    }
});

React.renderComponent(<Worksheets />, document.getElementById('container'));

