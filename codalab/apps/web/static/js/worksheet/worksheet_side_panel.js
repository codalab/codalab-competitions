/** @jsx React.DOM */
var WorksheetSidePanel = React.createClass({
    focustype: 'worksheet', // worksheet, bundle or None
    getInitialState: function(){
        return { };
    },
    componentDidMount: function(){
        var self = this;
        $('#dragbar').mousedown(function(e){
            self.resizePanel(e);
        });
        $(document).mouseup(function(e){
            $(this).unbind('mousemove');
        });
    },
    current_focus: function(){
        var focus = ''
        if(this.props.focusIndex > -1){
            focus = ws_obj.state.items[this.props.focusIndex].state;
            if(focus.mode == "markup"){
                // this.focustype = undefined;
                //for now lets default it back to showing worksheet info
                focus = ws_obj.state;
                this.focustype = 'worksheet'
            }
            else{
                this.focustype = 'bundle'
            }
        }else{
            focus = ws_obj.state;
            this.focustype = 'worksheet'
        }
        return  focus
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
        current_focus = this.current_focus();
        side_panel_details = ''
        switch (this.focustype) {
            case 'worksheet':
                side_panel_details = <WorksheetDetailSidePanel
                                        item={current_focus}
                                    />
                break;
            case 'bundle':
                side_panel_details = <BundleDetailSidePanel
                                        item={current_focus}
                                        subFocusIndex={this.props.subFocusIndex}
                                    />
                break;
            default:
                break;
        }


        return (
            <div className="ws-panel">
                {side_panel_details}
            </div>
        )
    }
});



/** @jsx React.DOM */
var WorksheetDetailSidePanel = React.createClass({
    getInitialState: function(){
        return { };
    },
    componentDidMount: function(){

    },
    componentWillUnmount: function(){

    },
    render: function(){
        var worksheet = this.props.item;


        return (
            <div id="panel_content">
                <h3>{worksheet.name}</h3>
                <p>{worksheet.uuid}</p>
                <p>{worksheet.owner}</p>
            </div>
        )
    }
});
var BundleDetailSidePanel = React.createClass({
    getInitialState: function(){
        return { };
    },
    componentDidMount: function(){

    },
    componentWillUnmount: function(){

    },
    render: function(){
        var item = this.props.item;
        var bundle_info = item.bundle_info[this.props.subFocusIndex]
        var bundle_url = '/bundles/' + bundle_info.uuid;

        return (
            <div id="panel_content">
                <em>subFocusIndex (maybe wrong): {this.props.subFocusIndex}</em>
                <h2>{bundle_info.uuid}</h2>
                <a target="_blank" href="{bundle_url}">{bundle_info.uuid}</a>
            </div>
        )
    }
});