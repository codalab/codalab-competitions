/// <reference path="../../lib/jq/jquery.d.ts" />
module Ajax {
    export class AjaxRequest {
        public ajaxJSONRequest(xUrl:string, succ, err, data) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: succ,
                error: err
            });
        } 

        public ajaxJSONRequestGeneral(xUrl: string, succ, err,type, data) {
            $.ajax({
                type: type,
                url: xUrl,
                cache: false,
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: succ,
                error: err
            });
        }

        public ajaxPostRequest(xUrl: string, succ, err) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                success: succ,
                error: err
            });
        }

        public ajaxGeneralRequest(xUrl: string, succ, err, type: string) {
            $.ajax({
                type: type,
                url: xUrl,
                cache: false,
                success: succ,
                error: err
            });
        }

        public ajaxGetRequest(xUrl:string, succ, err, data) {
            $.ajax({
                type: "GET",
                url: xUrl,
                data: data,
                cache: false,
                success: succ,
                error: err
            });
        }

        public ajaxFileUploadRequest(xUrl: string, succ, err, data) {
            $.ajax({
                type: "POST",
                url: xUrl,
                cache: false,
                processData: false,
                contentType: false,
                data:data,
                success: succ,
                error: err
            });
        }
    }
}