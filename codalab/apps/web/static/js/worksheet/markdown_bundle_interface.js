/** @jsx React.DOM */

var MarkdownBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        return {
            checked: false,
            new_item: false,
            editing: false,
        };
    },
    capture_keys: function(event){
        if(this.props.editing){
            console.log("setting up markdown keys");
            Mousetrap.reset(); // since we are editing reset and only let you save
            Mousetrap.bind(['ctrl+enter', "meta+enter"], function(e){
                console.log("ctrl+enter  meta+enter'");
                this.saveEditedItem(e.target.value);
            }.bind(this));

            Mousetrap.bind(['esc'], function(e){
            // TODO remove _owner feels like a hack
            this._owner.setState({editingIndex: -1});
            this._owner.props.toggleEditingText(false);
            if(this.props.editing){
                if(!$(this.getDOMNode()).find('textarea').val().length || this.state.new_item){
                    //calling WorksheetItemList unInsert
                    this.setState({new_item: false});
                    this._owner.unInsert();
                }
            }
        }.bind(this), 'keydown');
        }

    },
    saveEditedItem: function(interpreted){
        this.props.handleSave(this.props.index, interpreted);
    },
    processMathJax: function(){
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
    },
    componentDidMount: function() {
        this.processMathJax();
        if(this.props.editing){
            $(this.getDOMNode()).find('textarea').focus();
        }
    },
    componentDidUpdate: function(){
        if(this.props.editing){
            $(this.getDOMNode()).find('textarea').focus();
        }else {
            // TODO: there may be a more efficient way to do this,
            // but for now this seems logical
            this.processMathJax();
        }
    },
    handleClick: function(event){
        this.props.setFocus(this.props.index, event);
    },
    processMarkdown: function(text){
        text = this.removeMathJax(text)
        text = marked(text)
        text = this.replaceMathJax(text);
        return text
    },
    render: function() {
        var content = this.props.item.state.interpreted;
        var className = 'type-markup ' + (this.props.focused ? ' focused' : '') + (this.props.editing ? ' form-control mousetrap' : '');
        //if we can edit show checkbox if not show nothing(null)
        var checkbox = this.props.canEdit ? <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} disabled={!this.props.checkboxEnabled}/> : null;

        if (this.props.editing){ // are we editing show a text area
            var lines = Math.max(this.props.item.state.interpreted.split(/\r\n|\r|\n/).length, 3);
            return(
                <div className="ws-item" onClick={this.handleClick}>
                    {checkbox}
                    <textarea className={className} rows={lines} onKeyDown={this.handleKeydown} defaultValue={content} />
                </div>
            )
        }else { // just render the markdown
            var text = this.processMarkdown(content);
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
    }, // end of render function

    /// helper functions for making markdown and mathjax work together
    conentMathjaxText: [],
    removeMathJax: function(text){
        var start = 0;
        var end = -1;
        var len = 0
        // we need to rip out and replace the math wiht placeholder for markdown
        // to not interfere witht it
        while(text.indexOf("$", start) > 0){
            start = text.indexOf("$", start)
            end = text.indexOf("$", start+1)
            if(end === -1){ //we've reached the end
                start =-1
                break;
            }
            end++; // add 1 for later cutting
            var MathText = text.slice(start,end+1)  // eg: "$\sum_z p_\theta$"
            this.conentMathjaxText.push(MathText);
            //cut out the string and replace with @pppppp@ //markdown doesnt care about @
            var firstHalf = text.slice(0, start)
            var sencondHalf = text.slice(end)
            /// has to be the same length for replace to work and the start/end counting system
            var middle = "@"
            for(var i = 0; MathText.length-2 > i; i++){
                middle = middle + "p"
            }
            middle = middle + "@"
            text = firstHalf + middle + sencondHalf;
            start = end; //look for the next one
        }
        return text
    },
    replaceMathJax: function(text){
        var start = 0;
        var end = -1;
        var len = 0
        var MathText = ''
        for(var i = 0; this.conentMathjaxText.length > i; i++){
            MathText = this.conentMathjaxText[i];
            var placeholder = "@"
            for(var j = 0; MathText.length-2 > j; j++){
                placeholder = placeholder + "p"
            }
            placeholder = placeholder + "@"
            text = text.replace(placeholder, MathText);
        }
        this.conentMathjaxText = []
        return text
    },

}); //end of  MarkdownBundle