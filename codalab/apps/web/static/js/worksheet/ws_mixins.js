/** @jsx React.DOM */

var TableMixin = {
    // This handles some common elements of worksheet items that are presented as tables
    // TableBundle and RecordBundle
    getInitialState: function(){
        return {
            rowFocusIndex: 0
        };
    },
    handleClick: function(){
        this.props.setFocus(this);
    },
    keysToHandle: function(){
        return['up','k','down','j','x'];
    },
    scrollToRow: function(index){
        // scroll the window to keep the focused row in view
        var offsetTop = 0;
        if(index > -1){
            offsetTop = this.getDOMNode().offsetTop + (this.refs.row0.getDOMNode().offsetHeight * index) - 100;
        }
        $('html,body').animate({scrollTop: offsetTop}, 250);
    },
    handleKeyboardShortcuts: function(event){
        var item = this.props.item.state;
        var key = keyMap[event.keyCode];
        var index = this.state.rowFocusIndex;
        var rowsInTable = item.interpreted[1].length;
        var parentFocusIndex = this._owner.state.focusIndex;
        if(typeof key !== 'undefined'){
            event.preventDefault();
            switch (key) {
                case 'up':
                case 'k':
                    event.preventDefault();
                    if(event.shiftKey && this.props.canEdit){
                        this._owner.moveItem(-1);
                    }else{
                        index = Math.max(this.state.rowFocusIndex - 1, 0);
                        if(this.state.rowFocusIndex === 0){
                            this._owner.setState({focusIndex: parentFocusIndex - 1});
                            this._owner.scrollToItem(parentFocusIndex - 1);
                        }else {
                            this.setState({rowFocusIndex: index});
                            this.scrollToRow(index);
                        }
                    }
                    break;
                case 'down':
                case 'j':
                    event.preventDefault();
                    if(event.shiftKey && this.props.canEdit){
                        this._owner.moveItem(1);
                    }else {
                        index = Math.min(this.state.rowFocusIndex + 1, rowsInTable);
                        if(index == rowsInTable){
                            this._owner.setState({focusIndex: parentFocusIndex + 1});
                            this._owner.scrollToItem(parentFocusIndex + 1);
                        }else {
                            this.setState({rowFocusIndex: index});
                            this.scrollToRow(index);
                        }
                    }
                    break;
                case 'x':
                    event.preventDefault();
                    this.setState({checked: !this.state.checked});
                    break;
                default:
                    return true;
                }
            } else {
                return true;
            }
    }
};  // end of TableMixin

var Select2SearchMixin = {
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        _this = this;
        $('#search').select2({
            multiple:true,
            tags: function(){ // make a list possible search results from the dict
                options = [];
                for(var key in fakedata){
                    options.push(key);
                }
                return options;
            },
            tokenSeparators: [":", " ", ","], // Define token separators for the tokenizer function
            createSearchChoicePosition: 'bottom' // Users can enter their own commands (not autocompleted)
                                                 // but these will show up at the bottom. This allows a user
                                                 // to hit 'tab' to select the first highlighted option
        });
        $('#s2id_search').on('keydown', '.select2-input', function(e){
            // add some custom key events for working with the search bar
            switch(e.keyCode){
                case 9:
                    // usually the Tab key would move focus off the search input, so
                    // we want to prevent that
                    e.preventDefault();
                    break;
                case 13:
                    // cmd-enter or ctrl-enter triggers execution of whatever is
                    // in the search input
                    if(e.ctrlKey || e.metaKey){
                        e.preventDefault();
                        _this.executeCommands();
                    }
                    break;
                default:
                    return true;
            }
        });
    },
    componentWillUnmount: function(){
        // when the component unmounts, destroy the select2 instance
        $('#search').select2('destroy');
    },
    componentDidUpdate: function(){
        if(this.props.active){
            $('#s2id_autogen1').focus();
        }else {
            $('#s2id_autogen1').blur();
        }
    },
    executeCommands: function(){
        // parse and execute the contents of the search input
        var command = $('#search').select2('val'); // this comes in as an array
        // customization can be done here, depending on the desired syntax of commands.
        // currently, this just calls all of the functions named in the input
        for(i=0; i < command.length; i++){
            var input = fakedata[command[i]];
            if(ws_actions.hasOwnProperty(input)){
                ws_actions[input]();
            } else {
                console.error('The command \'' + command[i] + '\' was not recognized');
            }
        }
    }
};   // end of Select2SearchMixin

var CheckboxMixin = {
    handleCheck: function(event){
        this.setState({checked: event.target.checked});
    }
};