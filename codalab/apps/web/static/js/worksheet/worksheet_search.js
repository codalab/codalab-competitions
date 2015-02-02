/** @jsx React.DOM */

var WorksheetSearch = React.createClass({
    // ********************************************
    // please see ws_actions the goal of WorksheetSearch
    // is to be a generic front end for all actions and select2
    // for all new actions please add in ws_actions.
    // ********************************************
    componentDidMount: function(){
        // when the component has mounted, init the select2 plugin on the
        // general search input (http://ivaynberg.github.io/select2/)
        var self = this;
        // get our static list of commands and store it in this var
        var commands = ws_actions.getCommands();
        $('#search').select2({
            multiple:true,
            minimumInputLength: function(){
                var input = $('#search').val();
                var command = ws_actions.checkAndReturnCommand(input);
                if(command){
                    if(command.hasOwnProperty('minimumInputLength')){
                        return command.minimumInputLength;
                    }else{
                        return 0;
                    }
                }
                //sane defaults
                switch(input){
                    case '':
                        return 0;
                    default:
                        return 3;
                }
            },
            maximumSelectionSize:function(){
                var input = $('#search').val();
                var command = ws_actions.checkAndReturnCommand(input);
                if(command){
                    if(command.hasOwnProperty('maximumSelectionSize')){
                        if($.isFunction(command.maximumSelectionSize)){
                            return command.maximumSelectionSize();
                        }else{
                            return command.maximumSelectionSize;
                        }
                    }else{
                        return 0;
                    }
                }
                //sane defaults
                return 0;
            },
            formatSelection: function(item){
                return item.id;
                // When you search for a command, you should see its name and a description of what it
                // does. This comes from the command's helpText in the command dict.
                // But after you make a selection, we only want to show the relevant command in the command line
            },

            // custom query method, called on every keystroke over the min length
            // see http://ivaynberg.github.io/select2/#doc-query
            createSearchChoice: function(term){
                var input = $('#search').val();
                var command = ws_actions.checkAndReturnCommand(input); // will return undefined if doesnt exist.
                if(command){
                    if(command.hasOwnProperty('searchChoice')){
                        // { id: term, text: 'helper text you"ve entered term' };
                        return command.searchChoice(command, term);
                    }
                }
            },
            query: function(query){

                // Select2 is masking the actual #search field. Its value only changes when something new is entered
                // via select2. So when the value of #search changes, we know we need to reevaluate the context
                // in which select2 is being used (eg, we've gone from entering a command to looking up a bundle)
                var input = query.element.val();
                // if there's something in the commandline AND
                // if the last thing entered in the command line is in our known list of commands,
                // we know we need to start hitting the API for results
                var command = ws_actions.checkAndReturnCommand(input);
                if(input.length && command ){
                    // get our action object that tells us what to do (ajax url)
                    if(command.hasOwnProperty('queryfn')){
                        command.queryfn(query);
                    }else{ // no query fn, just fall back to nothing
                        query.callback({
                            results: []
                        });
                    }
                }else{
                    // either a command hasn't been entered or it wasn't one we support, so
                    // let's make a list of our known commands
                    // console.log('searching commands...');
                    var matchedOptions = [];
                    commands.map(function(item){
                        // we need to make our own matcher function because we're doing this
                        // custom thing. This is just a reimplementation of select2's default
                        // matcher. See http://ivaynberg.github.io/select2/#doc-matcher
                        if(item.id.toUpperCase().indexOf(query.term.toUpperCase())>=0){
                            matchedOptions.push(item);
                        }
                    });
                    console.log(matchedOptions.length + ' results');
                    // now pass back these results the same way we did the ajax ones
                    query.callback({
                        results: matchedOptions
                    });
                }// end of else
            }
        }).on('select2-open', function(){
            // because select2 is masking the actual #search field, we need to manually trigger
            // its focus event when select2 is invoked
            self.props.handleFocus();
        }).on('select2-close', function(){
            // because select2 is masking the actual #search field, we need to manually trigger
            // its focus event when select2 is invoked
            self.props.handleBlur();
        });

        $('#s2id_search').on('keydown', '.select2-input', function(e){
            // add some custom key events for working with the search bar
            switch(e.keyCode){
                case 9: // tab
                    // usually the Tab key would move focus off the search input, so
                    // we want to prevent that
                    e.preventDefault();
                    break;
                case 13: // enter
                    console.log('enter');
                    // cmd-enter or ctrl-enter triggers execution of whatever is
                    // in the search input
                    e.preventDefault();
                    self.executeCommands();
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
    refreshAndClear: function(){
        this.props.refreshWorksheet();
        $('#search').select2('val','').val('');
    },
    executeCommands: function(){
        // parse and execute the contents of the search input
        var input = $('#search').select2('val'); // this comes in as an array
        // customization can be done here, depending on the desired syntax of commands.
        // currently, this just calls all of the functions named in the input
        var entered_command = input[0];
        var command = ws_actions.checkAndReturnCommand(entered_command);
        if(command){
            command.executefn(input, ws_actions.commands[entered_command], this.refreshAndClear);
        } else {
            console.error('The command \'' + entered_command + '\' was not recognized');
        }
    },
    handleKeydown: function(event){
        // the only key the searchbar cares about is esc. Otherwise we're just typing in the input.
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            switch (key) {
                case 'esc':
                    event.preventDefault();
                    this.props.handleBlur();
                    break;
                default:
                    return true;
            }
        }
    },
    render: function(){
        return (
            <div className="ws-search">
                <div className="container">
                    <div className="input-group">
                        <input id="search" type="hidden" placeholder="General search/command line" />
                        <span className="input-group-btn">
                            <button className="btn btn-default" type="button" onClick={this.executeCommands}>Go</button>
                        </span>
                    </div>
                </div>
            </div>
        )
    }
});