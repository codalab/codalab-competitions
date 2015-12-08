/** @jsx React.DOM */

// Display a worksheet item which corresponds to (sub)worksheets.
var WorksheetBundle = React.createClass({
    mixins: [CheckboxMixin],

    getInitialState: function() {
      return { };
    },

    throttledScrollToRow: undefined,

    capture_keys: function() {
        // Move focus up one
        Mousetrap.bind(['up', 'k'], function(e) {
            if (this.props.subFocusIndex - 1 < 0)
              this.props.setFocus(this.props.focusIndex - 1, 'end');  // Move out of this table
            else
              this.props.setFocus(this.props.focusIndex, this.props.subFocusIndex - 1);
        }.bind(this), 'keydown');

        // Move focus down one
        Mousetrap.bind(['down', 'j'], function() {
            if (this.props.subFocusIndex + 1 >= this._getItems().length)
              this.props.setFocus(this.props.focusIndex + 1, 0);  // Move out of this table
            else
              this.props.setFocus(this.props.focusIndex, this.props.subFocusIndex + 1);
        }.bind(this), 'keydown');

        // Open worksheet in same tab
        Mousetrap.bind(['enter'], function(e) {
            this.props.openWorksheet(this.refs['row' + this.props.subFocusIndex].props.uuid);
        }.bind(this), 'keydown');

        // Open worksheet in new window/tab
        Mousetrap.bind(['shift+enter'], function(e) {
            window.open(this.refs['row' + this.props.subFocusIndex].props.url, '_blank');
        }.bind(this), 'keydown');

        // Paste uuid of focused worksheet into console
        Mousetrap.bind(['u'], function(e) {
            var uuid = this.refs['row' + this.props.subFocusIndex].props.uuid;
            $('#command_line').terminal().insert(uuid + ' ');
            //this.props.focusActionBar();
        }.bind(this), 'keydown');
    },

    updateRowIndex: function(rowIndex, open) {
        if (!open) {
          // Just highlight it
          this.props.setFocus(this.props.focusIndex, rowIndex);
        } else {
          // Actually open this worksheet.
          var uuid = this.refs['row' + rowIndex].props.uuid;
          this.props.openWorksheet(uuid);
        }
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

    shouldComponentUpdate: function(nextProps, nextState) {
      return worksheetItemPropsChanged(this.props, nextProps);
    },

    render: function() {
        if (this.props.active && this.props.focused)
          this.capture_keys();

        var self = this;
        var tableClassName = (this.props.focused ? 'table focused' : 'table');
        var canEdit = this.props.canEdit;
        var items = this._getItems();

        var body_rows_html = items.map(function(row_item, row_index) {
            var row_ref = 'row' + row_index;
            var row_focused = self.props.focused && (row_index == self.props.subFocusIndex);
            var url = '/worksheets/' + row_item.interpreted.uuid;
            return <TableWorksheetRow
                     key={row_index}
                     ref={row_ref}
                     item={row_item}
                     rowIndex={row_index}
                     focused={row_focused}
                     url={url}
                     uuid={row_item.interpreted.uuid}
                     canEdit={canEdit}
                     updateRowIndex={self.updateRowIndex}
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
        return {};
    },

    handleRowClick: function() {
      // Select row
      this.props.updateRowIndex(this.props.rowIndex, false);
    },

    handleTextClick: function(event) {
      var newWindow = true;
      // TODO: same window is broken, so always open in new window
      //var newWindow = event.ctrlKey;
      if (newWindow) {
        // Open in new window
        var item = this.props.item.interpreted;
        var ws_url = '/worksheets/' + item.uuid;
        window.open(ws_url, '_blank');
      } else {
        // Open in same window
        this.props.updateRowIndex(this.props.rowIndex, true);
      }
    },

    render: function() {
        var item = this.props.item.interpreted;
        var worksheet_display = item.name;
        if (item.title) {
            worksheet_display = item.title + " [" + item.name + "]";
        }

        var className = /*'type-worksheet' + */(this.props.focused ? ' focused' : '');
        return (
            <tr className={className}><td>
              <div onClick={this.handleRowClick}>
                <a href="javascript:0" onClick={this.handleTextClick}>
                    {worksheet_display}
                </a>
              </div>
            </td></tr>
        );
    }
})
