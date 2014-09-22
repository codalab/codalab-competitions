/** @jsx React.DOM */

// key mapping for convenience. we can move this into the global scope at some point.
var keyMap = {
    13: "enter",
    38: "up",
    40: "down",
    74: "j",
    75: "k",
    88: "x",
    191: "fslash"
};

var Worksheets = React.createClass({
    // this is the master parent component -- the 'app'
    getInitialState: function(){
        return {
            activeComponent:"list",
            filter: "",
        }
    },
    handleFocus: function(event){
        // the search input is the only one who calls this so far.
        // if it's being focused, set it as the active component. if blurred, set the list as active.
        if(event.type=="focus"){
            this.setState({activeComponent:"search"});
        }else if(event.type=="blur"){
            this.setState({activeComponent:"list"});
        }
    },
    bindEvents: function(){
        // listen for ALL keyboard events at the top leve
        window.addEventListener('keydown', this.handleKeyboardShortcuts);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.handleKeyboardShortcuts);
    },
    setFilter: function(event){
        // all this does is store and update the string we're filter worksheet names by
        this.setState({filter:event.target.value})
    },
    handleKeyboardShortcuts: function(event){
        // the only key this guy cares about is \, because that's the shortcut to focus on the search bar
        if(keyMap[event.keyCode] == 'fslash'){
            event.preventDefault();
            this.refs.search.getDOMNode().focus();
        }
        // otherwise, try to pass off the event to the active component
        var activeComponent = this.refs[this.state.activeComponent];
        if(activeComponent.hasOwnProperty('handleKeyboardShortcuts')){
            // if it has a method to handle keyboard shortcuts, pass it
            activeComponent.handleKeyboardShortcuts(event);
        }else {
            // otherwise watch it go by
            return true;
        }
    },
    componentDidMount: function(){
        this.bindEvents();
    },
    componentWillUnmount: function(){
        this.unbindEvents();
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
        // get the list of worksheets and store it in this.state.worksheets
        $.ajax({
            type: "GET",
            url: "/api/worksheets",
            dataType: 'json',
            cache: false,
            success: function(data) {
                if(this.isMounted()){
                    this.setState({worksheets: data});
                }
                $("#worksheet-message").hide().removeClass('alert-box alert');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                $("#worksheet-message").html("Couldn\'t retrieve worksheets. Please try refreshing the page.").addClass('alert-box alert');
                $("#container").hide();
            }.bind(this)
        });
    },
    componentDidUpdate: function(){
        // scroll the window to keep the focused element in view
        var itemNode = this.refs['ws' + this.state.focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    goToFocusedWorksheet: function(){
        // navigate to the worksheet details page for the focused worksheet
        window.location.href += this.state.worksheets[this.state.focusIndex].uuid;
    },
    toggleMyWorksheets: function(){
        // filter by MY worksheets?
        this.setState({myWorksheets: !this.state.myWorksheets});
    },
    handleKeyboardShortcuts: function(event) {
        // this guy has shortcuts for going up and down, and selecting (essentially, clicking on it)
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
        // internal method for filtering the list, called from render() below
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
        // filter the worksheets by whatever
        var worksheets = this.filterWorksheets(this.props.filter);
        // if there's only one worksheet, it should always be focused
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
    // a single worksheet in the list
    goToWorksheet: function(){
        // in case you click on one that isn't focused. this is essentially the same as making the whole thing an <a href="">
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
    // the search bar at the top. it only does three things, all of them in the parent's state:
    //   1. if it's focused, make it the active component
    //   2. if it's blurred, make the other component active
    //   3. pass the value of the input up to the parent to use for filtering
    render: function(){
        return (      
            <input id="search" className="ws-search" type="text" placeholder="Search worksheets" onChange={this.props.setFilter} onFocus={this.props.handleFocus} onBlur={this.props.handleFocus}/>
        )
    }
});

React.renderComponent(<Worksheets />, document.getElementById('container'));

