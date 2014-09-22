/** @jsx React.DOM */

var InlineBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    handleClick: function(){
        this.props.setFocus(this);
    },
    render: function() {
        var className = this.props.focused ? 'focused' : '';
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} /> : null;
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <em className={className}>
                    {this.state.interpreted}
                </em>
            </div>
        );
    } // end of render function
}); //end of  InlineBundle
