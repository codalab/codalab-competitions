/** @jsx React.DOM */

/*
Displays the list of items on the worksheet page.
A worksheet item is either a contiguous block of markup or a table, record, image, contents.
The main difference between the interpreted_items is that markup is grouped together.

All of the editing functionality here is deprecated, since it's too complicated to maintain
and to keep in sync with the markdown.  We are switching to pure markdown editing.
*/

var WorksheetItemList = React.createClass({
    getInitialState: function(){
        return {
            focusIndex: -1, // Index of item that we're focused on.
            editingIndex: -1,
            checkboxEnabled: true,
            worksheet: {
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
        // Set up the debounced version of the save method here so we can call it later
        this.slowSave = _.debounce(this.props.saveAndUpdateWorksheet, 1000);
    },
    componentDidUpdate: function(){
        if(!this.state.worksheet.items.length){
            $('.empty-worksheet').fadeIn('fast');
        }
        if(this.state.editMode){
            $('#raw-textarea').trigger('focus');
        }
    },
    capture_keys: function(){
        // console.log("bind keys for the WorksheetItemList");
        var fIndex = this.state.focusIndex;
        var eIndex = this.state.editingIndex;
        var focusedItem = this.refs['item' + fIndex];
        if(!this.props.active){ // if we are not the active component dont bind keys
            return;
        }

        // Go up
        Mousetrap.bind(['up', 'k'], function(e){
            if(fIndex <= 0){
                // if we're already at the top of the worksheet, we can't go higher
                fIndex = -1;
            }else {
                fIndex = Math.max(this.state.focusIndex - 1, 0);
            }
            this.setFocus(fIndex, e, null, 'up');
        }.bind(this), 'keydown');

        // Go to the top
        Mousetrap.bind(['1 shift+g'], function(e){
            $('body').stop(true).animate({scrollTop: 0}, 50);
            this.setFocus(0, e, null, null);
        }.bind(this), 'keydown');

        // Go down
        Mousetrap.bind(['down', 'j'], function(e){
            // Don't allow moving past the last item. Because the number of ws-item divs might
            // not be the same as the number of item objects because of editing/inserting/whatever,
            // count the actual divs instead
            fIndex = Math.min(this.state.focusIndex + 1, $('#worksheet_content .ws-item').length - 1);
            this.setFocus(fIndex, e, null, 'down');
        }.bind(this), 'keydown');

        // Go to the bottom
        Mousetrap.bind(['shift+g'], function(e){
            fIndex = $('#worksheet_content .ws-item').length - 1;
            this.setFocus(fIndex, e, null, true);
            $("html, body").animate({ scrollTop: $(document).height() }, "fast");
        }.bind(this), 'keydown');

        if (focusedItem && focusedItem.hasOwnProperty('capture_keys')) {
            // pass the event along to the element
            focusedItem.capture_keys();
        }
    },

    scrollToItem: function(index, event){
        // scroll the window to keep the focused element in view if needed
        var __innerScrollToItem = function(index, event){
            var container = $(".ws-container")
            var navbarHeight = parseInt($('body').css('padding-top'));
            var viewportHeight = Math.max($(".ws-container").innerHeight() || 0);

            var item = this.refs['item' + index];
            var node = item.getDOMNode();
            var nodePos = node.getBoundingClientRect(); // get all measurements for node rel to current viewport
             // where is the top of the elm on the page and does it fit in the the upper forth of the page
            var scrollTo = $(".ws-container").scrollTop() + nodePos.top - navbarHeight - (viewportHeight/4);
            // how far node top is from top of viewport
            var distanceFromTopViewPort = nodePos.top - navbarHeight;
            // TODO if moving up aka K we should focus on the bottom rather then the top, maybe? only for large elements?
            // the elm is down the page and we should scrol to put it more in focus
            // console.log('scrolling');
            if(distanceFromTopViewPort > viewportHeight/3){
                $(".ws-container").stop(true).animate({scrollTop: scrollTo}, 45);
                return;
            }
            // if the elment is not in the viewport (way up top), just scroll
            if(distanceFromTopViewPort < 0){
                $(".ws-container").stop(true).animate({scrollTop: scrollTo}, 45);
                return;
            }
        }; // end of __innerScrollToItem

        //throttle it becasue of keydown and holding keys
        if(this.throttledScrollToItem === undefined){ //create if we dont already have it.
            this.throttledScrollToItem = _.throttle(__innerScrollToItem, 75).bind(this);
        }
        this.throttledScrollToItem(index, event);
    },
    resetFocusIndex: function(){
        this.setState({focusIndex: -1});
    },

    setFocus: function(index, event, last_sub_el, direction, scroll) {
        if(typeof(scroll) === 'undefined'){
            scroll = true;
        }
        // index : what item index we want to focus on
        // event : the JS click event or keyboard event
        // last_sub_el: True/False force a focus on the last sub element
        if(index < this.state.worksheet.items.length){
            this.setState({focusIndex: index});
            //pass back up to workshet interface so the app knows which item is slected
            this.props.updateWorksheetFocusIndex(index);
            if(index >= 0) {
                var mode = ws_obj.state.items[index].state.mode;
                var react_el = this.refs['item'+index]
                if(mode === 'table'){
                    this.toggleCheckboxEnable(false);
                    if(direction == 'up'){
                        last_sub_el = true;
                    }
                }else {
                    this.toggleCheckboxEnable(true);
                }
                if(react_el && last_sub_el){ //we have a react item and wish to force last sub item (usefulll for tables)
                    if(react_el.hasOwnProperty('focusOnLast')){
                        react_el.focusOnLast(event);
                    }
                }
                if(typeof(event) !== 'undefined'){
                    // var throttledScrollToItem = _.throttle(this.scrollToItem, 1000).bind(this);
                    // console.log("again?")
                    // throttledScrollToItem(index, event);
                    if(scroll){
                        this.scrollToItem(index, event)
                    }
                }
            }
        }else {
            return false;
        }
    },
    toggleCheckboxEnable: function(enabled){
        this.setState({checkboxEnabled: enabled});
    },

    render: function(){
        this.capture_keys(); // each item capture keys are handled dynamically after this call
        // shortcut naming
        var canEdit         = this.props.canEdit;
        var updateWSFI      = this.props.updateWorksheetSubFocusIndex; // when on a table, understand which bundle user has selected
        var checkboxEnabled = this.state.checkboxEnabled;
        var editingIndex    = this.state.editingIndex;
        var focusIndex      = this.state.focusIndex;
        var handleSave      = this.saveItem;
        var setFocus        = this.setFocus;

        var worksheet_items = [];
        var items_display = <p className="empty-worksheet">This worksheet is empty</p>
        if (ws_obj.state.items.length > 0) {
            ws_obj.state.items.forEach(function(item, i){
                var ref = 'item' + i;
                var focused = i === focusIndex;
                var editing = i === editingIndex;
                //create the item of the correct type and add it to the list.
                worksheet_items.push(WorksheetItemFactory(item, ref, focused, editing, i, handleSave, setFocus, canEdit, checkboxEnabled, updateWSFI));
            });
            items_display = worksheet_items
        }

        return <div id="worksheet_items">{items_display}</div>
    }
});

////////////////////////////////////////////////////////////

// Create a worksheet item.
var WorksheetItemFactory = function(item, ref, focused, editing, i, handleSave, setFocus, canEdit, checkboxEnabled, updateWorksheetSubFocusIndex) {
    switch (item.state.mode) {
        case 'markup':
            return <MarkdownBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                        handleSave={handleSave}
                />
            break;
        case 'inline':
            return <InlineBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'table':
            return <TableBundle
                        key={'tb'+i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}

                        handleSave={handleSave}
                    />
            break;
        case 'contents':
            return <ContentsBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'html':
            return <HTMLBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'record':
            return <RecordBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'image':
            return <ImageBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'worksheet':
            return <WorksheetBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                        updateWorksheetSubFocusIndex={updateWorksheetSubFocusIndex}
                />
            break;
        case 'search':
            return <SearchBundle
                        key={i}
                        index={i}
                        item={item}
                        ref={ref}
                        focused={focused}
                        editing={editing}
                        canEdit={canEdit}
                        setFocus={setFocus}
                        checkboxEnabled={checkboxEnabled}
                />
            break;
        default:  // something new or something we dont yet handle
            return (
                <div>
                    <strong>
                        {item.state.mode}
                    </strong>
                </div>
            )
    }
}
