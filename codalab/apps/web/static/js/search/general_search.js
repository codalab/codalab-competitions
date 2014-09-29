/** @jsx React.DOM */

// Dictionary of terms that can be entered into the search bar and the names of 
// functions they call. See search_actions.js
var fakedata = {
    red: 'doRed',
    green: 'doGreen',
    blue: 'doBlue',
    orange: 'doOrange',
    yellow: 'doYellow',
    save: 'doSave'
    };


var Search = React.createClass({
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
        })
        .on('select2-focus', function(){
            _this.handleFocus();
        })
        .on('select2-blur', function(){
            _this.handleBlur();
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
    executeCommands: function(){
        // parse and execute the contents of the search input
        var command = $('#search').select2('val'); // this comes in as an array
        // customization can be done here, depending on the desired syntax of commands.
        // currently, this just calls all of the functions named in the input
        for(i=0; i < command.length; i++){
            var input = fakedata[command[i]];
            if(ws_searchActions.hasOwnProperty(input)){
                ws_searchActions[input]();
            } else {
                console.error('The command \'' + command[i] + '\' was not recognized');
            }
        }
    },
    componentWillUnmount: function(){
        // when the component unmounts, destroy the select2 instance
        $('#search').select2('destroy');
    },
    handleFocus: function(){
        // when the search bar is focused, turn off keyboard shortcuts for the
        // rest of the worksheet. This is done in two parts: change the interactions store
        // then trigger Worksheet to update its state
        ws_interactions.state.worksheetKeyboardShortcuts = false;
        ws_broker.fire('updateState');
    },
    handleBlur: function(){
        // see handleFocus method
        ws_interactions.state.worksheetKeyboardShortcuts = true;
        ws_broker.fire('updateState');
    },
    render: function(){
        return (
            <div className="row">
                <div className="large-12 columns general-search-container">
                    <input id="search" type="text" placeholder='General search box' onFocus={this.handleFocus} />
                </div>
            </div>
        );
    }
});

var general_search = <Search />;
React.renderComponent(general_search, document.getElementById('general_search'));
