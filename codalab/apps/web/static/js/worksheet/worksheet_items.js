/** @jsx React.DOM */

/*
Displays the list of items on the worksheet page.
A worksheet item is an interpreted items (either a contiguous block of markup
or a table, record, image, contents).  Note: different from worksheet item in
the bundle service.
*/

var WorksheetItemList = React.createClass({
    getInitialState: function() {
        return {};
    },
    throttledScrollToItem: undefined, // for use later
    componentDidMount: function() {
        this.props.refreshWorksheet();
    },
    componentDidUpdate: function() {
        var info = this.props.ws.info;
        if (!info || !info.items.length) {
            $('.empty-worksheet').fadeIn('fast');
        }
        if (this.state.editMode) {
            $('#raw-textarea').trigger('focus');
        }
    },

    capture_keys: function() {
        if (!this.props.active)  // If we're not the active component, don't bind keys
            return;

        // Open a new window (really should be handled at the item level)
        Mousetrap.bind(['enter'], function() {
            if (this.props.focusIndex < 0) return;
            var url = this.refs['item' + this.props.focusIndex].props.url;
            if (url)
              window.open(url, '_blank');
        }.bind(this), 'keydown');

        // Move focus up one
        Mousetrap.bind(['up', 'k'], function() {
            this.props.setFocus(this.props.focusIndex - 1, 'end');
        }.bind(this), 'keydown');

        // Move focus to the top
        Mousetrap.bind(['g g'], function() {
            $('body').stop(true).animate({scrollTop: 0}, 'fast');
            this.props.setFocus(-1, 0);
        }.bind(this), 'keydown');

        // Move focus down one
        Mousetrap.bind(['down', 'j'], function() {
            this.props.setFocus(this.props.focusIndex + 1, 0);
        }.bind(this), 'keydown');

        // Move focus to the bottom
        Mousetrap.bind(['shift+g'], function() {
            this.props.setFocus(this.props.ws.info.items.length - 1, 'end');
            $('html, body').animate({scrollTop: $(document).height()}, 'fast');
        }.bind(this), 'keydown');
    },

    render: function() {
        this.capture_keys(); // each item capture keys are handled dynamically after this call

        // Create items
        var items_display;
        var info = this.props.ws.info;
        if (info && info.items.length > 0) {
            var worksheet_items = [];
            info.items.forEach(function(item, index) {
                var focused = (index == this.props.focusIndex);
                var props = {
                  item: item,
                  version: this.props.version,
                  active: this.props.active,
                  focused: focused,
                  canEdit: this.props.canEdit,
                  focusIndex: index,
                  subFocusIndex: focused ? this.props.subFocusIndex : null,
                  setFocus: this.props.setFocus,
                  focusActionBar: this.props.focusActionBar,
                  openWorksheet: this.props.openWorksheet,
                };
                addWorksheetItems(props, worksheet_items);
            }.bind(this));
            items_display = worksheet_items;
        } else {
          items_display = <p className="empty-worksheet">(empty)</p>;
        }
        if (info && info.error)
          items_display = <p className="alert-danger">Error in worksheet: {info.error}</p>;

        return <div id="worksheet_items">{items_display}</div>;
    }
});

////////////////////////////////////////////////////////////

// Create a worksheet item based on props and add it to worksheet_items.
// - item: information about the table to display
// - index: integer representing the index in the list of items
// - focused: whether this item has the focus
// - canEdit: whether we're allowed to edit this item
// - setFocus: call back to select this item
// - updateWorksheetSubFocusIndex: call back to notify parent of which row is selected (for tables)
var addWorksheetItems = function(props, worksheet_items) {
    var item = props.item;

    // Unpack search item into a table.
    if (item.mode == 'search') {
      var subitem = item.interpreted.items[0];
      if (!subitem) {
        subitem = {'interpreted': '(no results)', 'mode': 'markup'};
        //console.error('Invalid item', item);
      }
      var subprops = {};
      for (var k in props) subprops[k] = props[k];
      subprops.item = subitem;
      subprops.focusIndex = props.focusIndex;
      addWorksheetItems(subprops, worksheet_items);
      return;
    }

    // Determine URL corresponding to item.
    var url = null;
    if (item.bundle_info && item.bundle_info.uuid)
      url = '/bundles/' + item.bundle_info.uuid;
    if (item.subworksheet_info)
      url = '/worksheets/' + item.subworksheet_info.uuid;

    props.key = props.ref = 'item' + props.focusIndex;
    props.url = url;

    var constructor = {
      'markup': MarkdownBundle,
      'table': TableBundle,
      'contents': ContentsBundle,
      'worksheet': WorksheetBundle,
      'wsearch': WorksheetBundle,
      'html': HTMLBundle,
      'record': RecordBundle,
      'image': ImageBundle,
      'graph': GraphBundle,
    }[item.mode];

    var elem;
    if (constructor) {
      elem = React.createElement(constructor, props);
    } else {
      elem = (
          <div>
              <strong>
                  Internal error: {item.mode}
              </strong>
          </div>
      );
    }
    worksheet_items.push(elem);
};
