var Ajax;
(function (Ajax) {
    var AjaxRequest = (function () {
        function AjaxRequest() { }
        AjaxRequest.prototype.ajaxJSONRequest = function (xUrl, succ, err, data) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: succ,
                error: err
            });
        };
        AjaxRequest.prototype.ajaxJSONRequestGeneral = function (xUrl, succ, err, type, data) {
            $.ajax({
                type: type,
                url: xUrl,
                cache: false,
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: succ,
                error: err
            });
        };
        AjaxRequest.prototype.ajaxPostRequest = function (xUrl, succ, err) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                success: succ,
                error: err
            });
        };
        AjaxRequest.prototype.ajaxGeneralRequest = function (xUrl, succ, err, type) {
            $.ajax({
                type: type,
                url: xUrl,
                cache: false,
                success: succ,
                error: err
            });
        };
        AjaxRequest.prototype.ajaxGetRequest = function (xUrl, succ, err, data) {
            $.ajax({
                type: "GET",
                url: xUrl,
                data: data,
                cache: false,
                success: succ,
                error: err
            });
        };
        AjaxRequest.prototype.ajaxFileUploadRequest = function (xUrl, succ, err, data) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                processData: false,
                contentType: false,
                data: data,
                success: succ,
                error: err
            });
        };
        return AjaxRequest;
    })();
    Ajax.AjaxRequest = AjaxRequest;    
})(Ajax || (Ajax = {}));

