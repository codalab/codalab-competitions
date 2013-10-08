/// <reference path="../../lib/jq/jquery.d.ts" />
/// <reference path="./AjaxRequest.ts" />
module Competition {

    export class Participants extends Ajax.AjaxRequest {
        saveParticipantStatus(obj) {
            if ($(obj).parent().hasClass("disabledStatus")) { return false; }
            var operationValue;
            var userId;
            var reason = "";
            $(obj).parent().siblings(".buttonPreloader").show();
            $(obj).parent().addClass('disabledStatus');
            if ($(obj).hasClass("approve")) {
                operationValue = 'approved';
                userId = $(obj).attr("id").replace("A", "");
            } else {
                operationValue = 'denied';
                userId = $(obj).attr("id").replace("R", "");
                reason = $("#reason").val();
            }
            var data = { "operation": operationValue, "participantId": parseInt($.trim(userId)), "reason": reason };
            var xUrl = "/api/competition/" + $("#competitionID").val() + '/userstatus/';
            var onSuccess = function (data) {
                    if (data.status == 'approved') {
                        $(obj).parent().siblings("p").text("Participation approved");
                        $(obj).parent().hide();
                        $(obj).parent().siblings(".buttonPreloader").hide();
                    } else if (data.status == 'denied') {
                        $(obj).parent().siblings("p").text("Participation Denied");
                        $(obj).parent().parent().append("<p style='color:red'>Reason: " + data.reason + "<p>");
                        $(obj).parent().hide();
                        $(obj).parent().siblings(".buttonPreloader").hide();
                    } else {
			alert("WTF?");
                    };
                };
               var onError = function (xhr, status, err) {
                    $(obj).parent().removeClass("disabledStatus");
                    $(obj).parent().siblings(".buttonPreloader").hide();
               }
               super.ajaxJSONRequest(xUrl, onSuccess, onError, data);
           
        } 
    showDialog(obj, message:string) {
        $(".popupContainer,.grayOverlaper").show();
        $(".popupBlock h1").text(message);
        $("#reason").val("");
        $(".cancel").click(function () { Participants.prototype.hideDialog(); });
        $("#btnOk").click(function () {
            Participants.prototype.hideDialog();
            Participants.prototype.saveParticipantStatus(obj)
        });
    }

    private hideDialog()  { $(".popupContainer,.grayOverlaper").hide(); }
    }
}

$(function () {
    var Participants = new Competition.Participants();
    $("li.active").removeClass("active");
    $("#liMycodeLab").addClass("active");
    $(".buttonAccept").click(function () { Participants.saveParticipantStatus(this) });
    $(".buttonReject").click(function () { Participants.showDialog(this, "Rejection reason") });
});
