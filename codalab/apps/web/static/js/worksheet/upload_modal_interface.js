/** @jsx React.DOM */

var UploadModal = React.createClass({
    getInitialState: function(){
        return{
            "error": null,
            "is_uploading": false
        }
    },
    componentDidMount: function() {
        this.resetState();
        $(this.getDOMNode()).modal({background: true, keyboard: true, show: false});
        this.show(); //  un/comment to get modal as pages loads for testing.
    },
    componentWillUnmount: function() {
        $(this.getDOMNode()).off('hidden');
    },
    resetState: function(){
        this.setState({"error": null, "is_uploading": false});
    },
    show: function(){
        $(this.getDOMNode()).modal('show');
        this.resetState();
    },
    hide: function(){
        $(this.getDOMNode()).modal('hide');
        this.resetState();
    },
    onSubmit: function(e){
        this.setState({"error": null, "is_uploading": true});
        e.stopPropagation();
        e.preventDefault();

        var fd = new FormData();
        fd.append( 'file', this.refs.file.getDOMNode().files[0] );
        fd.append( 'worksheet_uuid', ws_obj.state.uuid);
        $.ajax({
            url:'/api/bundles/upload_url/',
            data: fd,
            processData: false,
            contentType: false,
            cache: false,
            type: 'POST',
            success: function(data, status, jqXHR){
                this.props.refreshWorksheet();
                // this.hide(); // hidden for testing
            }.bind(this),
            error: function(jqHXR, status, error){
                error = jqHXR.responseJSON['error'];
                this.setState({
                        "error": "there has been an error please try again",
                        "is_uploading": false
                    })
                console.error(status + ': ' + error);

            }.bind(this)
        });
    },
    render: function() {
        var error_html = ''
        if(this.state.error){
            error_html = (  <div className="alert alert-danger" role="alert">
                                {this.state.error}
                            </div>
                        );
        }
        var uploading_html = '';
        if(this.state.is_uploading){
            var style = { width: '100%'}; // to control the % of the progress bar, show 100% and animate it.
            uploading_html = (
                                <div className="progress">
                                  <div  className="progress-bar progress-bar-striped active"
                                        role="progressbar"
                                        style={style}
                                    >
                                    Uploading
                                  </div>
                                </div>
                            )
        }
        return (
            <div className="modal fade" id="ws-bundle-upload" tabindex="-1" role="dialog" aria-hidden="true">
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <button type="button" className="close" data-dismiss="modal">
                                <span aria-hidden="true">&times;</span>
                                <span className="sr-only">Close</span>
                            </button>
                            <h4 className="modal-title" >Upload a Dataset</h4>
                        </div>
                        <form name="uploadForm" onSubmit={this.onSubmit} ref="uploadForm" enctype="multipart/form-data" method="post"  >
                            <div className="modal-body">
                                <p>
                                    <input id="uploadInput" type="file" ref="file" name="file"/>
                                </p>
                                {uploading_html}
                                {error_html}
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
                                <input type="submit" className="btn btn-success" value="Upload" />
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    } // end of render function
}); //end of  UploadModal
