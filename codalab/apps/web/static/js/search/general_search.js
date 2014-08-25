/** @jsx React.DOM */

var fakedata = [
    {term:'red', action:'paint the town red'},
    {term:'green', action:'green like the leaves'},
    {term:'blue', action:'the deep blue sea'},
    {term:'orange', action:'orange you glad I didn\'t say banana?'},
    {term:'yellow', action:'they call me mellow yellow'}
];

var Search = React.createClass({
    getInitialState: function(){
        return {
            value: '',
            open: false,
            results: []
        };
    },
    handleChange: function(event){
        var searchInput = event.target.value;
        if(searchInput.length >= 3){
            this.getResults(searchInput);
        }else {
            this.setState({results: []});
        }
        this.setState({value: searchInput});
    },
    getResults: function(searchInput){
        console.log('------------');
        console.log('Searching for ' + searchInput);
        this.setState({results: fakedata});
    },
    cleanupSearch: function(){
        this.setState({
            value:'',
            results:[]
        });
    },
    render: function(){
        var openClass = this.state.results.length ? 'open' : 'closed';
        var parentCallback = this.cleanupSearch;
        var resultList = this.state.results.map(function(result, index){
            return <SearchResult result={result} key={index} callback={parentCallback} />
        });
        return (
            <div className="row">
                <div className="large-12 columns general-search-container">
                    <input type="text" value={this.state.value} placeholder='General search box' onChange={this.handleChange} />
                    <ul id="search_results" className={openClass}>
                       {resultList}
                    </ul>
                </div>
            </div>
        );
    }
});

var SearchResult = React.createClass({
    doSearchAction: function(){
        console.log('do the search action for ' + this.props.term);
        alert(this.props.result.action.toString());
        this.props.callback();
    },
    render: function(){
        return(
            <li onClick={this.doSearchAction} key={this.props.key}>
                {this.props.result.term}
            </li>
        )
    }
})
var general_search = <Search />;
React.renderComponent(general_search, document.getElementById('general_search'));
