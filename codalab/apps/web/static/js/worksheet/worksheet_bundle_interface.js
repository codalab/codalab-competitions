/** @jsx React.DOM */

// Display a worksheet item which corresponds to a (sub)worksheet.
var WorksheetBundle = React.createClass({
    mixins: [CheckboxMixin],
    getInitialState: function() {
        return {};
    },
    capture_keys: function(event) {
        Mousetrap.bind(['enter'], function(e) {
            this.goToWorksheet();
        }.bind(this), 'keydown');
    },
    handleClick: function(event) {
        this.props.setFocus(this.props.index);
    },
    goToWorksheet: function() {
        window.open('/worksheets/' + this.props.item.interpreted.uuid);
    },
    render: function() {
        var item = this.props.item.interpreted;
        var className = 'type-worksheet' + (this.props.focused ? ' focused' : '');
        var ws_url = '/worksheets/' + item.uuid;

        var worksheet_display = item.name
        if (item.title) {
            worksheet_display = item.title + " [" + item.name + "]";
        }
        return(
            <div className="ws-item" onClick={this.handleClick}>
                <div className={className}>
                    <a href={ws_url} target="_blank">
                        {worksheet_display}
                    </a>
                </div>
            </div>
        );
    } // end of render function
});
