// 'class' to manage a worksheet and its items.
// gets created in worksheet/details.html
var WorksheetContent = function() {
    //init
    function WorksheetContent(url) {
        this.url = url;
        this.state = {
            last_item_id: 0,
            name: '',
            owner: null,
            owner_id: 0,
            uuid: 0,
            items: [ ]
        };
        this.consolidateMarkdownBundles = function(ws) {
            var consolidatedWorksheet = [];
            var markdownChunk         = '';
            ws.items.map(function(item){
                var mode        = item['mode'];
                var interpreted = item['interpreted'];
                switch(mode) {
                    case 'markup':
                        var content = interpreted + '\n';
                        markdownChunk += content;
                        break;
                    default:
                        if(markdownChunk.length){
                            consolidatedWorksheet.push({
                                mode: 'markup',
                                interpreted: markdownChunk,
                                bundle_info: null
                            });
                            markdownChunk = '';
                        }
                        consolidatedWorksheet.push(item);
                        break;
                }
            });
            ws.items = consolidatedWorksheet;
            return ws;
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
                console.log("WorksheetContent: setting worksheet state:");
                console.log(data);
                console.log('');
                consolidatedWorksheet = this.consolidateMarkdownBundles(data);
                this.state = consolidatedWorksheet;
                props.success(consolidatedWorksheet);
            }.bind(this),
            error: function(xhr, status, err) {
                props.error(xhr, status, err);
            }.bind(this)
        });
    };
    return WorksheetContent;
}();