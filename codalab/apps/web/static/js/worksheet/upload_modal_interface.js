/** @jsx React.DOM */

// Show a modal dialog for uploading bundles.
var UploadModal = React.createClass({
    getInitialState: function(){
        return{
            "bundle_type": 'dataset',
            "error": null,
            "is_uploading": false
        }
    },
    componentDidMount: function() {
        this.resetState();
        $(this.getDOMNode()).modal({background: true, keyboard: true, show: false});
        //this.show(); //  un/comment to get modal as pages loads for testing.
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
    onDataset: function(e) { this.setState({'bundle_type': 'dataset'}); },
    onProgram: function(e) { this.setState({'bundle_type': 'program'}); },
    onSubmit: function(e){
        this.setState({"error": null, "is_uploading": true});
        e.stopPropagation();
        e.preventDefault();

        var fd = new FormData();
        fd.append('file', this.refs.file.getDOMNode().files[0]);
        fd.append('bundle_type', this.state.bundle_type);
        fd.append('worksheet_uuid', this.props.ws.state.uuid);
        $.ajax({
            url:'/api/bundles/upload/',
            data: fd,
            processData: false,
            contentType: false,
            cache: false,
            type: 'POST',
            success: function(data, status, jqXHR){
                this.props.refreshWorksheet();
                this.hide();
            }.bind(this),
            error: function(jqHXR, status, error){
                var error = "Error uploading file."
                if(jqHXR.responseJSON){
                    error = jqHXR.responseJSON['error'];
                }else{
                    error = error
                }
                this.setState({
                    "error": error,
                    "is_uploading": false
                });
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
                                    Uploading...
                                  </div>
                                </div>
                            )
        }
        return (
            <div className="modal fade" id="ws-bundle-upload" tabIndex="-1" role="dialog" aria-hidden="true">
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <button type="button" className="close" data-dismiss="modal">
                                <span aria-hidden="true">&times;</span>
                                <span className="sr-only">Close</span>
                            </button>
                            <h4 className="modal-title" >Upload bundle</h4>
                        </div>
                        <form name="uploadForm" onSubmit={this.onSubmit} ref="uploadForm" encType="multipart/form-data" method="post"  >
                            <div className="modal-body">
                                <p>
                                    Bundle type: &nbsp;
                                    <input type="radio" name="bundleType" value="dataset" onChange={this.onDataset} checked={this.state.bundle_type == 'dataset'}>Dataset</input> &nbsp;
                                    <input type="radio" name="bundleType" value="program" onChange={this.onProgram} checked={this.state.bundle_type == 'program'}>Program</input>
                                </p>
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
}); //end of UploadModal
