var __extends = this.__extends || function (d, b) {
    function __() { this.constructor = d; }
    __.prototype = b.prototype;
    d.prototype = new __();
}
var Competition;
(function (Competition) {
    var Participants = (function (_super) {
        __extends(Participants, _super);
        function Participants() {
            _super.apply(this, arguments);

        }
        Participants.prototype.saveParticipantStatus = function (obj) {
            if($(obj).parent().hasClass("disabledStatus")) {
                return false;
            }
            var operationValue;
            var userId;
            var reason = "";
            $(obj).parent().siblings(".buttonPreloader").show();
            $(obj).parent().addClass('disabledStatus');
            if($(obj).hasClass("approve")) {
                operationValue = 0;
                userId = $(obj).attr("id").replace("A", "");
            } else {
                operationValue = 1;
                userId = $(obj).attr("id").replace("R", "");
                reason = $("#reason").val();
            }
            var data = {
                "operation": operationValue,
                "participantId": parseInt($.trim(userId)),
                "reason": reason
            };
            var xUrl = "/api/competitionparticipantstatus/" + $("#competitionID").val();
            var onSuccess = function (data) {
                if(data.status == 2) {
                    $(obj).parent().siblings("p").text("Participation approved");
                    $(obj).parent().hide();
                    $(obj).parent().siblings(".buttonPreloader").hide();
                } else {
                    if(data.status == 3) {
                        $(obj).parent().siblings("p").text("Participation rejected");
                        $(obj).parent().parent().append("<p style='color:red'>Reason: " + data.reason + "<p>");
                        $(obj).parent().hide();
                        $(obj).parent().siblings(".buttonPreloader").hide();
                    } else {
                    }
                }
                ; ;
            };
            var onError = function (xhr, status, err) {
                $(obj).parent().removeClass("disabledStatus");
                $(obj).parent().siblings(".buttonPreloader").hide();
            };
            _super.prototype.ajaxJSONRequest.call(this, xUrl, onSuccess, onError, data);
        };
        Participants.prototype.showDialog = function (obj, message) {
            $(".popupContainer,.grayOverlaper").show();
            $(".popupBlock h1").text(message);
            $("#reason").val("");
            $(".cancel").click(function () {
                Participants.prototype.hideDialog();
            });
            $("#btnOk").click(function () {
                Participants.prototype.hideDialog();
                Participants.prototype.saveParticipantStatus(obj);
            });
        };
        Participants.prototype.hideDialog = function () {
            $(".popupContainer,.grayOverlaper").hide();
        };
        return Participants;
    })(Ajax.AjaxRequest);
    Competition.Participants = Participants;    
})(Competition || (Competition = {}));

$(function () {
    var Participants = new Competition.Participants();
    $("li.active").removeClass("active");
    $("#liMycodeLab").addClass("active");
    $(".buttonAccept").click(function () {
        Participants.saveParticipantStatus(this);
    });
    $(".buttonReject").click(function () {
        Participants.showDialog(this, "Rejection reason");
    });
});
