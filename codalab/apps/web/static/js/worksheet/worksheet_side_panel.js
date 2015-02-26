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
                <h3 className="ws-name">{worksheet.name}</h3>
                <p className="ws-uuid">{worksheet.uuid}</p>
                <p className="ws-owner">{worksheet.owner}</p>
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
        var bundle_info;
        if(item.bundle_info instanceof Array){ //tables are arrays
            bundle_info = item.bundle_info[this.props.subFocusIndex]
        }else{ // content/images/ect. are not
            bundle_info = item.bundle_info
        }
        var bundle_url = '/bundles/' + bundle_info.uuid;
        var bundle_download_url = "/bundles/" + bundle_info.uuid + "/download";
        // bundle_info.name = "Wyle E Coyoted";
        var bundle_name;
        if(bundle_info.metadata.name){
            bundle_name = <h3 className="bundle-name">{ bundle_info.metadata.name }</h3>
        }
        var bundle_state_class = 'bundle-state state-' + (bundle_info.state || 'ready')
        // "uuid": "",
        // "hard_dependencies": [],
        // "state": "ready",
        // "dependencies": [],
        // "command": null,
        // "bundle_type": "",
        // "metadata": {},
        // "files": {},
        var bundle_description = bundle_info.metadata.description ? <p className="bundle-description">{bundle_info.metadata.description}</p> : ''
        var dependencies = bundle_info.dependencies
        var dependencies_list_html = dependencies.map(function(d, index) {
            var dep_bundle_url = '/bundles/' + d.parent_uuid;
            return (
                    <tr>
                        <th>
                            {d.parent_name}
                        </th>
                        <td>
                            <a href={dep_bundle_url} className="bundle-link" target="_blank">
                                {d.parent_uuid}
                            </a>
                        </td>
                    </tr>
                )
        });
        var metadata = bundle_info.metadata
        var metadata_list_html = [];
        for (var property in metadata) {
            if (metadata.hasOwnProperty(property)) {
                metadata_list_html.push(
                    <tr>
                        <th>
                            {property}
                        </th>
                        <td>
                            <span >
                                {metadata[property]}
                            </span>
                        </td>
                    </tr>
                )
            }
        }
        // <em>subFocusIndex (maybe wrong): {this.props.subFocusIndex}</em>
        return (
            <div id="panel_content">
                <div className="bundle-header">
                    {bundle_name}
                    <div className="bundle-links">
                        <a href={bundle_url} className="bundle-link" target="_blank">{bundle_info.uuid}</a>
                        <a href={bundle_download_url} className="bundle-download btn btn-default btn-sm" alt="Download Bundle">
                            <span className="glyphicon glyphicon-download-alt"></span>
                        </a>
                    </div>
                    { bundle_description }
                </div>
                <table className="bundle-meta table">
                    <tbody>
                        <tr>
                            <th>
                                state:
                            </th>
                            <td>
                                <span className={bundle_state_class}>
                                    {bundle_info.state || 'ready'}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                command:
                            </th>
                            <td>
                                {bundle_info.command || "<none>"}
                            </td>
                        </tr>
                    </tbody>
                </table>
                <h4>metadata </h4>
                <table className="bundle-meta table">
                    <tbody>
                        {metadata_list_html}
                    </tbody>
                </table>
                <h4>dependencies</h4>
                <table className="bundle-meta table">
                    <tbody>
                        {dependencies_list_html}
                    </tbody>
                </table>
            </div>
        )
    }
});