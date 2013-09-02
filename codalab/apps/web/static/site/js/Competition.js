
var Competition;
(function (Competition) {

    Competition.invokePhaseButtonOnOpen = function(id) {
        var btn = $("#" + id + " .button.selected")[0];
        if (btn === undefined) {
            btn = $("#" + id + " .button.active")[0];
            if (btn === undefined) {
                btn = $("#" + id + " .button")[0];
            }
        }
        btn.click();
    }

    Competition.loadTabContent = function() {
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

    Competition.getPhaseSubmissions = function(competitionId, phaseId, cstoken) {
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
                        //var subNumber = response.submission_number.toString();
                        //var subSubmitted = response.submitted_at;
                        //var subStatus = "Unknonw";
                        //switch (response.status) {
                        //    case 1: subStatus = "Submitted"; break;
                        //    case 6: subStatus = "Running"; break;
                        //    case 7: subStatus = "Failed"; break;
                        //    case 8: subStatus = "Cancelled"; break;
                        //    case 9: subStatus = "Finished"; break;
                        //}
                        //var x = $("#user_results").dataTable().fnAddData([subNumber, subSubmitted, subStatus, "", "", ""]);
                        //$('#fileUploadButton').text("Submit Results");
                        //$('#fileUploadButton').removeClass('disabled');
                        window.location.reload();
                    },
                    fail: function (jqXHR) {
                        $('#details').html("An error occurred (" + jqXHR.status + " - " + jqXHR.responseJSON.detail + ")");
                        $('#fileUploadButton').text("Submit Results");
                        $('#fileUploadButton').removeClass('disabled');
                    }
                });

                var prTable = $("#user_results").dataTable({
                    'bPaginate': false,
                    'bInfo': false,
                    'bFilter': false,
                    'bAutoWidth': false,
                    'bSort': false
                });
                /*
                var crTable = $("#competition_results").dataTable({
                    "fnDrawCallback": function (oSettings) {
                        // Need to redo the counters if filtered or sorted
                        if (oSettings.bSorted || oSettings.bFiltered) {
                            for (var i = 0, iLen = oSettings.aiDisplay.length ; i < iLen ; i++) {
                                $('td:eq(0)', oSettings.aoData[oSettings.aiDisplay[i]].nTr).html(i + 1);
                            }
                        }
                    },
                    "aoColumnDefs": [
                        { "bSortable": false, "aTargets": [0] }
                    ],
                    "aaSorting": [[1, 'asc']],
                    'bPaginate': false,
                    'bInfo': false,
                    'bFilter': false
                });
                */
                $('#user_results .enclosed-foundicon-plus').on('click', function () {
                    var nTr = $(this).parents('tr')[0];
                    if (prTable.fnIsOpen(nTr)) {
                        $(this).removeClass("enclosed-foundicon-minus");
                        $(this).addClass("enclosed-foundicon-plus");
                        prTable.fnClose(nTr);
                    }
                    else {
                        $(this).removeClass("enclosed-foundicon-plus");
                        $(this).addClass("enclosed-foundicon-minus");
                        var elem = $("#submission_details_template .submission_details").clone();
                        elem.find("a").each(function (i) { $(this).attr("href", $(this).attr("href").replace("_", nTr.id)) });
                        var state = $(nTr).find("input[name='state']").val();
                        if (state == 1) {
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
                        prTable.fnOpen(nTr, elem, 'details');
                    }
                });
            },
            error: function (xhr, status, err) {
                $(".competition_submissions").html("<div class='alert-error'>An error occurred. Please try refreshing the page.</div>");
            }
        });
    }

    Competition.getPhaseResults = function(competitionId, phaseId) {
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

    Competition.registationCanProceed = function() {
        if ($("#checkbox").is(":checked") === true) {
            $("#participateButton").removeClass("disabledStatus");
        } else {
            $("#participateButton").addClass("disabledStatus");
        };
    };

    Competition.displayRegistrationStatus = function() {
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

})(Competition || (Competition = {}));

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
                Competition.invokePhaseButtonOnOpen("submissions_phase_buttons");
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

    $('#Participate').click(function (obj) {
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
