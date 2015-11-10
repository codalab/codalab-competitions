/** @jsx React.DOM */

/*
Displays the list of items on the worksheet page.
A worksheet item is an interpreted items (either a contiguous block of markup
or a table, record, image, contents).  Note: different from worksheet item in
the bundle service.
*/

var WorksheetItemList = React.createClass({
    getInitialState: function() {
        return {
            focusIndex: -1, // Index of worksheet item that we're focused on.
        };
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
        Mousetrap.bind(['enter'], function(e) {
            var url = this.refs['item' + this.state.focusIndex].props.url;
            if (url)
              window.open(url, '_blank');
        }.bind(this), 'keydown');

        // Move focus up one
        Mousetrap.bind(['up', 'k'], function(e) {
            this.setFocus(this.state.focusIndex - 1, 'end');
        }.bind(this), 'keydown');

        // Move focus to the top
        Mousetrap.bind(['g g'], function(e) {
            $('body').stop(true).animate({scrollTop: 0}, 'fast');
            this.setFocus(-1, 0);
        }.bind(this), 'keydown');

        // Move focus down one
        Mousetrap.bind(['down', 'j'], function(e) {
            this.setFocus(this.state.focusIndex + 1, 0);
        }.bind(this), 'keydown');

        // Move focus to the bottom
        Mousetrap.bind(['shift+g'], function(e) {
            this.setFocus(this.props.ws.info.items.length - 1, 'end');
            $("html, body").animate({ scrollTop: $(document).height() }, 'fast');
        }.bind(this), 'keydown');
    },

    // If |item| is a table or search with table embedded inside, then return the number of rows
    _numTableRows: function(item) {
      if (item.mode == 'table')
        return item.bundle_info.length;
      if (item.mode == 'search')
        return this._numTableRows(item.interpreted.items[0]);
      return null;
    },

    setFocus: function(index, subIndex) {
        var info = this.props.ws.info;
        if (index < -1 || index >= info.items.length)
          return;  // Out of bounds (note -1 is okay)
        //console.log('WorksheetItemList.setFocus', index, subIndex);

        this.setState({focusIndex: index});
        this.props.updateWorksheetFocusIndex(index);  // Notify parent of selection (so we can show the right thing on the side panel)
        if (index != -1 && subIndex != null) {
          // Change subindex (for tables)
          var item = info.items[index];
          console.log('EEEEEEEEEEE', item);
          var numTableRows = this._numTableRows(item);
          if (numTableRows != null) {
            if (subIndex == 'end')
              subIndex = numTableRows - 1;  // Last row of table
            this.props.updateWorksheetSubFocusIndex(subIndex);  // Notify parent of selection
            this.refs['item' + index].focusOnRow(subIndex); // Notify child
          }
        }
        this.scrollToItem(index);
    },

    resetFocusIndex: function() {
        this.setState({focusIndex: -1});
    },

    scrollToItem: function(index) {
        // scroll the window to keep the focused element in view if needed
        var __innerScrollToItem = function(index) {
          // Compute the current position of the focused item.
          var pos;
          if (index == -1) {
            pos = -1000000;  // Scroll all the way to the top
          } else {
            var item = this.refs['item' + index];
            if (this._numTableRows(item.props.item) != null)  // Table scrolling is handled at the row level
              return;
            var node = item.getDOMNode();
            pos = node.getBoundingClientRect().top;
          }
          keepPosInView(pos);
        };

        // Throttle so that if keys are held down, we don't suffer a huge lag.
        if (this.throttledScrollToItem === undefined)
            this.throttledScrollToItem = _.throttle(__innerScrollToItem, 50).bind(this);
        this.throttledScrollToItem(index);
    },

    render: function() {
        this.capture_keys(); // each item capture keys are handled dynamically after this call

        var active = this.props.active;
        var focusIndex = this.state.focusIndex;
        var canEdit = this.props.canEdit;
        var setFocus = this.setFocus;
        var updateWorksheetSubFocusIndex = this.props.updateWorksheetSubFocusIndex;

        // Create items
        var items_display;
        var info = this.props.ws.info;
        if (info && info.items.length > 0) {
            var worksheet_items = [];
            info.items.forEach(function(item, index) {
                var focused = (index === focusIndex);
                var props = {
                  item: item,
                  index: index,
                  active: active,
                  focused: focused,
                  canEdit: canEdit,
                  setFocus: setFocus,
                  updateWorksheetSubFocusIndex: updateWorksheetSubFocusIndex
                };
                addWorksheetItems(props, worksheet_items);
            });
            items_display = worksheet_items;
        } else {
          items_display = <p className="empty-worksheet">(empty)</p>;
        }
        if (info && info.error)
          items_display = <p className="alert-danger">Error in worksheet: {info.error}</p>;

        return <div id="worksheet_items">{items_display}</div>
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

    // These worksheet items unpack into multiple interpreted items.
    if (item.mode == 'search') {
      if (item.interpreted.items.length != 1) {
          console.error('Expected exactly one item, but got', item.interpreted.items);
      } else {
        var subitem = item.interpreted.items[0];
        var subprops = {};
        for (var k in props) subprops[k] = props[k];
        subprops.item = subitem;
        subprops.index = props.index;
        addWorksheetItems(subprops, worksheet_items);
      }
      return;
    }

    // Determine URL corresponding to item.
    var url = null;
    if (item.bundle_info && item.bundle_info.uuid)
      url = '/bundles/' + item.bundle_info.uuid;
    if (item.subworksheet_info)
      url = '/worksheets/' + item.subworksheet_info.uuid;

    props.key = props.ref = 'item' + props.index;
    props.url = url;

    var constructor = {
      'markup': MarkdownBundle,
      'table': TableBundle,
      'contents': ContentsBundle,
      'worksheet': WorksheetBundle,
      'html': HTMLBundle,
      'record': RecordBundle,
      'image': ImageBundle,
    }[item.mode];

    var elem;
    if (constructor) {
      elem = React.createElement(constructor, props);
    } else {
      elem = (
          <div>
              <strong>
                  Not supported yet: {state.mode}
              </strong>
          </div>
      );
    }
    worksheet_items.push(elem);
}
