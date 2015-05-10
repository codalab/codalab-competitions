/** @jsx React.DOM */

var BootstrapModal = React.createClass({
    getInitialState: function(){
        return{
            "header_txt": "",
            "body_txt": "",
            "success_button_txt": "",
            "ws_modal": "ws_modal",
        }
    },
    componentDidMount: function() {
        $(this.getDOMNode()).modal({background: true, keyboard: true, show: false});
    },
    componentWillUnmount: function() {
        $(this.getDOMNode()).off('hidden');
    },
    show: function(){
        $(this.getDOMNode()).modal();
    },
    render: function() {
        var header_txt = this.state.header_txt;
        var body_txt = this.state.body_txt;
        var success_button_txt = this.state.success_button_txt;
        var success_button = '';
        if(success_button_txt){
            success_button = <button type="button" className="btn btn-primary">{success_button_txt}</button>
        }
        return (
            <div className="modal fade" id={this.state.modal_id} tabindex="-1" role="dialog" aria-hidden="true">
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <button type="button" className="close" data-dismiss="modal">
                                <span aria-hidden="true">&times;</span>
                                <span className="sr-only">Close</span>
                            </button>
                            <h4 className="modal-title" >{header_txt}</h4>
                        </div>
                        <div className="modal-body">
                            {body_txt}
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
                            {success_button ? success_button : null}
                        </div>
                    </div>
                </div>
            </div>
        );
    } // end of render function
}); //end of  BootstrapModal
