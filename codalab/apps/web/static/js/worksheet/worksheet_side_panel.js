/** @jsx React.DOM */
var WorksheetSidePanel = React.createClass({
    componentDidMount: function(){
        var self = this;
        $('#dragbar').mousedown(function(e){
            self.resizePanel(e);
        });
        $(document).mouseup(function(e){
            $(this).unbind('mousemove');
        });
    },
    componentWillUnmount: function(){

    },
    resizePanel: function(e){
        e.preventDefault();
        $(document).mousemove(function(e){
            var windowWidth = $(window).width();
            var panelWidth = (windowWidth - e.pageX) / windowWidth * 100;
            if(10 < panelWidth && panelWidth < 55){
                $('.ws-container').css('width', e.pageX);
                $('.ws-panel').css('width', panelWidth + '%');
                $('#dragbar').css('right', panelWidth + '%');
            }
        });
    },
    render: function(){
        return (
            <div className="ws-panel">
                <div id="panel_content">
                    <h3>Here</h3>
                    <p>{this.props.focusIndex}</p>
                </div>
            </div>
        )
    }
});