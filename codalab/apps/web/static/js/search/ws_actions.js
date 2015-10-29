/*
CodaLab action bar (web terminal).
TODO: revamp this to make the interface more uniform and pass more control to the CLI.
*/

(function() {

    var WorksheetActions = function(){};

    WorksheetActions.prototype.execute = function(command) { // is a promise must resolve and return a promise
        var defer = jQuery.Deferred();

        $.ajax({
            type:'POST',
            cache: false,
            url:'/api/worksheets/command/',
            contentType:"application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'worksheet_uuid': ws_obj.state.uuid,
                'command': command,
            }),
            success: function(data, status, jqXHR) {
                // console.log('===== Output of command: ' + options);
                if (data.data.exception){
                    console.error(data.data.exception);
                    defer.reject(data.data.exception);
                }
                if (data.data.stdout) {
                    // console.log(data.data.stdout);
                    defer.resolve(data.data.stdout);
                    if (data.data.structured_result && data.data.structured_result.refs) {
                        var references = data.data.structured_result['refs'];
                        Object.keys(references).forEach(function(k) {
                            $(".terminal-output div div:contains(" + k + ")").html(function(idx, html) {
                                var hyperlink_info = references[k];
                                if (hyperlink_info.uuid) {
                                    if (hyperlink_info.type === 'bundle' || hyperlink_info.type === 'worksheet') {
                                        var link = '/' + hyperlink_info['type'] + 's/' + hyperlink_info['uuid'];
                                        return html.replace(k, "<a href=" + link + " target='_blank'>" + k + "</a>");
                                    }
                                    else {
                                        console.warn("Couldn't create hyperlink for", hyperlink_info.uuid, ". Type is neither 'worksheet' nor 'bundle'");
                                    }
                                }
                                else {
                                    console.warn("Complete uuid not available for", k, "to create hyperlink");
                                }
                            }, this);
                        }, this);
                    }
                }
                if (data.data.stderr) {
                    //console.log(data.data.stderr);
                    var err;
                    err = data.data.stderr.replace(/\n/g, "<br>&emsp;"); // new line and a tab in
                    // 200 is ok response, this is a false flag due to how output is getting defined.
                    if (err.indexOf("200") === -1) { //-1 is not found
                        defer.reject(err);
                        return;
                    }

                }
                if (data.data.structured_result) {

                }
                // console.log('=====');
                defer.resolve();
            },
            error: function(jqHXR, status, error){
                defer.reject(error);
            }
        });
        return defer.promise();
    };

    WorksheetActions.prototype.completeCommand = function(command) {
        var deferred = jQuery.Deferred();
        $.ajax({
            type:'POST',
            cache: false,
            url:'/api/worksheets/command/',
            contentType:"application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify({
                'worksheet_uuid': ws_obj.state.uuid,
                'command': command,
                'autocomplete': true,
            }),
            success: function(data, status, jqXHR) {
                deferred.resolve(data.completions);
            },
            error: function(jqHXR, status, error) {
                console.error(error);
                deferred.reject();
            }
        });
        return deferred.promise();
    };

    window.WorksheetActions = WorksheetActions;
})();
