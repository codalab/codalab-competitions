/** @jsx React.DOM */

var WorksheetBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    keysToHandle: function(){
        return['enter']
    },
    handleKeydown: function(){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            event.preventDefault();
            switch (key) {
                case 'enter':
                    event.preventDefault();
                    this.goToWorksheet();
                    break;
                default:
                    return true;
            }
        }
    },
    handleClick: function(event){
        this.props.setFocus(this.props.key, event);
    },
    goToWorksheet: function(){
        window.open('/worksheets/' + this.props.item.state.interpreted.uuid);
    },
    render: function() {
        var item = this.props.item.state.interpreted;
        var className = 'type-worksheet' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} disabled={!this.props.checkboxEnabled}/> : null;
        var ws_url = '/worksheets/' + item.uuid;
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <div className={className}>
                    <a href={ws_url} target="_blank">
                        {item.name}
                    </a>
                </div>
            </div>
        );
    } // end of render function
}); //end of  InlineBundle
