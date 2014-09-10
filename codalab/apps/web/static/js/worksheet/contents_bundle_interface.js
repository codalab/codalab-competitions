/** @jsx React.DOM */

var ContentsBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        var contents = this.state.interpreted.map(function(item){
            return item.replace(/%\s/, '');
        });
        contents = contents.join('');
        // contents = contents.replace(/%\s/g, '');
        return(
            <blockquote>
                <p dangerouslySetInnerHTML={{__html: contents}} />
            </blockquote>
        );
    } // end of render function
}); //end of  ContentsBundle
