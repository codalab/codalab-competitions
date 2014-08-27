/** @jsx React.DOM */
var keyMap = {
    74: "j",
    75: "k"
};

var Worksheet = React.createClass({
    getInitialState: function(){
        ws_obj.state.focusIndex = 0;
        ws_obj.state.keyboardShortcuts = true;
        return ws_obj.state;
    },
    bindEvents: function(){
        window.addEventListener('keydown', this.move);
    },
    unbindEvents: function(){
        window.removeEventListener('keydown', this.move);
    },
    move: function(event) {
        if(this.state.keyboardShortcuts){
            var key = keyMap[event.keyCode];
            if(typeof key !== 'undefined'){
                switch (key) {
                    case 'k':
                        var index = Math.max(this.state.focusIndex - 1, 0);
                        break;
                    case 'j':
                        var index = Math.min(this.state.focusIndex + 1, this.state.items.length - 1);
                        break;
                    default:
                        var index = this.state.focusIndex;
                }
                this.setState({focusIndex: index});
            } else {
                return false;
            }
        } else {
            return false;
        }
    },
    toggleKeyboardShortcuts: function(){
        this.setState({keyboardShortcuts: !this.state.keyboardShortcuts});
    },
    componentDidMount: function() {  // once on the page lets get the ws info
        console.log('componentDidMount');
        ws_obj.fetch({
            success: function(data){
                $("#worksheet-message").hide();
                // as successful fetch will update our state data on the ws_obj.
                this.setState(ws_obj.state);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                if (xhr.status == 404) {
                    $("#worksheet-message").html("Worksheet was not found.");
                } else {
                    $("#worksheet-message").html("An error occurred. Please try refreshing the page.");
                }
            }.bind(this)
        });
        this.bindEvents();
    },
    componentDidUpdate: function(){
        var itemNode = this.refs['item' + this.state.focusIndex].getDOMNode();
        if(itemNode.offsetTop > window.innerHeight / 2){
            window.scrollTo(0, itemNode.offsetTop - (window.innerHeight / 2));
        }
    },
    componentWillUnmount: function(){
        this.unbindEvents();
    },
    render: function() {
        var focusIndex = this.state.focusIndex;
        var keyboardShortcutsClass = this.state.keyboardShortcuts ? 'shortcuts-on' : 'shortcuts-off';
        var listBundles = this.state.items.map(function(item, index) {
            var focused = focusIndex === index;
            var itemID = 'item' + index;
            return <WorksheetItem item={item} focused={focused} ref={itemID} />;
        });
         // listBundles is now a list of react components that each el is
        return (
            <div id="worksheet-content" className={keyboardShortcutsClass}>
                <div className="worksheet-name">
                    <h1 className="worksheet-icon">{this.state.name}</h1>
                    <div className="worksheet-author">{this.state.owner}</div>
                    <label>
                        <input type="checkbox" onChange={this.toggleKeyboardShortcuts} checked={this.state.keyboardShortcuts} />
                            Keyboard Shortcuts <small> for example on/off </small>
                    </label>
                    {
                        /*  COMMENTING OUT EXPORT BUTTON UNTIL WE DETERMINE ASSOCIATED ACTION
                            <a href="#" className="right">
                                <button className="med button">Export</button>
                            </a<
                        */
                    }
                </div>
                <div>{listBundles}</div>
            </div>
        );
    },
});


var WorksheetItem = React.createClass({
    render: function() {
        var item = this.props.item;
        var focused = this.props.focused ? ' focused' : '';
        var itemIndex = this.props.index;
        console.log('');
        console.log('WorksheetItem');
        console.log(item);
        var mode          = item['mode'];
        var interpreted   = item['interpreted'];
        var info          = item['bundle_info'];
        var classString   = 'type-' + mode + focused;
        var rendered_bundle = (
                <div> </div>
            );

        //based on the mode create the correct isolated component
        switch (mode) {
            case 'markup':
                rendered_bundle = (
                    <MarkdownBundle info={info} interpreted={interpreted} type={mode} />
                );
                break;

            case 'inline':
                rendered_bundle = (
                    <InlineBundle info={info} interpreted={interpreted} mode={mode} />
                );
                break;

            case 'table':
                rendered_bundle = (
                    <TableBundle info={info} interpreted={interpreted} mode={mode} />
                );
                break;

            default: // render things we don't know in bold for now
                rendered_bundle = (
                    <div>
                        <strong>{ mode }</strong>
                    </div>
                )
                break;
        }
        return(
            <div className={classString} key={this.props.itemId}>
                {rendered_bundle}
            </div>

        );
    } // end of render function
}); // end of WorksheetItem


var MarkdownBundle = React.createClass({
    componentDidMount: function() {
        MathJax.Hub.Queue([
            'Typeset',
            MathJax.Hub,
            this.getDOMNode()
        ]);
    },
    render: function() {
        //create a string of html for innerHTML rendering
        var text = markdown.toHTML(this.props.interpreted);
        if(text.length == 0){
            text = "<br>"
        }
        //
        // more info about dangerouslySetInnerHTML
        // http://facebook.github.io/react/docs/special-non-dom-attributes.html
        // http://facebook.github.io/react/docs/tags-and-attributes.html#html-attributes
        return(
            <span dangerouslySetInnerHTML={{__html: text}} />
        );
    } // end of render function
}); //end of  MarkdownBundle


var InlineBundle = React.createClass({
    render: function() {
        return(
            <em>
                {this.props.interpreted}
            </em>
        );
    } // end of render function
}); //end of  InlineBundle

var TableBundle = React.createClass({

    render: function() {
        var info = this.props.info;  //shortcut naming
        var bundle_url = "/bundles/" + info.uuid + "/"

        var header_items = this.props.interpreted[0]
        var header_html = header_items.map(function(item) {
                return <th> {item} </th>;
            });

        var row_items = this.props.interpreted[1];
        var body_rows_html = row_items.map(function(row_item) {
            var row_cells = header_items.map(function(header_key){
                if(header_key == 'name'){
                    return (
                        <td>
                            <a href={bundle_url} className="bundle-link">
                                { row_item[header_key] }
                            </a>
                        </td>
                    )
                } else {
                    return <td> { row_item[header_key] }</td>
                }
            });
            return (
                <tr>
                    {row_cells}
                </tr>
            );
        });

        return(
            <table className="table table-responsive">
                <thead>
                    <tr>{ header_html }</tr>
                </thead>
                <tbody>
                    { body_rows_html }
                </tbody>
            </table>
        );
    } // end of render function
}); //end of  InlineBundle

var worksheet_react = <Worksheet />;
React.renderComponent(worksheet_react, document.getElementById('worksheet-body'));
