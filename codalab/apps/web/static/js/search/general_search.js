/** @jsx React.DOM */

var fakedata = [
    {'term': 'red', 'action': 'doRed'},
    {'term': 'green', 'action': 'doGreen'},
    {'term': 'blue', 'action': 'doBlue'},
    {'term': 'orange', 'action': 'doOrange'},
    {'term': 'yellow', 'action': 'doYellow'},
    {'term': 'save', 'action': 'doSave'}
    ];

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
                fakedata.map(function(item){
                    options.push(item.term);
                })
                return options;
            },
            tokenSeparators: [":", " "]
        })
        .on('select2-focus', function(){
            _this.handleFocus();
        });
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
