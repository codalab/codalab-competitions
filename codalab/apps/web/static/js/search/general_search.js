/** @jsx React.DOM */

var fakedata = {
    red: 'doRed',
    green: 'doGreen',
    blue: 'doBlue',
    orange: 'doOrange',
    yellow: 'doYellow',
    save: 'doSave'
    };

var Search = React.createClass({
    getInitialState: function(){
        return {
            value: '',
            open: false,
            results: []
        };
    },
    componentDidMount: function(){
        _this = this;
        $('#search').select2({
            multiple:true,
            tags: function(){
                options = [];
                for(key in fakedata){
                    options.push(key);
                }
                return options;
            },
            tokenSeparators: [":", " ", ","],
            createSearchChoicePosition: 'bottom'
        })
        .on('select2-focus', function(){
            _this.handleFocus();
        });
        $('#s2id_search').on('keydown', '.select2-input', function(e){
            switch(e.keyCode){
                case 9:
                    e.preventDefault();
                    break;
                case 13:
                    e.preventDefault();
                    _this.executeCommands();
                    break;
                default:
                    return true;
            }
        });
    },
    executeCommands: function(){
        var command = $('#search').select2('val');
        for(i=0; i < command.length; i++){
            ws_searchActions[fakedata[command[i]]]();
        }
    },
    componentWillUnmount: function(){
        $('#search').select2('destroy');
    },
    handleFocus: function(){
        ws_interactions.state.worksheetKeyboardShortcuts = false;
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
