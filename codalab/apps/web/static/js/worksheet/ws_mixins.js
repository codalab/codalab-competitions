/** @jsx React.DOM */

// Dictionary of terms that can be entered into the search bar and the names of
// functions they call. See ws_actions.js
var clActions = [
    {   id: 'add',
        functionName: 'doAdd',
        text: 'add - ask for a bundle uuid',
        api: 'bundle'
    },
    {   id: 'info',
        functionName: 'doInfo',
        text: 'info - go to a bundle\'s info page',
    }
];
var optionsList = clActions;
var Select2SearchMixin = {
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        _this = this;
        var commandOptions = {
            multiple:true,
            data: function(){
                return {results: optionsList};
            },
            formatSelection: function(item){
                return item.id
            },
            tokenSeparators: [":", " ", ","], // Define token separators for the tokenizer function
            createSearchChoicePosition: 'bottom' // Users can enter their own commands (not autocompleted)
                                                 // but these will show up at the bottom. This allows a user
                                                 // to hit 'tab' to select the first highlighted option
        }
        $('#search').select2(commandOptions).on('change', function(){
            var input = $(this).val();
            if(input.length > 0){
                for(var i=0; i < clActions.length; i++){
                    if(input == clActions[i].id){
                        console.log(input);
                        console.log(clActions[i].api);
                        getDynamicOptions(clActions[i].api);
                        break;
                    }
                }
            } else {
                // reset to intial commands
                optionsList = clActions;
            }
        });
        //https://github.com/ivaynberg/select2/issues/967
        function getDynamicOptions(val) { // called by a changeEvent on another element)
            console.log('getDynamicOptions with')
            console.log(val)
            return queryDynamicOptions(val)
                .done( function(data) {
                    console.log('return queryDynamicOptions with data')
                    console.log(data)
                // Empty your existing data before populating a new list
                optionsList = [];
                data.map(function(item){
                    optionsList.push({
                        'id': item.uuid,
                        'text': item.name + ' | ' + item.uuid
                    });
                });
                // // see comment on for queryDynamicOptions() - on what's going on w/ my data
                // $.each(data, function(item) {
                //     // Finally update your optionsList with the data
                //     optionsList.push({ id: vData[0], text: vData[1] });
                //     });
                // });
            });
        }
        function queryDynamicOptions(optionVal) {
            console.log('queryDynamicOptions with')
            console.log(optionVal);
            return $.ajax({
                url: '/api/worksheets/',
                type: 'get',
                data: { option: optionVal },
                dataType: 'json'
            });
        }
        // $('#s2id_search').on('keydown', '.select2-input', function(e){
        //     // add some custom key events for working with the search bar
        //     switch(e.keyCode){
        //         case 9:
        //             // usually the Tab key would move focus off the search input, so
        //             // we want to prevent that
        //             e.preventDefault();
        //             break;
        //         case 13:
        //             // cmd-enter or ctrl-enter triggers execution of whatever is
        //             // in the search input
        //             if(e.ctrlKey || e.metaKey){
        //                 e.preventDefault();
        //                 _this.executeCommands();
        //             }
        //             break;
        //         default:
        //             return true;
        //     }
        // });
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
            console.error('The command \'' + command[0] + '\' was not recognized');
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
