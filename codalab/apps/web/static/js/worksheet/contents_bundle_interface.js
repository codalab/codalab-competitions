/** @jsx React.DOM */

var ContentsBundle = React.createClass({
    getInitialState: function(){
        return this.props.item.state;
    },
    render: function() {
        var className = 'type-contents' + (this.props.focused ? ' focused' : '');
        var contents = this.state.interpreted.map(function(item){
            return item.replace(/%\s/, '');
        });
        contents = contents.join('');
        // contents = contents.replace(/%\s/g, '');
        return(
            <div className={className} ref={this.props.item.state.ref}>
                <blockquote>
                    <p dangerouslySetInnerHTML={{__html: contents}} />
                </blockquote>
            </div>
        );
    } // end of render function
}); //end of  ContentsBundle
