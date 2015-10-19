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
            worksheet: {  // TODO: how is this different from ws_obj?
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

        var focusIndex      = this.state.focusIndex;
        var canEdit         = this.props.canEdit;
        var setFocus        = this.setFocus;
        var updateWSFI      = this.props.updateWorksheetSubFocusIndex; // when on a table, understand which bundle user has selected

        // Create items
        var items_display;
        if (ws_obj.state.items.length > 0) {
            var worksheet_items = [];
            ws_obj.state.items.forEach(function(item, index) {
                var focused = (index === focusIndex);
                worksheet_items.push(WorksheetItemFactory(item, index, focused, canEdit, setFocus, updateWSFI));
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
var WorksheetItemFactory = function(item, index, focused, canEdit, setFocus, updateWorksheetSubFocusIndex) {
    var ref = 'item' + index;

    // Determine URL corresponding to item.
    var url = null;
    if (item.state.bundle_info && item.state.bundle_info.uuid)
      url = '/bundles/' + item.state.bundle_info.uuid;
    if (item.state.subworksheet_info)
      url = '/worksheets/' + item.state.subworksheet_info.uuid;

    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'table':
            return <TableBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'contents':
            return <ContentsBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'html':
            return <HTMLBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'record':
            return <RecordBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'image':
            return <ImageBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                   />;
        case 'worksheet':
            return <WorksheetBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                    />;
        case 'search':
            return <SearchBundle
                     key={ref}
                     ref={ref}
                     url={url}
                     item={item}
                     index={index}
                     focused={focused}
                     canEdit={canEdit}
                     setFocus={setFocus}
                     updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                    />;
        default:  // something new or something we dont yet handle
            return (
                <div>
                    <strong>
                        Not supported yet: {item.state.mode}
                    </strong>
                </div>
            );
    }
}
