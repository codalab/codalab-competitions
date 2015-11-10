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
        var src= "data:image/png;base64," + this.props.item.interpreted;
        var styles = {};
        if (this.state.properties) {
            if (this.state.properties.hasOwnProperty('height')) {
                styles['height'] = this.state.properties.height + "px;"
            }
            if (this.state.properties.hasOwnProperty('width')) {
                styles['width'] = this.state.properties.width + "px;"
            }
        }
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className} ref={this.props.item.ref}>
                    <img style={styles} src={src} />
                </div>
            </div>
        );
    } // end of render function
}); //end of  ContentsBundle
