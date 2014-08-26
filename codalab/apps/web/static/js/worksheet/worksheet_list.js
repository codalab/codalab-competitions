/** @jsx React.DOM */
var keyMap = {
    13: "enter",
    38: "up",
    40: "down",
    74: "j",
    75: "k",
    88: "x"
}
var WorksheetList = React.createClass({
    getInitialState: function(){
        return {
            worksheets: [],
            focusIndex: 0
        };
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.move);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.move);
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
        this.bindEvents();
    },
    componentDidUpdate: function(){
        var itemNode = this.refs['ws' + this.state.focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    goToFocusedWorksheet: function(){
        window.location.href += this.state.worksheets[this.state.focusIndex].uuid;
    },
    move: function(event) {
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
    render: function() {
        var focusIndex = this.state.focusIndex;
        var worksheetList = this.state.worksheets.map(function(worksheet, index){
            var wsID = 'ws' + index;
            var focused = focusIndex === index;
            return <Worksheet details={worksheet} focused={focused} ref={wsID} key={index} />
        });
        return (
            <div id="worksheet-list">
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
})

React.renderComponent(<WorksheetList />, document.getElementById('worksheets'));

