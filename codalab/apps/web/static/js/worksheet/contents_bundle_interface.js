/** @jsx React.DOM */

// Display a worksheet item representing the file contents of a bundle.
var ContentsBundle = React.createClass({
    mixins: [CheckboxMixin, GoToBundleMixin],
    getInitialState: function(){
        return {};
    },
    handleClick: function(event){
        this.props.setFocus(this.props.focusIndex, 0);
    },

    shouldComponentUpdate: function(nextProps, nextState) {
      return worksheetItemPropsChanged(this.props, nextProps);
    },

    render: function() {
        var className = 'type-contents' + (this.props.focused ? ' focused' : '');
        var contents = this.props.item.interpreted.join('');
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className} ref={this.props.item.ref}>
                    <blockquote>
                        <p>{contents}</p>
                    </blockquote>
                </div>
            </div>
        );
    }
});
