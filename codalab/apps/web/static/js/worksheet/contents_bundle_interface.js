/** @jsx React.DOM */

var ContentsBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function(){
        this.props.item.state.checked = false;
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
            <div className="ws-item">
                <input type="checkbox" className="ws-checkbox" onChange={this.handleCheck} checked={this.state.checked} />
                <div className={className} ref={this.props.item.state.ref}>
                    <blockquote>
                        <p dangerouslySetInnerHTML={{__html: contents}} />
                    </blockquote>
                </div>
            </div>
        );
    } // end of render function
}); //end of  ContentsBundle
