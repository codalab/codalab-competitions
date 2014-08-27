// 'class' to manage a worksheet and it's items.
// gets created in worksheet/details.html
var WorksheetContent =  function() {
    //init
    function WorksheetContent(url) {
        this.url = url;
        this.state= {
            last_item_id: 0,
            name: '',
            owner: null,
            owner_id: 0,
            uuid: 0,
            items: [ ]
        };
    }
    //add functions and calls below
    WorksheetContent.prototype.fetch = function(props) {
        props = props || {};
        props.success = props.success || function(data){};
        props.error = props.error || function(xhr, status, err){};

        $.ajax({
            type: "GET",
            url: this.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("setting worksheet state");
                console.log(data);
                console.log('');
                this.state = data;
                props.success(data);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };
    return WorksheetContent;
}();