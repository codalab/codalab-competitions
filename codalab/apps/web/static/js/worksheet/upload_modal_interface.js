/** @jsx React.DOM */

var UploadModal = React.createClass({
    getInitialState: function(){
        return{
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
    onSubmit: function(e){
        e.stopPropagation();
        e.preventDefault();

        var fd = new FormData();
        fd.append( 'file', this.refs.file.getDOMNode().files[0] );
        //
        $.ajax({
            url:'/api/bundles/upload_url/',
            data: fd,
            processData: false,
            contentType: false,
            cache: false,
            type: 'POST',
            success: function(data, status, jqXHR){
                console.log('uplaoded');
                console.log(data);
                console.log('');
            }.bind(this),
            error: function(jqHXR, status, error){

            }.bind(this)
        });
    },
    render: function() {
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
