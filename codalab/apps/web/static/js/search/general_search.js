/** @jsx React.DOM */

// var substringMatcher = function(strs) {
//     return function findMatches(q, cb) {
//         var matches, substrRegex;
//         matches = [];
//         q = q.split(' ');
//         q = q[q.length -1];
//         substrRegex = new RegExp(q, 'i');
//         $.each(strs, function(i, str) {
//             // todo split q on space and pop off the last one to match against
//             if (substrRegex.test(str.term)) {
//             matches.push(str);
//         }
//     });
//     cb(matches);
//     };
// };

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
        $('#search').select2({
            tags: function(){
                options = [];
                fakedata.map(function(item){
                    options.push(item.term);
                })
                return options;
            },
        });
    },
    componentWillUnmount: function(){
        
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
