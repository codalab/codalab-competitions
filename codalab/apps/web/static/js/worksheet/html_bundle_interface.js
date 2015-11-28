/** @jsx React.DOM */

// Display a worksheet item which is the HTML file in a bundle.
var HTMLBundle = React.createClass({
    mixins: [CheckboxMixin, GoToBundleMixin],
    getInitialState: function(){
        return {};
    },
    handleClick: function(event){
        this.props.setFocus(this.props.focusIndex, 0);
    },
    render: function() {
        var className = 'type-html' + (this.props.focused ? ' focused' : '');
        var contents = html_sanitize(this.props.item.interpreted.join(''));
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className} ref={this.props.item.ref}>
                    <div className="html-bundle" dangerouslySetInnerHTML={{__html: contents}}>
                    </div>
                </div>
            </div>
        );
    }
});
