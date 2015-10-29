/** @jsx React.DOM */

/*
Displays the list of items on the worksheet page.
A worksheet item is either a contiguous block of markup or a table, record, image, contents.
The main difference between the interpreted_items is that markup is grouped together.

All of the editing functionality here is deprecated, since it's too complicated to maintain
and to keep in sync with the markdown.  We are switching to pure markdown editing.
*/

var WorksheetItemList = React.createClass({
    getInitialState: function() {
        return {
            focusIndex: -1, // Index of item that we're focused on.
            checkboxEnabled: true,
            worksheet: {  // TODO: how is this different from this.props.ws?
                last_item_id: 0,
                name: '',
                owner: null,
                owner_id: 0,
                uuid: 0,
                items: [],
                edit_permission: false,
                raw: []
            }
        };
    },
    throttledScrollToItem: undefined, // for use later
    componentDidMount: function() {
        this.props.refreshWorksheet();
    },
    componentDidUpdate: function() {
        if (!this.state.worksheet.items.length) {
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
            this.setFocus(this.state.worksheet.items.length - 1, 'end');
            $("html, body").animate({ scrollTop: $(document).height() }, 'fast');
        }.bind(this), 'keydown');
    },

    setFocus: function(index, subIndex) {
        if (index < -1 || index >= this.state.worksheet.items.length)
          return;  // Out of bounds (note -1 is okay)
        //console.log('WorksheetItemList.setFocus', index, subIndex);

        this.setState({focusIndex: index});
        this.props.updateWorksheetFocusIndex(index);  // Notify parent of selection (so we can show the right thing on the side panel)
        if (index != -1 && subIndex != null) {
          // Change subindex (for tables)
          var item = this.state.worksheet.items[index].state;
          if (item.mode == 'table') {
            if (subIndex == 'end') {
              subIndex = item.bundle_info.length - 1;  // Last row of table
            }
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
            if (item.props.item.state.mode == 'table')  // Table scrolling is handled at the row level
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
        if (this.props.ws.state.items.length > 0) {
            var worksheet_items = [];
            this.props.ws.state.items.forEach(function(item, index) {
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
                worksheet_items.push(createWorksheetItem(props));
            });
            items_display = worksheet_items;
        } else {
          items_display = <p className="empty-worksheet">(empty)</p>;
        }

        return <div id="worksheet_items">{items_display}</div>
    }
});

////////////////////////////////////////////////////////////

// Create a worksheet item.
// - item: information about the table to display
// - index: integer representing the index in the list of items
// - focused: whether this item has the focus
// - canEdit: whether we're allowed to edit this item
// - setFocus: call back to select this item
// - updateWorksheetSubFocusIndex: call back to notify parent of which row is selected (for tables)
var createWorksheetItem = function(props) {
    // Determine URL corresponding to item.
    var state = props.item.state;
    var url = null;
    if (state.bundle_info && state.bundle_info.uuid)
      url = '/bundles/' + state.bundle_info.uuid;
    if (state.subworksheet_info)
      url = '/worksheets/' + state.subworksheet_info.uuid;

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
      'search': SearchBundle
    }[state.mode];

    if (constructor) {
      return React.createElement(constructor, props);
    } else {
      return (
          <div>
              <strong>
                  Not supported yet: {state.mode}
              </strong>
          </div>
      );
    }
}
