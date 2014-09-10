/** @jsx React.DOM */

var InlineBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        return(
            <em>
                {this.state.interpreted}
            </em>
        );
    } // end of render function
}); //end of  InlineBundle
