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

        // Open worksheet in new window/tab
        Mousetrap.bind(['enter'], function(e) {
            window.open(this.refs['row' + this.props.subFocusIndex].props.url, '_blank');
        }.bind(this), 'keydown');

        // Paste uuid of focused worksheet into console
        Mousetrap.bind(['u'], function(e) {
            var uuid = this.refs['row' + this.props.subFocusIndex].props.uuid;
            $('#command_line').terminal().insert(uuid + ' ');
            //this.props.focusActionBar();
        }.bind(this), 'keydown');
    },

    updateRowIndex: function(rowIndex) {
        this.props.setFocus(this.props.focusIndex, rowIndex);
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
    handleClick: function() {
      this.props.updateRowIndex(this.props.rowIndex);
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
