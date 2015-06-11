// 'class' to manage a bundle details for side panel.
// gets created in worksheet/details.html
var BundleContent = function() {
    //init
    function BundleContent() {
        this.url = null;
        this.current_uuid = null;
        this.state = {
            name: '',
        };
    }
    //add functions and calls below
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
                console.log("BundleContent: setting bundle details state:");
                // console.log(data);
                // console.log('');
                this.state = data;
                console.log(data.uuid);
                console.log(this.current_uuid);
                props.success(this.state);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };


    return BundleContent;
}();