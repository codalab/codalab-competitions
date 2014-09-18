/** @jsx React.DOM */

var InlineBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        var className = this.props.focused ? 'focused' : '';
        return(
            <em className={className}>
                {this.state.interpreted}
            </em>
        );
    } // end of render function
}); //end of  InlineBundle
