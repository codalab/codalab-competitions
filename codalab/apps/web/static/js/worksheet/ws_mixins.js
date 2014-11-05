/** @jsx React.DOM */

var Select2SearchMixin = {
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        _this = this;
        $('#search').select2({
            multiple:true,
            tags: function(){ // make a list of possible search results from the clActions dict
                options = [];
                for(var key in clActions){
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
        var input = clActions[command[0]];
        if(ws_actions.hasOwnProperty(input)){
            ws_actions[input](command);
        } else {
            console.error('The command \'' + command[i] + '\' was not recognized');
        }
    }
};   // end of Select2SearchMixin

var CheckboxMixin = {
    handleCheck: function(event){
        this.setState({checked: event.target.checked});
        if(this.hasOwnProperty('toggleCheckRows')){
            this.toggleCheckRows();
        }
    }
};
