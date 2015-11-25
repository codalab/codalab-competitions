/** @jsx React.DOM */

// Display a worksheet item which corresponds to (sub)worksheets.
var WorksheetBundle = React.createClass({
    mixins: [CheckboxMixin],

    getInitialState: function() {
      return {
        rowFocusIndex: -1,  // Which row of the table has the focus?
      };
    },

    throttledScrollToRow: undefined,

    capture_keys: function(event) {
        // Move focus up one
        Mousetrap.bind(['up', 'k'], function(e) {
            var newIndex = this.state.rowFocusIndex - 1;
            if (newIndex < 0)
              this.props.setFocus(this.props.index - 1, 'end');  // Move out of this table
            else
              this.focusOnRow(newIndex);
        }.bind(this), 'keydown');

        // Move focus down one
        Mousetrap.bind(['down', 'j'], function(event) {
            var newIndex = this.state.rowFocusIndex + 1;
            var index = this.state.rowFocusIndex;
            var numRows = this._getItems().length;
            if (newIndex >= numRows)
              this.props.setFocus(this.props.index + 1, 0);  // Move out of this table
            else
              this.focusOnRow(newIndex);
        }.bind(this), 'keydown');

        // Open worksheet in new window/tab
        Mousetrap.bind(['enter'], function(e) {
            window.open(this.refs['row' + this.state.rowFocusIndex].props.url, '_blank');
        }.bind(this), 'keydown');

        // Paste uuid of focused worksheet into console
        Mousetrap.bind(['u'], function(e) {
            var uuid = this.refs['row' + this.state.rowFocusIndex].props.uuid;
            $('#command_line').terminal().insert(uuid);
            this.props.focusActionBar();
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

    focusOnRow: function(rowIndex) {
        this.props.setFocus(this.props.index, rowIndex);
        this.updateRowFocusindex(rowIndex);
    },

    updateRowFocusindex: function(rowIndex) {
        this.setState({rowFocusIndex: rowIndex});
        this.scrollToRow(rowIndex);
    },

    _getItems: function() {
      var item = this.props.item;
      if (item.mode == 'worksheet') {
        return [item];
      } else if (item.mode == 'wsearch') {
        return item.interpreted.items;
      } else {
        throw 'Invalid: ' + item.mode;
      }
    },

    render: function() {
        if (this.props.active && this.props.focused)
          this.capture_keys();

        var self = this;
        var tableClassName = (this.props.focused ? 'table focused' : 'table');
        var canEdit = this.props.canEdit;
        var items = this._getItems();

        var focusIndex = this.state.rowFocusIndex;
        var body_rows_html = items.map(function(item, index) {
            var row_ref = 'row' + index;
            var rowFocused = self.props.focused && (index == focusIndex);
            var url = '/worksheets/' + item.interpreted.uuid;
            return <TableWorksheetRow
                     key={index}
                     ref={row_ref}
                     item={item}
                     index={index}
                     focused={rowFocused}
                     url={url}
                     uuid={item.interpreted.uuid}
                     canEdit={canEdit}
                     handleClick={self.focusOnRow}
                   />;
        });
        return (
            <div className="ws-item">
                <div className="type-table table-responsive">
                    <table className={tableClassName}>
                      <tbody>
                          {body_rows_html}
                      </tbody>
                  </table>
                </div>
            </div>
        );
    } // end of render function
});

////////////////////////////////////////////////////////////

var TableWorksheetRow = React.createClass({
    getInitialState: function() {
        return { };
    },
    handleClick: function() {
      this.props.handleClick(this.props.index);
    },

    render: function() {
        var item = this.props.item.interpreted;
        var className = /*'type-worksheet' + */(this.props.focused ? ' focused' : '');
        var ws_url = '/worksheets/' + item.uuid;

        var worksheet_display = item.name;
        if (item.title) {
            worksheet_display = item.title + " [" + item.name + "]";
        }

        return (
            <tr className={className}><td>
              <div onClick={this.handleClick}>
                <a href={ws_url} target="_blank">
                    {worksheet_display}
                </a>
              </div>
            </td></tr>
        );
    }
})
