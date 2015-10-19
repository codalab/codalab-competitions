/** @jsx React.DOM */

// Display a worksheet item which corresponds to a table where each row is a bundle.
var TableBundle = React.createClass({
    mixins: [CheckboxMixin],

    getInitialState: function() {
      return {
        rowFocusIndex: -1,  // Which row of the table has the focus?
      };
    },

    throttledScrollToRow: undefined,

    capture_keys: function() {
        // Move focus up one
        Mousetrap.bind(['up', 'k'], function(e) {
            var newIndex = this.state.rowFocusIndex - 1;
            if (newIndex < 0)
              this.props.setFocus(this.props.index - 1, -1);  // Move out of this table
            else
              this.focusOnRow(newIndex);
        }.bind(this), 'keydown');

        // Move focus down one
        Mousetrap.bind(['down', 'j'], function(event) {
            var newIndex = this.state.rowFocusIndex + 1;
            var index = this.state.rowFocusIndex;
            var numRows = this.props.item.state.interpreted[1].length;
            if (newIndex >= numRows)
              this.props.setFocus(this.props.index + 1, 0);  // Move out of this table
            else
              this.focusOnRow(newIndex);
        }.bind(this), 'keydown');
    },

    scrollToRow: function(index) {
        var __innerScrollToRow = function(index) {
            //console.log('__innerScrollToRow', index);
            // Compute the current position of the focused row.
            var node = this.getDOMNode();
            var nodePos = node.getBoundingClientRect();
            var rowHeight = this.refs.row0.getDOMNode().offsetHeight;
            var tablePos = nodePos.top;
            var pos = tablePos + (index * rowHeight);
            // Make sure it's visible
            keepPosInView(pos);
        };

        // Throttle so that if keys are held down, we don't suffer a huge lag.
        if (this.throttledScrollToRow === undefined)
            this.throttledScrollToRow = _.throttle(__innerScrollToRow, 50).bind(this);
        this.throttledScrollToRow(index);
    },

    focusOnRow: function(rowIndex, event) {
        this.setState({rowFocusIndex: rowIndex});
        this.props.updateWorksheetSubFocusIndex(rowIndex);
        this.scrollToRow(rowIndex);
    },

    handleClick: function(event) {
        this.props.setFocus(this.props.index);
    },

    render: function() {
        //console.log('TableBundle.render', this.state.rowFocusIndex);

        if (this.props.active && this.props.focused)
          this.capture_keys();

        var self = this;
        var tableClassName = (this.props.focused ? 'table focused' : 'table');
        var item = this.props.item.state;
        var canEdit = this.props.canEdit;
        var bundle_info = item.bundle_info;
        var header_items = item.interpreted[0];
        var column_classes = header_items.map(function(item, index) {
            return 'table-column-' + encodeURIComponent(item).replace("%", "_").replace(/[^-_A-Za-z0-9]/g, "_");
        });
        var header_html = header_items.map(function(item, index) {
            return <th key={index} className={column_classes[index]}>{item}</th>;
        });
        var focusIndex = this.state.rowFocusIndex;
        var row_items = item.interpreted[1];
        /* row_items is an array of objects containing table content.
        For instance row_items may be Array[1] where
        object0 = {
            Parameters = {
                path: "/output",
                text: "params",
                uuid: "0xdafcc128243d46fb8a7f76926148ed7a
            }
            uuid: "0xdafcc128243d46fb8a7f76926148ed7a"
         } */
        var column_with_hyperlinks = [];
        (Object.keys(row_items[0])).forEach(function(x) {
            if (typeof row_items[0][x] === 'object' && 'path' in row_items[0][x]) {
                column_with_hyperlinks.push(x);
            }
        })
        var body_rows_html = row_items.map(function(row_item, index) {
            var row_ref = 'row' + index;
            var rowFocused = self.props.focused && (index == focusIndex);
            var url = '/bundles/' + bundle_info[index].uuid;
            return <TableRow
                     key={index}
                     ref={row_ref}
                     item={row_item}
                     index={index}
                     focused={rowFocused}
                     url={url}
                     uuid={bundle_info[index].uuid}
                     headerItems={header_items}
                     columnClasses={column_classes}
                     canEdit={canEdit}
                     handleClick={self.focusOnRow}
                     columnWithHyperlinks={column_with_hyperlinks}
                   />;
        });
        return (
            <div className="ws-item">
                <div className="type-table table-responsive">
                    <table className={tableClassName} onClick={this.handleClick}>
                        <thead>
                            <tr>
                                {header_html}
                            </tr>
                        </thead>
                        <tbody>
                            {body_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }
});

////////////////////////////////////////////////////////////

var TableRow = React.createClass({
    getInitialState: function() {
        return { };
    },
    handleClick: function() {
        this.props.handleClick(this.props.index);
    },

    capture_keys: function() {
        Mousetrap.bind(['enter'], function(e) {
            window.open(this.props.url, '_blank');
        }.bind(this), 'keydown');
    },

    render: function() {
        //console.log('TableRow.render', this.props.focused);
        if (this.props.focused)
          this.capture_keys();

        var focusedClass = this.props.focused ? 'focused' : '';
        var row_items = this.props.item;
        var header_items = this.props.headerItems;
        var column_classes = this.props.columnClasses;
        var base_url = this.props.url;
        var uuid = this.props.uuid;
        var column_with_hyperlinks = this.props.columnWithHyperlinks;
        var row_cells = this.props.headerItems.map(function(header_key, index) {
            var row_content = row_items[header_key];

            // See if there's a link
            var url;
            if (index == 0) {
              url = base_url;
            } else if (column_with_hyperlinks.indexOf(header_key) != -1) {
              url = '/api/bundles/filecontent/' + uuid + row_content['path'];
              if ('text' in row_content) {
                row_content = row_content['text'];
              } else {
                // In case text doesn't exist, content will default to basename of the path
                // indexing 1 here since the path always starts with '/'
                row_content = row_content['path'].split('/')[1];
              }
            }
            if (url)
              row_content = <a href={url} className="bundle-link" target="_blank">{row_content}</a>;

            return (
              <td key={index} className={column_classes[index]}>
                {row_content}
              </td>
            );
        });

        return (
            <tr className={focusedClass} onClick={this.handleClick}>
                {row_cells}
            </tr>
        );
    }
})
