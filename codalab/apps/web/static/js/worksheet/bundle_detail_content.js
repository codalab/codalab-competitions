/*
Information about the current bundle that's selected in the side panel.
*/
var BundleContent = function() {
    function BundleContent() {
        this.url = null;
        this.current_uuid = null;
        this.state = {
            name: '',
        };
    }

    BundleContent.prototype.fetch = function(props) {
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};

        $.ajax({
            type: "GET",
            url: "/api/bundles/" + this.current_uuid,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.state = data;
                props.success(this.state);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };

    return BundleContent;
}();
