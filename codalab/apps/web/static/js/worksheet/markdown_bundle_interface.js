/** @jsx React.DOM */

var MarkdownBundle = React.createClass({
    getInitialState: function(){
        this.props.item.state.lines = this.props.item.state.interpreted.split(/\r\n|\r|\n/).length;
        return this.props.item.state;
    },
    handleMarkdownKeyboardShortcuts: function(event){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    this._owner.props.onExitEdit();
                    break;
                case 'enter':
                    if(event.ctrlKey || (isMac && event.metaKey)){
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
        this._owner.props.onExitEdit();
        ws_searchActions.doSave();
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
            this.getDOMNode().focus();
        }
    },
    render: function() {
        if (this.props.editing){
            return(
                <textarea rows={this.state.lines} onKeyDown={this.handleMarkdownKeyboardShortcuts} defaultValue={this.state.interpreted} />
            )
        }else {
        var text = marked(this.state.interpreted);
        // create a string of html for innerHTML rendering
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        return(
            <span dangerouslySetInnerHTML={{__html: text}} onKeyDown={this.handleMarkdownKeyboardShortcuts} />
        );
        }
    } // end of render function
}); //end of  MarkdownBundle