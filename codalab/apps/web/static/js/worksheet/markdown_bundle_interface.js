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

    placeholderText: '@MATH@',

    processMarkdown: function(text) {
        var mathSegments = [];
        // 'we have $x^2$' => 'we have @MATH@'
        text = this.removeMathJax(text, mathSegments);
        // 'we have @ppp@' => '<p>we have @MATH@</p>'
        text = marked(text);
        // '<p>we have @ppp@</p>' => '<p>we have @x^2@</p>'
        text = this.restoreMathJax(text, mathSegments);
        return text;
    },

    shouldComponentUpdate: function(nextProps, nextState) {
      return worksheetItemPropsChanged(this.props, nextProps);
    },

    render: function() {
        var contents = this.props.item.interpreted;
        // Order is important!
        contents = this.processMarkdown(contents);
        contents = html_sanitize(contents);

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
    removeMathJax: function(text, mathSegments) {
        var curr = 0;  // Current position
        // Replace math (e.g., $x^2$ or $$x^2$$) with placeholder so that it
        // doesn't interfere with Markdown.
        var newText = '';
        while (true) {
            // Figure out next block of math from current position.
            // Example:
            //   0123456 [indices]
            //   $$x^2$$ [text]
            //   start = 0, inStart = 2, inEnd = 5, end = 7
            start = text.indexOf("$", curr);
            if (start == -1) break;  // No more math
            var inStart = (text[start + 1] == '$' ? start + 2 : start + 1);
            var inEnd = text.indexOf('$', inStart);
            if (inEnd === -1) {  // We've reached the end without closing
                console.error('Math \'$\' not matched', text);
                break;
            }
            var end = (text[inEnd + 1] == '$' ? inEnd + 2 : inEnd + 1);

            var mathText = text.slice(start, end);  // e.g., "$\sum_z p_\theta$"
            mathSegments.push(mathText);
            newText += text.slice(curr, start) + this.placeholderText;
            curr = end; // Look for the next occurrence of math
        }
        newText += text.slice(curr);
        return newText;
    },

    restoreMathJax: function(text, mathSegments) {
        // Restore the MathJax, replacing placeholders with the elements of mathSegments.
        var newText = '';
        var curr = 0;
        for (var i = 0; i < mathSegments.length; i++) {
            var start = text.indexOf(this.placeholderText, curr);
            if (start == -1) {
              console.error('Internal error: shouldn\'t happen');
              break;
            }
            newText += text.slice(curr, start) + mathSegments[i];
            curr = start + this.placeholderText.length;  // Advance cursor
        }
        newText += text.slice(curr);
        return newText;
    },
});
