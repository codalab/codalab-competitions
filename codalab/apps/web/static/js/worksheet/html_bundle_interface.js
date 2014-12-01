/** @jsx React.DOM */

var HTMLBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
        return this.props.item.state;
    },
    handleClick: function(){
        this.props.setFocus(this.props.key);
    },
    render: function() {
        var className = 'type-html' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} disabled={!this.props.checkboxEnabled}/> : null;
        // if there is an error with the file path interpreted is null
        var contents = ["null"]
        if(this.state.interpreted){
            contents = this.state.interpreted.map(function(item){
                return item.replace(/%\s/, '');
            });
        }
        contents = contents.join('');
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
