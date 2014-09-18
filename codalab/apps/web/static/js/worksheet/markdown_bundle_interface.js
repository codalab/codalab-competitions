/** @jsx React.DOM */

var MarkdownBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.lines = this.props.item.state.interpreted.split(/\r\n|\r|\n/).length;
        this.props.item.state.checked = false
        return this.props.item.state;
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
        console.log('------ save the worksheet here ------');
        this.setState({interpreted: textarea.value});
        // Callback to <Worksheet /> to reset editing
        this._owner.setState({editingIndex: -1});
        ws_actions.doSave();
    },
    componentDidMount: function() {
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
    },
    componentDidUpdate: function(){
        if(this.props.editing){
            $(this.getDOMNode()).find('textarea').focus();
        }
    },
    render: function() {
        var className = this.props.focused ? 'focused' : '';
        if (this.props.editing){
            return(
                <div className="ws-item">
                    <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                    <textarea className={className} rows={this.state.lines} onKeyDown={this.handleKeydown} defaultValue={this.state.interpreted} />
                </div>
            )
        }else {
        var text = marked(this.state.interpreted);
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