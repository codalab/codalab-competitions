/*
CodaLab action bar (web terminal).
*/

(function() {

    var WorksheetActions = function(){};

    WorksheetActions.prototype.execute = function(command) { // is a promise must resolve and return a promise
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
            }),
            success: function(data, status, jqXHR) {
                result = {};

                if (data.data.exception){
                    console.error(data.data.exception);
                    deferred.reject(data.data.exception);
                    return;
                }

                if (data.data.stdout) {
                    result.stdout = data.data.stdout;

                    // Patch in hyperlinks to bundles
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
                    var err = data.data.stderr.replace(/\n/g, "<br>&emsp;"); // new line and a tab in
                    // 200 is ok response, this is a false flag due to how output is getting defined.
                    if (err.indexOf("200") === -1) { //-1 is not found
                        deferred.reject(err);
                        return;
                    }
                }

                // The bundle service can respond with instructions back to the UI.
                // These come in the form of an array of 2-arrays, with the first element
                // representing the type of action, and the second element parameterizing
                // that action.
                //
                // Possible actions:
                // ['openWorksheet', WORKSHEET_UUID]   - load worksheet
                // ['setEditMode', true|false]         - set edit mode
                // ['openBundle', BUNDLE_UUID]         - load bundle info in new tab
                // ['upload', null]                    - open upload modal
                if (data.data.structured_result && data.data.structured_result.ui_actions) {
                    result.ui_actions = data.data.structured_result.ui_actions;
                }

                deferred.resolve(result);
            },
            error: function(jqHXR, status, error){
                deferred.reject(error);
            }
        });
        return deferred.promise();
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
