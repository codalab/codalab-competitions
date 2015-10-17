/** @jsx React.DOM */

// Display a worksheet item which is the HTML file in a bundle.
var HTMLBundle = React.createClass({
    mixins: [CheckboxMixin, GoToBundleMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    handleClick: function(event){
        var index = this.props.index;
        var last_sub_el = undefined;
        var direction = undefined;
        var scroll = false;
        this.props.setFocus(this.props.index, event, last_sub_el, direction, scroll);
    },
    render: function() {
        var className = 'type-html' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} disabled={!this.props.checkboxEnabled}/> : null;
        var contents = this.state.interpreted.join('');
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <div className={className} ref={this.props.item.state.ref}>
                    <div className="html-bundle" dangerouslySetInnerHTML={{__html: contents}}>
                    </div>
                </div>
            </div>
        );
    } // end of render function
}); //end of  ContentsBundle
