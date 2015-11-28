/** @jsx React.DOM */

// Display a worksheet item which corresponds to Markdown (with MathJax).
var MarkdownBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function() {
        return {};
    },
    processMathJax: function() {
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
    },
    componentDidMount: function() {
    },
    componentDidUpdate: function() {
        this.processMathJax();
    },
    handleClick: function(event) {
        this.props.setFocus(this.props.focusIndex, 0);
    },
    processMarkdown: function(text) {
        // 'we have $x^2$' => 'we have @ppp@'
        text = this.removeMathJax(text);
        // 'we have @ppp@' => '<p>we have @ppp@</p>'
        text = marked(text);
        // '<p>we have @ppp@</p>' => '<p>we have @x^2@</p>'
        text = this.replaceMathJax(text);
        return text;
    },
    render: function() {
        var contents = html_sanitize(this.props.item.interpreted);
        contents = this.processMarkdown(contents);

        // create a string of html for innerHTML rendering
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        var className = 'type-markup ' + (this.props.focused ? ' focused' : '');
        return (
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className} dangerouslySetInnerHTML={{__html: contents}} />
            </div>
        );
    }, // end of render function

    /// helper functions for making markdown and mathjax work together
    contentMathjaxText: [],
    removeMathJax: function(text) {
        var start = 0;
        var end = -1;
        var len = 0
        // Replace math (e.g., $x^2$) with placeholder so that it doesn't interfere with Markdown.
        while (text.indexOf("$", start) > 0) {
            start = text.indexOf("$", start);
            end = text.indexOf("$", start+1);
            if (end === -1) {  // We've reached the end
                start =-1
                break;
            }
            end++; // Add 1 for later cutting
            var mathText = text.slice(start, end);  // e.g., "$\sum_z p_\theta$"
            this.contentMathjaxText.push(mathText);
            // Cut out the math and replace with @pppppp@ since markdown doesnt care about @
            var firstHalf = text.slice(0, start);
            var sencondHalf = text.slice(end);
            /// New string has to be the same length for replace to work and the start/end counting system
            var middle = "@";
            for(var i = 0; i < mathText.length-2; i++) {
                middle = middle + "p";
            }
            middle = middle + "@";
            text = firstHalf + middle + sencondHalf;
            start = end; // Look for the next occurrence of math
        }
        return text
    },
    replaceMathJax: function(text) {
        // Restore the MathJax.
        var start = 0;
        var end = -1;
        var len = 0
        var mathText = '';
        for(var i = 0; i < this.contentMathjaxText.length; i++) {
            mathText = this.contentMathjaxText[i];
            var placeholder = "@";
            for(var j = 0; j < mathText.length-2; j++) {
                placeholder = placeholder + "p";
            }
            placeholder = placeholder + "@";
            text = text.replace(placeholder, mathText);
        }
        this.contentMathjaxText = [];
        return text;
    },
});
