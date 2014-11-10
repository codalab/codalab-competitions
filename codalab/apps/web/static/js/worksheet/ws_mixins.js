/** @jsx React.DOM */

var Select2SearchMixin = {
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        _this = this;
        // get our static list of commands and store it in this var
        var optionsList = ws_actions.getCommands();
        $('#search').select2({
            multiple:true,
            data: function(){
                return {results: optionsList};
                // data represents the list of possible autocomplete matches.
                // We make this a function returning the contents of optionsList
                // so we can dynamically change those contents later.
            },
            formatSelection: function(item){
                return item.id
                // When you search for a command, you should see its name and a description of what it
                // does. This comes from the command's helpText in the command dict.
                // But after you make a selection, we only want to show the relevant command in the command line
            },
         }).on('change', function(){
            // Select2 is masking the actual #search field. Its value only changes when something new is entered
            // via select2. So when the value of #search changes, we know we need to reevaluate the context
            // in which select2 is being used (eg, we've gone from entering a command to looking up a bundle)
            var input = $(this).val();
            if(input.length){ // if there's something in the commandline...
                // if the last thing entered in the command line is in our known list of commands
                if(ws_actions.commands.hasOwnProperty(_.last(input.split(',')))){
                    // we need to update the data source for the autocomplete, based on the command entered
                    loadDynamicOptions(ws_actions.commands[input]);
                }
            } else {
                // reset to intial list of commands
                optionsList = ws_actions.getCommands();
            }
        }).on('select2-open', function(){
            _this.props.handleFocus();
        });
        //https://github.com/ivaynberg/select2/issues/967
        function loadDynamicOptions(command) {
            // first go make the call to get the list of options, then process it for select2 consumption
            return fetchDynamicOptions(command).done(function(data){
                optionsList = [];
                data.map(function(item){
                    optionsList.push({
                        'id': item.uuid,
                        'text': item.name + ' | ' + item.uuid
                    });
                });
            });
        }
        function fetchDynamicOptions(command) {
            // command is the object from ws_actions.commands. It knows what api endpoint (url) it needs to hit
            // to get a list of options relevant to its command. For instance, the "add" command knows it needs
            // to look for bundles.
            return $.ajax({
                url: command.url,
                type: 'get',
                dataType: 'json'
                // data: { option: command }, // if we need to send something to the API, we can do it here
            });
        }
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
        var input = $('#search').select2('val'); // this comes in as an array
        // customization can be done here, depending on the desired syntax of commands.
        // currently, this just calls all of the functions named in the input
        var command = input[0];
        if(ws_actions.commands.hasOwnProperty(command)){
            ws_actions[ws_actions.commands[command].functionName](input, ws_actions.commands[command]);
        } else {
            console.error('The command \'' + command + '\' was not recognized');
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
