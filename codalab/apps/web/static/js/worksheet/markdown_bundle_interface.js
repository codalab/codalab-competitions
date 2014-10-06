/** @jsx React.DOM */

var MarkdownBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        return {
            checked: false,
            new_item: false
        };
    },
    keysToHandle: function(){
        return['esc','enter'];
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc': // cancel
                    this._owner.setState({editingIndex: -1});
                    if(!$(this.getDOMNode()).find('textarea').val().length || this.state.new_item){
                        this._owner.unInsert();
                    }
                    event.stopPropagation();
                    break;
                case 'enter':  // save or add a new line
                    if(event.ctrlKey || event.metaKey){ // ctrl/meta on mac for saving item
                        event.preventDefault();
                        this.saveEditedItem(event.target);
                    }
                    break;
                default:
                    return true;
            }
        } else {
            return true;
        }
    },
    saveEditedItem: function(textarea){
        this.props.handleSave(textarea);
    },
    componentDidMount: function() {
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
        if(this.props.editing){
            $(this.getDOMNode()).find('textarea').focus();
        }
    },
    componentDidUpdate: function(){
        if(this.props.editing){
            $(this.getDOMNode()).find('textarea').focus();
        }
    },
    handleClick: function(){
        this.props.setFocus(this);
    },
    render: function() {
        var content = this.props.item.state.interpreted;
        var className = 'type-markup' + (this.props.focused ? ' focused' : '');
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} /> : null;
        if (this.props.editing){
            var lines = Math.max(this.props.item.state.interpreted.split(/\r\n|\r|\n/).length, 3);
            return(
                <div className="ws-item" onClick={this.handleClick}>
                    {checkbox}
                    <textarea className={className} rows={lines} onKeyDown={this.handleKeydown} defaultValue={content} />
                </div>
            )
        }else {
        var text = marked(content);
        // create a string of html for innerHTML rendering
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        return(
            <div className="ws-item" onClick={this.handleClick}>
                {checkbox}
                <div className={className} dangerouslySetInnerHTML={{__html: text}} onKeyDown={this.handleKeydown} />
            </div>
        );
        }
    } // end of render function
}); //end of  MarkdownBundle