/** @jsx React.DOM */

var InlineBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    render: function() {
        var className = this.props.focused ? 'focused' : '';
        return(
            <div className="ws-item">
                <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                <em className={className}>
                    {this.state.interpreted}
                </em>
            </div>
        );
    } // end of render function
}); //end of  InlineBundle
