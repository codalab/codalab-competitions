/** @jsx React.DOM */


var Worksheet = React.createClass({
    getInitialState: function(){
        return {
            "last_item_id": 0,
            "name": "",
            "owner": null,
            "owner_id": 0,
            "uuid": 0,
            "items": [ ]
        };
    },
    componentDidMount: function() {  // once on the page lets get the ws info
        console.log('componentDidMount');
        $.ajax({
            type: "GET",
            //  /api/worksheets/0x706<...>d5b66e
            url: "/api" + document.location.pathname,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("setting worksheet state");
                console.log(data);
                console.log('');

                this.setState(data);

                $("#worksheet-message").hide();
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
    },
    render: function() {
         var listBundles = this.state.items.map(function(item) {
            return <WorksheetItem item={item} />;
        });
         // listBundles is now a list of react components that each el is
        return (
            <div id="worksheet-content">
                <div className="large-12 columns worksheet-name">
                    <h2 className="worksheet-icon">{this.state.name}</h2>
                    <label className="worksheet-author">{this.state.owner}</label>
                    {
                        /*  COMMENTING OUT EXPORT BUTTON UNTIL WE DETERMINE ASSOCIATED ACTION
                            <a href="#" className="right">
                                <button className="med button">Export</button>
                            </a<
                        */
                    }
                </div>
                <hr />
                <div>{listBundles}</div>
            </div>
        );
    }
});


var WorksheetItem = React.createClass({
    render: function() {
        var item = this.props.item;
        console.log('');
        console.log('WorksheetItem');
        console.log(item);
        var mode          = item['mode'];
        var interpreted   = item['interpreted'];
        var info          = item['bundle_info'];
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

            case 'bundle':
                rendered_bundle = (
                    <Rawbundle info={info} interpreted={interpreted} mode={mode} />
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
            <div>
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
            <span  dangerouslySetInnerHTML={{__html: text}} />
        );
    } // end of render function
}); //end of  MarkdownBundle


var Rawbundle = React.createClass({
    render: function() {
        var info = this.props.info;
        var bundle_icon_classes = "";
        bundle_icon_classes += ' bundle-name';
        bundle_icon_classes += ' bundle-icon-sm-indent';
        bundle_icon_classes += ' bundle-icon-sm--' + info.bundle_type + '--' + info.state;
        // notice we use className
        // http://facebook.github.io/react/docs/jsx-in-depth.html
        bundle_url = "/bundles/" + info.uuid + "/"
        return(
           <div id="bundle-template">
               <div className="row">
                   <div className="large-12 columns">
                       <div className="bundle-tile">
                           <div className="large-12 columns">
                               <a  className="bundle-download" alt="Download Bundle">
                                   <button className="small button secondary"><i className="fi-arrow-down"></i></button>
                               </a>
                               <label className="bundle-uuid">{data.uuid}</label>
                               <a href={bundle_url} className="bundle-link">
                                   <h4 className={bundle_icon_classes}>
                                        {data.metadata.name}
                                   </h4>
                               </a>
                           </div> {/* end of bundle-tile */}
                       </div>
                   </div>
               </div>
           </div>
        ); // return
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
        header_html.push(<th>Bundle Info</th>)

        var row_items = this.props.interpreted[1];
        var body_rows_html = row_items.map(function(row_item) {
                var row_cells = header_items.map(function(header_key){
                    return <td> { row_item[header_key] }</td>
                });
                return (
                    <tr>
                        {row_cells}
                        <td>
                            <a href={bundle_url} className="bundle-link">
                                {info.uuid}
                            </a>
                        </td>
                    </tr>
                );
            });

        return(
            <table>
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

var worksheet_react = <Worksheet />
React.renderComponent(worksheet_react, document.getElementById('worksheet-body'));
