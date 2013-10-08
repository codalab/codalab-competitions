/// <reference path="../../lib/jq/jquery.d.ts" />
/// <reference path="./AjaxRequest.ts" />
declare var Urls: any;
module FileUpload {
    export class FileUploadFile extends Ajax.AjaxRequest {
        static timerId = 0;
        static rg1 = /^[^\\:\*\?"<>\|\%]+$/; // forbidden characters \ : * ? " < > |
        static rg2 = /^\./; // cannot start with dot (.)
        static rg3 = /^(nul|prn|con|lpt[0-9]|com[0-9])(\.|$)/i; // forbidden file names
        static staticCallback;
        static phaseValue = 1;
        private isValidFileName(fname) {
            return FileUploadFile.rg1.test(fname) && !FileUploadFile.rg2.test(fname) && !FileUploadFile.rg3.test(fname);
        }

        private canUploadFile() {
            var filedata;
            try {
                filedata = new FormData();
                return filedata !== undefined;
            }
            catch (e) { return filedata }
        }

        public uploadFile(reason: number, callBack) {
            FileUpload.FileUploadFile.staticCallback = callBack;
            var fileName = $("#uploadFile").val();
            if (FileUploadFile.prototype.canUploadFile() === undefined) {
                alert("Your current version of the browser is not supporting file upload functionality");
            } else {
                if (fileName !== "") {
                    if (FileUploadFile.prototype.validateFileExtension(fileName, ((reason == 1) ? true : false)) === false) {
                        alert("Please use the images for file upload");
                        $("#uploadFile").focus();
                        $("#uploadFile").val("");
                        return false;
                    }
                    var file = (<HTMLInputElement>$("#uploadFile")[0]).files[0];
                    if (file.size <= 4 * 1024 * 1024) {
                        if (reason !== 3) {
                            $("#imageProcess").css("display", "inline-block");
                        } else {
                            if (FileUpload.FileUploadFile.phaseValue === 1) {
                                $("#imageProcessph1").css("display", "inline-block");
                            }
                            else {
                                $("#imageProcessph2").css("display", "inline-block");
                            }
                        }
                        FileUploadFile.prototype.getFilToken(reason);
                    }
                    else {
                        alert("maximum file size of 4MB exceeded");
                        $("#uploadFile").focus();
                        $("#uploadFile").val("");
                    }
                }
            }
        }

        private uploadFileWithToken(token: number, reason: number) {
            var file = (<HTMLInputElement> $("#uploadFile")[0]).files[0];
            var filedata = new FormData();
            if (filedata !== undefined) {
                filedata.append("file", file);
                filedata.append("token", token);
                filedata.append("competitionId", parseInt($("#CompetitionId").val()));
                if (reason === 3) {
                    filedata.append("phaseNumber", FileUpload.FileUploadFile.phaseValue);
                }
                var onSuccess = function (data) {
                    FileUpload.FileUploadFile.timerId = setInterval("FileUpload.FileUploadFile.prototype.getFileStatus(" + token + "," + reason + ")", 3000);
                };
                var onError = function (xhr, status, err) {
                    clearInterval(FileUpload.FileUploadFile.timerId);
                    $("#imageProcess").hide();
                    $(".preloaderInputImg").hide();
                };
                super.ajaxFileUploadRequest("/FileUpload/Submit/", onSuccess, onError, filedata)
            }
        }

        private getFilToken(reason: number) {
            var data = { "reason": reason };
            $.ajax({
                url: "/FileUpload/Begin",
                type: "post",
                cache: false,
                data: data,
                success: function (data) {
                    FileUploadFile.prototype.uploadFileWithToken(data, reason)
                },
                error: function (xhr, status, err) {
                    clearInterval(FileUpload.FileUploadFile.timerId);
                    $("#imageProcess").hide();
                    $(".preloaderInputImg").hide()
                }
            });
        }

        private getFileStatus(token: number, reason: number ) {
            $("#resultStatus").hide();
            var data = { "id": token };
            $.ajax({
                url: "/FileUpload/Status",
                type: "post",
                cache: false,
                data: data,
                success: function (data) {
                    if (FileUpload.FileUploadFile.timerId < 10000) {
                        if (data.status == 8) {
                            if (reason === 1) {
                                FileUpload.FileUploadFile.staticCallback(token);
                            }
                            else {
                             //Competition.CompetitionDetails.prototype.requestPartialViewcontroller(10);
                                FileUpload.FileUploadFile.staticCallback(data);
                            }
                            $("#imageProcess").css("display", "none");
                            clearInterval(FileUpload.FileUploadFile.timerId);
                            $(".preloaderInputImg").hide()
                            //  $("#resultStatus").text(data.message);
                            $("#uploadFile").replaceWith($("#uploadFile").clone(true));
                        }
                        else if (data.status == 9) {
                            $("#resultStatus").show();
                            $("#resultStatus").text(data.message);
                            $("#imageProcess").css("display", "none");
                            $(".preloaderInputImg").hide()
                            if (reason === 3) {
                                if (FileUpload.FileUploadFile.phaseValue === 1) {
                                    $("#errorLabelPh1").css("display", "inline-block");
                                    $("#errorLabelPh1").text("");
                                    $("#errorLabelPh1").text(data.message)
                                } else {
                                    $("#errorLabelPh2").text("");
                                    $("#errorLabelPh2").css("display", "inline-block");
                                    $("#errorLabelPh2").text(data.message)
                                }
                            }
                            clearInterval(FileUpload.FileUploadFile.timerId);
                            $("#uploadFile").replaceWith($("#uploadFile").clone(true));
                        }
                    }
                    else {
                        $("#imageProcess").css("display", "none");
                        $(".preloaderInputImg").hide()
                        clearInterval(FileUpload.FileUploadFile.timerId);
                        $("#uploadFile").replaceWith($("#uploadFile").clone(true));
                    }
                },
                error: function (xhr, status, err) {
                    clearInterval(FileUpload.FileUploadFile.timerId);
                    $("#imageProcess").hide();
                    $(".preloaderInputImg").hide()
                    $("#resultStatus").text(err);
                    $("#uploadFile").replaceWith($("#uploadFile").clone(true));
                }
            });
        }

        private validateFileExtension(fileName: string, requiredValidation: bool) {
            if (requiredValidation === true) {
                var ext = fileName.split('.').pop().toLowerCase();
                return ($.inArray(ext, ['gif', 'png', 'jpg', 'jpeg', 'bmp']) != -1);
            } else { return true; }
        }

    }
}
