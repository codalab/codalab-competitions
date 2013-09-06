var Competition;
(function (Competition) {

    Competition.invokePhaseButtonOnOpen = function (id) {
        var btn = $("#" + id + " .button.selected")[0];
        if (btn === undefined) {
            btn = $("#" + id + " .button.active")[0];
            if (btn === undefined) {
                btn = $("#" + id + " .button")[0];
            }
        }
        btn.click();
    }

    Competition.loadTabContent = function () {
        var name = $.trim(window.location.hash).toLowerCase();
        if (name == "#results") { $('#Results').click(); }
        if (name == "#participate-submit_results") { $('#Participate').click(); }
    }

    function addToLeaderboard(competition, submission, cstoken) {
        var result = 0;
        url = "/api/competition/" + competition + "/submission/" + submission + "/leaderboard";
        request = $.ajax({
            url: url,
            type: 'post',
            datatype: 'text',
            data: {
                'csrfmiddlewaretoken': cstoken,
            },
            success: function (response, textStatus, jqXHR) {
                btn.addClass("leaderBoardRemove");
                btn.text("Remove from Leaderboard");

            },
            error: function (jsXHR, textStatus, errorThrown) {
            },
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", cstoken);
            }
        });
    };

    function removeFromLeaderboard(competition, submission, cstoken) {
        var result = 0;
        url = "/api/competition/" + competition + "/submission/" + submission + "/leaderboard";
        request = $.ajax({
            url: url,
            type: 'delete',
            datatype: 'text',
            data: {
                'csrfmiddlewaretoken': cstoken,
            },
            success: function (response, textStatus, jqXHR) {
            },
            error: function (jsXHR, textStatus, errorThrown) {
            },
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", cstoken);
            }
        });
    };

    Competition.getPhaseSubmissions = function (competitionId, phaseId, cstoken) {
        $(".competition_submissions").html("").append("<div class='competitionPreloader'></div>").children().css({ 'top': '200px', 'display': 'block' });
        var url = "/competitions/" + competitionId + "/submissions/" + phaseId;
        $.ajax({
            type: "GET",
            url: url,
            cache: false,
            success: function (data) {
                $(".competition_submissions").html("").append(data);

                $('#fileUploadButton').on('click', function () {
                    var disabled = $('#fileUploadButton').hasClass('disabled');
                    if (!disabled) {
                        $('#details').html("");
                        $('#fileUpload').click();
                    }
                });
                $('#fileUpload').liteUploader(
                {
                    script: '/api/competition/' + competitionId + '/submission',
                    allowedFileTypes: 'application/zip,application/x-zip-compressed',
                    maxSizeInBytes: 104857600,
                    csrfmiddlewaretoken: cstoken,
                    customParams: {
                        'csrfmiddlewaretoken': cstoken
                    },
                    before: function () {
                        $('#fileUploadButton').addClass('disabled');
                        $('#fileUploadButton').text("Submitting...");
                        return true;
                    },
                    each: function (file, errors) {
                        if (errors.length > 0) {
                            $('#details').html('The selected file is not a valid ZIP file under 100MB.');
                        }
                    },
                    success: function (response) {
                        $("#user_results tr.noData").remove();
                        $("#user_results").append(Competition.displayNewSubmission(response));
                        $('#user_results #' + response.id + ' .enclosed-foundicon-plus').on("click", function () { Competition.showOrHideSubmissionDetails(this) });
                        $('#fileUploadButton').removeClass("disabled");
                        $('#fileUploadButton').text("Submit Results");
                        $('#user_results #' + response.id + ' .enclosed-foundicon-plus').click();
                    },
                    fail: function (jqXHR) {
                        var msg = "An unexpected error occured.";
                        if (jqXHR.status == 403) {
                            msg = jqXHR.responseJSON.detail;
                        }
                        $('#details').html(msg);
                        $('#fileUploadButton').text("Submit Results");
                        $('#fileUploadButton').removeClass('disabled');
                    }
                });

                $('#user_results .enclosed-foundicon-plus').on('click', function () {
                    Competition.showOrHideSubmissionDetails(this);
                });
            },
            error: function (xhr, status, err) {
                $(".competition_submissions").html("<div class='alert-error'>An error occurred. Please try refreshing the page.</div>");
            }
        });
    }

    Competition.getPhaseResults = function (competitionId, phaseId) {
        $(".competition_results").html("").append("<div class='competitionPreloader'></div>").children().css({ 'top': '200px', 'display': 'block' });
        var url = "/competitions/" + competitionId + "/results/" + phaseId;
        $.ajax({
            type: "GET",
            url: url,
            cache: false,
            success: function (data) {
                $(".competition_results").html("").append(data);
            },
            error: function (xhr, status, err) {
                $(".competition_results").html("<div class='alert-error'>An error occurred. Please try refreshing the page.</div>");
            }
        });
    }

    Competition.registationCanProceed = function () {
        if ($("#checkbox").is(":checked") === true) {
            $("#participateButton").removeClass("disabledStatus");
        } else {
            $("#participateButton").addClass("disabledStatus");
        };
    };

    Competition.displayRegistrationStatus = function () {
        var sOut = "";
        sOut = "<div class='participateInfoBlock pendingApproval'>"
        sOut += "<div class='infoStatusBar'></div>"
        sOut += "<div class='labelArea'>"
        sOut += "<label class='regApprovLabel'>Your request to participate in this challenge has been received and a decision is pending.</label>"
        sOut += "<label></label>"
        sOut += "</div>"
        sOut += "</div>"
        return sOut;
    }

    function fmt2(val) {
        var s = val.toString();
        if (s.length == 1) {
            s = "0" + s;
        }
        return s;
    }
    function lastModifiedLabel(dtString) {
        var d;
        if ($.browser.msie && (parseInt($.browser.version) === 8)) {
            d = new Date();
            var dd = parseInt(dtString.substring(8, 10), 10);
            var mm = parseInt(dtString.substring(5, 7), 10);
            var yr = parseInt(dtString.substring(0, 4), 10);
            var hh = parseInt(dtString.substring(11, 13), 10);
            var mn = parseInt(dtString.substring(14, 16), 10);
            var sc = parseInt(dtString.substring(17, 19), 10);
            d.setUTCDate(dd);
            d.setUTCMonth(mm);
            d.setUTCFullYear(yr);
            d.setUTCHours(hh);
            d.setUTCMinutes(mn);
            d.setUTCSeconds(sc);
        } else {
            d = new Date(dtString);
        }
        var dstr = $.datepicker.formatDate('M dd, yy', d).toString();
        var hstr = d.getHours().toString();
        var mstr = fmt2(d.getMinutes());
        var sstr = fmt2(d.getSeconds());
        return "Last modified: " + dstr + " at " + hstr + ":" + mstr + ":" + sstr;
    }

    Competition.displayNewSubmission = function (response) {
        var elemTr = $("#submission_details_template #submission_row_template tr").clone();
        $(elemTr).attr("id", response.id.toString());
        $(elemTr).addClass(Competition.oddOrEven(response.submission_number));
        $(elemTr).children().each(function (index) {
            switch (index) {
                case 0: if (response.status === 6) { $(this).val("1"); } break;
                case 1: $(this).html(response.submission_number.toString()); break;
                case 2:
                    var fmt = function (val) {
                        var s = val.toString();
                        if (s.length == 1) {
                            s = "0" + s;
                        }
                        return s;
                    }
                    var dt = new Date(response.submitted_at);
                    var d = $.datepicker.formatDate('mm/dd/yy', dt).toString();
                    var h = dt.getHours().toString();
                    var m = fmt(dt.getMinutes());
                    var s = fmt(dt.getSeconds());
                    $(this).html(d + " " + h + ":" + m + ":" + s);
                    break;
                case 3: $(this).html(Competition.getSubmissionStatus(response.status)); break;
            }
        }
      );
        return elemTr;
    }

    Competition.oddOrEven = function (x) {
        return (x & 1) ? "odd" : "even";
    }

    Competition.getSubmissionStatus = function (status) {
        var subStatus = "Unknown";
        switch (status) {
            case 1: subStatus = "Submitting"; break;
            case 2: subStatus = "Submitted"; break;
            case 3: subStatus = "Running"; break;
            case 4: subStatus = "Failed"; break;
            case 5: subStatus = "Cancelled"; break;
            case 6: subStatus = "Finished"; break;
        }
        return subStatus;
    }

    Competition.showOrHideSubmissionDetails = function (obj) {
        var nTr = $(obj).parents('tr')[0];
        if ($(obj).hasClass("enclosed-foundicon-minus")) {
            $(obj).removeClass("enclosed-foundicon-minus");
            $(obj).addClass("enclosed-foundicon-plus");
            $(nTr).next("tr.trDetails").remove();
        }
        else {
            $(obj).removeClass("enclosed-foundicon-plus");
            $(obj).addClass("enclosed-foundicon-minus");
            var elem = $("#submission_details_template .trDetails").clone();
            elem.find("a").each(function (i) { $(this).attr("href", $(this).attr("href").replace("_", nTr.id)) });
            var phasestate = $('#phasestate').val();
            var state = $(nTr).find("input[name='state']").val();
            if ((phasestate == 1) && (state == 1)) {
                var btn = elem.find("button");
                btn.removeClass("hide");
                var submitted = $(nTr).find(".status").hasClass("submitted");
                var competition = $("#competitionId").val();
                if (submitted) {
                    btn.addClass("leaderBoardRemove");
                    btn.text("Remove from Leaderboard");
                    btn.on('click', function () {
                        removeFromLeaderboard(competition, nTr.id, cstoken);
                    });
                } else {
                    btn.addClass("leaderBoardSubmit");
                    btn.text("Submit to Leaderboard");
                    btn.on('click', function () {
                        addToLeaderboard(competition, nTr.id, cstoken);
                    });
                }
            }
            else {
                var status = $(nTr).find(".statusName").html();
                var btn = elem.find("button").addClass("hide");
                if ($.trim(status) === "Submitting" || $.trim(status) === "Submitted" || $.trim(status) === "Running") {
                    btn.removeClass("hide");
                    btn.text("Refresh status")
                    btn.on('click', function () {
                        Competition.updateSubmissionStatus($("#competitionId").val(), nTr.id, this)
                    });
                }
            }
            $(nTr).after(elem);
        }
    }

    Competition.updateSubmissionStatus = function (competitionId, submissionId, obj) {
        $(obj).parents(".submission_details").find(".preloader-handler").append("<div class='competitionPreloader'></div>").children().css({ 'top': '25px', 'display': 'block' });
        var url = "/api/competition/" + competitionId + "/submission/" + submissionId;
        $.ajax({
            type: "GET",
            url: url,
            cache: false,
            success: function (data) {
                $('#user_results #' + submissionId).find(".statusName").html(Competition.getSubmissionStatus(data.status));
                if (data.status === 6) {
                    $('#user_results #' + submissionId + "input:hidden").val("1");
                    var phasestate = $('#phasestate').val();
                    if (phasestate == 1) {
                        $(obj).addClass("leaderBoardSubmit");
                        $(obj).text("Submit to Leaderboard");
                    } else {
                        $(obj).addClass("hide");
                    }
                }
                else if (data.status > 3) {
                    $(obj).addClass("hide");
                }
                $(".competitionPreloader").hide();
            },
            error: function (xhr, status, err) {

            }
        });
    }

})(Competition || (Competition = {}));
var prTable;
$(document).ready(function () {

    $("#checkbox").click(function (e) { Competition.registationCanProceed(); });

    $("#participate_form").submit(function (event) {
        event.preventDefault();
        if ($("#participateButton").hasClass("disabledStatus")) {
            return false;
        }
        $("#result").html('');
        var values = $(this).serialize();
        var competitionId = $("#competitionId").val();
        request = $.ajax({
            url: "/api/competition/" + competitionId + "/participate/",
            type: "post",
            dataType: "text",
            data: values,
            success: function (response, textStatus, jqXHR) {
                $('.content form').replaceWith(Competition.displayRegistrationStatus());
            },
            error: function (jsXHR, textStatus, errorThrown) {
                alert("There was a problem registering for this competition.");;
            }
        });
        return false;
    });

    $("#submissions_phase_buttons .button").each(function (e, index) {
        $(this).click(function () {
            var phaseId = $.trim($(this).attr("id").replace("submissions_phase_", ""));
            $("#submissions_phase_buttons .button").removeClass('selected');
            $(this).addClass('selected');
            var competitionId = $("#competitionId").val();
            var cstoken = $("#cstoken").val();
            Competition.getPhaseSubmissions(competitionId, phaseId, cstoken);
        });
    });

    $('a[href="#participate-submit_results"]').click(function (obj) {
        Competition.invokePhaseButtonOnOpen("submissions_phase_buttons");
    });

    $("#results_phase_buttons .button").each(function (e, index) {
        $(this).click(function () {
            var phaseId = $.trim($(this).attr("id").replace("results_phase_", ""));
            $("#results_phase_buttons .button").removeClass('selected');
            $(this).addClass('selected');
            var competitionId = $("#competitionId").val();
            Competition.getPhaseResults(competitionId, phaseId);
        });
    });

    $('#Results').click(function (obj) {
        Competition.invokePhaseButtonOnOpen("results_phase_buttons");
    });

    // This helps make sections appear with Foundation
    $(this).foundation('section', 'reflow');
    Competition.loadTabContent();

    $(".top-bar-section ul > li").removeClass("active");
    $("#liCompetitions").addClass("active");
});
