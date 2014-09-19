/** @jsx React.DOM */

var MarkdownBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        return {
            lines: this.props.item.state.interpreted.split(/\r\n|\r|\n/).length,
            checked: false
        }
    },
    handleKeydown: function(event){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    this._owner.setState({editingIndex: -1});
                    break;
                case 'enter':
                    if(event.ctrlKey || event.metaKey){
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
    render: function() {
        var content = this.props.item.state.interpreted;
        var className = this.props.focused ? 'focused' : '';
        if (this.props.editing){
            return(
                <div className="ws-item">
                    <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                    <textarea className={className} rows={this.state.lines} onKeyDown={this.handleKeydown} defaultValue={content} />
                </div>
            )
        }else {
        var text = marked(content);
        // create a string of html for innerHTML rendering
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        return(
            <div className="ws-item">
                <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                <div className={className} dangerouslySetInnerHTML={{__html: text}} onKeyDown={this.handleKeydown} />
            </div>
        );
        }
    } // end of render function
}); //end of  MarkdownBundle