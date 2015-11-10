/*
Information about the current worksheet and its items.
*/

var WorksheetContent = function() {
    function WorksheetContent(url) {
        this.url = url;
        this.info = null;  // Worksheet info
    }

    WorksheetContent.prototype.fetch = function(props) {
        // Set defaults
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};
        if (props.async === undefined){
            props.async = true;
        }

        $.ajax({
            type: 'GET',
            url: this.url,
            async: props.async,
            dataType: 'json',
            cache: false,
            success: function(info) {
                this.info = info;
                props.success(this.info);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    WorksheetContent.prototype.saveWorksheet = function(props) {
        $('#update_progress').show();
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};
        var postdata = {
            'name': this.info.name,
            'uuid': this.info.uuid,
            'owner_id': this.info.owner_id,
            'lines': this.info.raw
        };
        $('#save_error').hide();
        $.ajax({
            type: 'POST',
            cache: false,
            url: this.url,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data: JSON.stringify(postdata),
            success: function(data) {
                console.log('Saved worksheet ' + this.info.uuid);
                props.success(data);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    return WorksheetContent;
}();
