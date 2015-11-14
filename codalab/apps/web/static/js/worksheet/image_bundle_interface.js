/** @jsx React.DOM */

// Display a worksheet item which is an image file in a bundle.
var ImageBundle = React.createClass({
    mixins: [CheckboxMixin, GoToBundleMixin],
    getInitialState: function() {
        return {};
    },
    handleClick: function(event) {
        this.props.setFocus(this.props.index);
    },
    render: function() {
        var className = 'type-image' + (this.props.focused ? ' focused' : '');
        var src = "data:image/png;base64," + this.props.item.interpreted;
        var styles = {};
        var properties = this.props.item.properties;
        if (properties) {
            if (properties.hasOwnProperty('height')) {
                styles['height'] = properties.height + "px;"
            }
            if (properties.hasOwnProperty('width')) {
                styles['width'] = properties.width + "px;"
            }
        }
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className} ref={this.props.item.ref}>
                    <img style={styles} src={src} />
                </div>
            </div>
        );
    }
});
