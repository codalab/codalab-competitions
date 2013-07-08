/// <reference path="../../lib/jq/jquery.d.ts" />
/// <reference path="../../lib/jq/jqueryui.d.ts" />
/// <reference path="./FileUpload.ts" />
module Competition {
    export class CompetitionDetails extends FileUpload.FileUploadFile {
        static page = 0;
        static pageSubmission = 0;
        static loadSucess = false;
        static loadSucessSubmisstion = false;
        static currentMainTab;
        static currentSubTab;
        static timerId = 0;

        public requestPartialViewcontroller(pageId: number) {
            CompetitionDetails.prototype.hidePhaseToggleBtn();
            var competitionId = $("#CompetitionId").val();
            var url = "/competitions/details/" + competitionId + "/page/" + pageId;
            var onSuccess = function (data) {
                if ($(".competitionsDetailTabTop > li.active").hasClass("tab1")) {
                    $("#subContainerBlock").append(data);
                }
                else {
                    $("#subContainerBlockForParticipate").html("");
                    $("#subContainerBlockForParticipate").append(data);
                    if (pageId === 10) {
                        CompetitionDetails.pageSubmission = 0;
                        $("#resultSubmissionResults > tr").remove();
                        $("#selctedPhaseButton").val($("#activePhase").val());
                        CompetitionDetails.prototype.getSubmissionsPageResults($("#activePhase").val());
                        CompetitionDetails.prototype.togglePhases($("#activePhase").val())
                        $("#uploadFile").change(function () {
                            var onSuccess = function (dataA) {
                                CompetitionDetails.prototype.requestPartialViewcontroller(10)
                            };
                            CompetitionDetails.prototype.uploadFile(2, onSuccess);
                        });
                        $("#submitResults").click(function (e) {
                            $("#uploadFile").click();
                        });
                        CompetitionDetails.prototype.showPhaseToggleBtn();
                    }
                }
                $('.CompetitionsDetailLftUl > li').removeClass('active');
                $("#tab" + pageId).addClass("active");
                CompetitionDetails.prototype.hideProcess();
            };
            var onError = function (xhr, status, err) {
                CompetitionDetails.prototype.hideProcess();
            };
            super.ajaxGetRequest(url, onSuccess, onError, null);
        }

        requestPartialView(obj) {
            $(".preloader").show();
            $(".tabArea").hide();
            var id: string = $(obj).attr("id");
            var index = $.trim(id.replace("tab", ""))
            $(".CompetitionsDetailLft li").removeClass("active");
            $(obj).addClass("active");
            if ($('#' + id + "_" + index).length === 0) {
                CompetitionDetails.prototype.requestPartialViewcontroller(parseInt(index));
                if (parseInt(index) === 1) {
                    $("#statusBar").show();
                }
            } else {
                $('#' + id + "_" + index).show();
                if (parseInt(index) === 1) {
                    $("#statusBar").show();
                }
                CompetitionDetails.prototype.hideProcess();
            }
        }

        private hideProcess() { $(".preloader").hide(); }

        private hideDialog() { $(".popupContainer,.grayOverlaper").hide(); }

        public checkRegisterStatus() {
            $(".preloader").show();
            var xUrl = "/api/competitionparticipantstatus/" + $("#CompetitionId").val();
            var onSuccess = function (data) {
                CompetitionDetails.prototype.setRegisterButtonLabel(data.status, data.reason);
                CompetitionDetails.prototype.hideDialog();
                CompetitionDetails.prototype.hideProcess();
            };
            var onError = function (xhr, status, err) {
                CompetitionDetails.prototype.setRegisterButtonLabel(999, "");
                CompetitionDetails.prototype.hideDialog();
                CompetitionDetails.prototype.hideProcess();
            };
            super.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        public saveUserRegisterStatus() {
            var url = "/api/competitionparticipantstatus/" + $("#CompetitionId").val();
            var onSuccess = function (data) {
                CompetitionDetails.prototype.checkRegisterStatus();
            };
            var onError = function (xhr, status, err) {
                CompetitionDetails.prototype.hideDialog();
            };
            super.ajaxPostRequest(url, onSuccess, onError)
        }

        private setRegisterButtonLabel(status: number, reason: string) {
            CompetitionDetails.prototype.hideAllTabSections();
            switch (status) {
                case 0:
                    CompetitionDetails.prototype.showRegisterButton("register", "You have not yet registered for this competition");
                    CompetitionDetails.prototype.showRegisterSection();
                    break;
                case 1:
                    CompetitionDetails.prototype.showRegisterLabel("Your registration is pending approval");
                    $("#participateInfoBlock").addClass("pendingApproval");
                    break;
                case 2:
                    $("#participateInfoBlock").hide();
                    CompetitionDetails.prototype.showTabSections();
                    break;
                case 3:
                    CompetitionDetails.prototype.showRegisterLabel("Your registration has been rejected.");
                    $("#rejectionReasonLabel").show();
                    $("#rejectionReasonLabel").text(reason);
                    $("#participateInfoBlock").addClass("rejectedApproval");
                    break;
                default:
                    CompetitionDetails.prototype.showRegisterLabel("status not available");
                    break;
            }
        }

        private showRegisterButton(text: string, label: string) {
            $(".buttonPreloader").hide();
            $(".blueRegButton").show();
            $("#registerCompetition").text(text);
            $("#registerCompetitionLabel").text(label);
        }

        private showRegisterLabel(text: string) {
            $(".buttonPreloader").hide();
            $(".blueRegButton").hide();
            $("#registerCompetitionLabel").text(text);
            $("#registerCompetitionLabel").show();
        }

        public allowRegister() {
            if ($("#chkRegister").is(":checked") === true) {
                $("#registerCompetition").removeClass("disabledStatus");
            } else {
                $("#registerCompetition").addClass("disabledStatus");
            };
        }
        public getCompetitionResults(phaseValue) {
            $("#seeTheResults div.competitionTileNoRecord").remove();
            if (CompetitionDetails.page > -1) {
                $("#seeTheResults tr:first").show();
                $("<tr id='preLoaderRow'><td colspan='5'><div class='coloumPreloader'></div></td></tr>").insertAfter($("#seeTheResults tr:last"));
                var data = { "pageNumber": CompetitionDetails.page, "pageSize": 6 };
                CompetitionDetails.page++;
                var xUrl = "/Competitions/" + $("#CompetitionId").val() + "/results/" + phaseValue + "/" + parseInt($("#selectedRank").val());
                var onSuccess = function (data) {
                    if ($(data).text() !== "There are no results.") {
                        CompetitionDetails.loadSucess = true;
                        $("#seeTheResults").append(data);
                        $("#preLoaderRow").remove();
                        
                        if ($('body').outerHeight() < $(window).height()) { CompetitionDetails.prototype.getCompetitionResults(phaseValue); }
                        if ($("#seeTheResults tr.trHearder").length > 1) {
                            $("#seeTheResults tr:first").remove();
                        }

                        $(".trHearder").find(".rankHeader").each(function () {
                            $(this).click(function () {
                                CompetitionDetails.page = 0;
                                $("#selectedRank").val($(this).children("input:hidden").val());
                                $('#seeTheResults tr:gt(0)').remove();
                                CompetitionDetails.prototype.getCompetitionResults($("#selctedPhaseButton").val());
                            });
                        });
                    }
                    else {
                        if (CompetitionDetails.page === 1) {
                            if ((parseInt($("#activePhase").val()) > -1) && ((parseInt(phaseValue) === 0) || (parseInt(phaseValue) > parseInt($("#activePhase").val())))) { data = "<p> This phase has not started.</p>"; }
                            $("#seeTheResults").append("<div class=\"competitionTileNoRecord\">" + data + "</div>");
                            $("#seeTheResults tr:first").hide();
                        }
                        CompetitionDetails.page = -1;
                        $("#preLoaderRow").remove();

                    }

                };
                var onError = function (xhr, status, err) {
                    $("#preLoaderRow").remove();
                };
                super.ajaxJSONRequest(xUrl, onSuccess, onError, data);
            }
        }

        private showTabSections() {
            $("#tabParticipantContainer").show();
        }

        private showPhaseToggleBtn() {
            $("#phaseToggleBtnContainerSubmitPage").show();
        }
        private hidePhaseToggleBtn() {
            $("#phaseToggleBtnContainerSubmitPage").hide();
        }

        private hideAllTabSections() {
            $("#tabParticipantContainer").hide();
            $("#registerOptionContainer").hide();
            $("#rejectionReasonLabel").hide();
            CompetitionDetails.prototype.hidePhaseToggleBtn();
        }

        private showRegisterSection() {
            $("#registerOptionContainer").show();
        }

        public getLftTabsForCompetition(tabNumber: number) {
            $(".preloader").show();
            var xUrl = "/competitions/details/" + $("#CompetitionId").val() + "/tab/ " + tabNumber;
            var currentTabId;
            var onSuccess = function (data) {
                if (tabNumber === 0) {
                    $("#CompetitionsDetailLftLtd").html(""); $("#CompetitionsDetailLftLtd").append(data);
                    $('.CompetitionsDetailLftUl > li').removeClass('active');
                    $("#CompetitionsDetailLftLtd > li:first").addClass("active");
                    currentTabId = $("#CompetitionsDetailLftLtd > li:first").attr("id");
                }
                else {
                    $("#CompetitionsDetailLftParticipate").html(""); $("#CompetitionsDetailLftParticipate").append(data);
                    $('.CompetitionsDetailLftUl > li').removeClass('active');
                    $("#CompetitionsDetailLftParticipate > li:first").addClass("active");
                    currentTabId = $("#CompetitionsDetailLftParticipate > li:first").attr("id");
                }
                $('.CompetitionsDetailLftUl > li').click(function () {
                    var myClass = $(this).attr("class");
                    if (!$(this).hasClass('active')) {
                        $('.CompetitionsDetailLftUl > li').removeClass('active');
                        $(this).addClass('active');
                        CompetitionDetails.prototype.requestPartialView(this);
                        window.location.hash = $.trim($.trim($('.competitionsDetailTabTop > li.active').attr("class").replace("active", "")) + "-" + $(this).attr("id"));
                    }
                })
                CompetitionDetails.prototype.getTabSelectionIdentifiersFromURL();
                if (CompetitionDetails.currentSubTab) {
                    CompetitionDetails.prototype.requestPartialViewcontroller(parseInt($.trim(CompetitionDetails.currentSubTab.replace("tab", ""))));
                }
                else {
                    CompetitionDetails.prototype.requestPartialViewcontroller(parseInt($.trim(currentTabId.replace("tab", ""))));

                }

            };
            var onError = function (xhr, status, err) {

            };
            super.ajaxGetRequest(xUrl, onSuccess, onError, null)
        }

        public getSubmissionsPageResults(phaseValue) {
            $("#resultSubmissionResults div.competitionTileNoRecord").remove();
            if (CompetitionDetails.pageSubmission > -1) {
                $("#resultSubmissionResults tr:first").show();
                $("<tr id='preLoaderRow'><td colspan='4'><div class='coloumPreloader'></div></td></tr>").insertAfter($("#resultSubmissionResults tr:last"));
                var data = { "pageNumber": CompetitionDetails.pageSubmission, "pageSize": 6 };
                CompetitionDetails.pageSubmission++;
                var xUrl = "/Competitions/" + $("#CompetitionId").val() + "/submissions/" + phaseValue;
                var onSuccess = function (data) {
                    if ($(data).text() !== "There are no previous submissions.") {
                        CompetitionDetails.loadSucessSubmisstion = true;
                        $("#resultSubmissionResults").append(data);
                        $("#preLoaderRow").remove();
                        $(".toggleIconExp").unbind("click").click(function () {
                            $(this).parents('.toggleTble').next('div').toggleClass('preSubmissionToggleView preSubmissionToggle');
                            $(this).toggleClass('toggleIconColp toggleIconExp');
                        });
                        $(".leaderboardUpdate").click(function () {
                            var submissionVal = $(this).parents('.preSubmissionToggleView').siblings(".toggleTble").find("tr td:first").text();
                            CompetitionDetails.prototype.updateLeaderBoard(parseInt(submissionVal), this);
                        });
                        $(".leaderboardDelete").click(function () {
                            CompetitionDetails.prototype.deleteLeaderBoard(this);
                        });
                        $(".globalBlueButtonSmallFlexi").click(function () {
                            var submissionVal = $(this).parents('.preSubmissionToggleView').siblings(".toggleTble").find("tr td:first").text();
                            var type = $(this).attr("id");
                            CompetitionDetails.prototype.openSubStandardWindow(submissionVal, type)
                        })
                        if ($('body').outerHeight() < $(window).height()) { CompetitionDetails.prototype.getSubmissionsPageResults(phaseValue); }
                    }
                    else {
                        if (CompetitionDetails.pageSubmission === 1) {
                            $("#resultSubmissionResults").append("<div class=\"competitionTileNoRecord\">" + data + "</div>"); $("#resultSubmissionResults tr:first").hide()
                        }
                        CompetitionDetails.pageSubmission = -1;
                        $("#preLoaderRow").remove();
                    }
                    CompetitionDetails.prototype.getCurrentLederBoardDetails();
                };
                var onError = function (xhr, status, err) {
                    $("#preLoaderRow").remove();
                };
                super.ajaxJSONRequest(xUrl, onSuccess, onError, data);
            }
        }

        private openSubStandardWindow(submissionValue,type) {
            var selectedPhaseValue = $("#selctedPhaseButton").val();
            var competitionId = $("#CompetitionId").val();
            var URL = "" + "/" + competitionId + "/" + selectedPhaseValue + "/" + submissionValue + "/" + type;
            window.open(URL)
            //alert(URL);
        }

        private getCurrentLederBoardDetails() {
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/leaderboard/entry/" + $("#selctedPhaseButton").val() + "/submission/1";
            var onSuccess = function (data) {
                var currentTickElement = $(".resultSubResultsContainer").find("tr td:first:contains('" + (data.number) + "')").siblings("td.ticked").find("div");
                $(currentTickElement).removeClass("leaderboardHidden");
                $(currentTickElement).addClass("leaderboardVisible");
                $(currentTickElement).parents(".toggleTble").siblings(".preSubmissionToggle").find("a.leaderboardbuttonHidden").removeClass("leaderboardbuttonHidden")
                $(currentTickElement).parents(".toggleTble").siblings(".preSubmissionToggle").find("a.leaderboardUpdate").addClass("leaderboardbuttonHidden")
            };
            var onError = function (xhr, status, err) {
            };
            super.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        private updateLeaderBoard(submissionID: number, obj) {
            $(obj).addClass("disabledStatus");
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/leaderboard/entry/" + $("#selctedPhaseButton").val() + "/submission/" + submissionID;
            var filedata = new FormData();
            if (filedata !== undefined) {
                filedata.append("submissionId", 2);
            }
            var onSuccess = function (data) {
                $("a.leaderboardDelete").addClass("leaderboardbuttonHidden")
                $("a.leaderboardUpdate").removeClass("leaderboardbuttonHidden")
                $(".leaderboardVisible").addClass("leaderboardHidden");
                $(obj).siblings("a").removeClass("leaderboardbuttonHidden");
                $(obj).addClass("leaderboardbuttonHidden");
                var currentTickElement = $(obj).parents('.preSubmissionToggleView').siblings(".toggleTble").find("tr td.ticked div");
                $(currentTickElement).removeClass("leaderboardHidden");
                $(currentTickElement).addClass("leaderboardVisible");
                $(obj).removeClass("disabledStatus");

            };
            var onError = function (xhr, status, err) { $(obj).removeClass("disabledStatus"); };
            super.ajaxPostRequest(xUrl, onSuccess, onError);
        }

        private deleteLeaderBoard(obj) {
            $(obj).addClass("disabledStatus");
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/leaderboard/entry/" + $("#selctedPhaseButton").val() + "/submission/1/";
            var onSuccess = function (data) {
                $(".leaderboardVisible").addClass("leaderboardHidden");
                $(obj).siblings("a").removeClass("leaderboardbuttonHidden");
                $(obj).addClass("leaderboardbuttonHidden");
                var currentTickElement = $(obj).parents('.preSubmissionToggleView').siblings(".toggleTble").find("tr td.ticked div");
                $(currentTickElement).removeClass("leaderboardVisible");
                $(currentTickElement).addClass("leaderboardHidden");
                $(obj).removeClass("disabledStatus");
            };
            var onError = function (xhr, status, err) {
                $(obj).removeClass("disabledStatus");
            };
            super.ajaxGeneralRequest(xUrl, onSuccess, onError, "Delete");
        }

        public getAcivePhase() {
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/active-phase";
            var onSuccess = function (data) {
                $("#activePhase").val(data.active);
                $("#selctedPhaseButton").val(data.active);
                var strHtmlStrip = "";
                for (var v in data.phases.phases) {
                    strHtmlStrip = strHtmlStrip + "<section><label>" + data.phases.phases[v].label + "</br>";
                    strHtmlStrip = strHtmlStrip + "<span> begins " + $.datepicker.formatDate('mm/dd/yy', new Date(data.phases.phases[v].startDate)) + "</span></label></section>";
                }
                strHtmlStrip = strHtmlStrip + "<section><label> Competition </br>";
                if (data.phases.endDate !== undefined && data.phases.endDate !== null) {
                    strHtmlStrip = strHtmlStrip + "<span> ends " + $.datepicker.formatDate('mm/dd/yy', new Date(data.phases.endDate)) + "</span>";
                }
                else {
                    strHtmlStrip = strHtmlStrip + "<span> has no end </span>";
                }
                strHtmlStrip = strHtmlStrip + "</label></section>";

                $(".challStatusStripSection").append(strHtmlStrip);
                CompetitionDetails.prototype.showPhaseButtons(data);
                if (CompetitionDetails.currentMainTab === "tab3") {
                    CompetitionDetails.page = 0;
                    CompetitionDetails.prototype.getCompetitionResults($("#activePhase").val());
                }
            };
            var onError = function (xhr, status, err) {
            };
            super.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        private togglePhases(i: number) {
            var phaseToggleBtnContainerSubmitPage = $("#phaseToggleBtnContainerSubmitPage div");
            var phaseToggleBtnContainerResultpage = $("#phaseToggleBtnContainerResultpage div");
            $(phaseToggleBtnContainerSubmitPage).addClass("disabled");
            $(phaseToggleBtnContainerSubmitPage).addClass("disabledStatus");
            $(phaseToggleBtnContainerResultpage).addClass("disabledStatus");
            $("#phaseToggleBtnContainerSubmitPage div span").remove();
            $("#phaseToggleBtnContainerResultpage div span").remove();

            if (i > 0) {
                $(phaseToggleBtnContainerSubmitPage).eq(i - 1).removeClass("disabled");
                $(phaseToggleBtnContainerSubmitPage).eq(i - 1).removeClass("disabledStatus");
                $(phaseToggleBtnContainerSubmitPage).eq(i - 1).append("<span ></span>");
                $(phaseToggleBtnContainerResultpage).eq(i - 1).removeClass("disabled");
                $(phaseToggleBtnContainerResultpage).eq(i - 1).removeClass("disabledStatus");
                $(phaseToggleBtnContainerResultpage).eq(i - 1).append("<span ></span>");
            }
            else {
                $("#plblSubmission").text("This phase of the competition has not started.You cannot submit results at this time.");
                $("#submitResults").parent("div").hide();
                $(phaseToggleBtnContainerSubmitPage).eq(0).removeClass("disabled");
                $(phaseToggleBtnContainerSubmitPage).eq(0).removeClass("disabledStatus");
                $(phaseToggleBtnContainerResultpage).eq(0).removeClass("disabled");
                $(phaseToggleBtnContainerResultpage).eq(0).removeClass("disabledStatus");
            }
        }

        private showPhaseButtons(data) {
            $("#phaseToggleBtnContainerSubmitPage").html("");
            $("#phaseToggleBtnContainerResultpage").html("");
            var strHtmlSubmission = "";
            var strHtmlResult = "";
            for (var v in data.phases.phases) {
                strHtmlSubmission = strHtmlSubmission + "<div  class ='globalBlueButton phaseToggleBtn lFloat' id='submission" + v.toString() + "'><a>" + data.phases.phases[v].label + "</a></div>";
                strHtmlResult = strHtmlResult + "<div  class ='globalBlueButton phaseToggleBtn lFloat' id='result" + v.toString() + "'><a>" + data.phases.phases[v].label + "</a></div>";
            }
            $("#phaseToggleBtnContainerSubmitPage").append(strHtmlSubmission);
            $("#phaseToggleBtnContainerResultpage").append(strHtmlResult);
            var i = parseInt($("#activePhase").val());
            CompetitionDetails.prototype.togglePhases(i);
            $("#phaseToggleBtnContainerSubmitPage div").each(function () {
                $(this).click(function () {
                    if (parseInt($("#activePhase").val()) !== 0) {
                        if ($(this).hasClass("disabled")) {
                            $("#submitResults").parent("div").hide();
                        } else {
                            $("#submitResults").parent("div").show();
                        }
                    }
                    $("#phaseToggleBtnContainerSubmitPage div").addClass("disabledStatus");
                    $(this).removeClass("disabledStatus")
                    $(this).addClass("");
                    $('#resultSubmissionResults tr:gt(0)').remove();
                    var currentPhase = (parseInt($.trim($(this).attr("id").replace("submission", ""))) + 1)
                    $("#selctedPhaseButton").val(currentPhase.toString());
                    if (currentPhase < parseInt($("#activePhase").val())) {
                        $("#plblSubmission").text("View your previous submissions");
                    } else if (currentPhase === parseInt($("#activePhase").val())) {
                        $("#plblSubmission").text("Submit a new result set or view your previous submissions.");
                    } else { $("#plblSubmission").text("This phase of the competition has not started. You cannot submit results at this time"); }
                    Competition.CompetitionDetails.pageSubmission = 0;
                    CompetitionDetails.prototype.getSubmissionsPageResults($("#selctedPhaseButton").val());

                });
            });
            $("#phaseToggleBtnContainerResultpage div").each(function () {
                $(this).click(function () {
                    $("#phaseToggleBtnContainerResultpage div").addClass("disabledStatus");
                    $(this).removeClass("disabledStatus")
                    $("#selctedPhaseButton").val((parseInt($.trim($(this).attr("id").replace("result", ""))) + 1).toString());
                    $('#seeTheResults tr:gt(0)').remove();
                    Competition.CompetitionDetails.page = 0;
                    $("#selectedRank").val("1");
                    CompetitionDetails.prototype.getCompetitionResults($("#selctedPhaseButton").val());
                });
            });
        }

        public getTabSelectionIdentifiersFromURL() {
            CompetitionDetails.currentMainTab = undefined;
            CompetitionDetails.currentSubTab = undefined;
            var arrTabs = window.location.hash.split("-")
            if (arrTabs !== undefined) {
                switch (arrTabs.length) {
                    case 1:
                        if ($.trim(arrTabs[0]) !== "") {
                            CompetitionDetails.currentMainTab = $.trim(arrTabs[0].replace("#", ""));
                            CompetitionDetails.currentSubTab = undefined;
                        }
                        break;
                    case 2:
                        CompetitionDetails.currentMainTab = $.trim(arrTabs[0].replace("#", ""));
                        CompetitionDetails.currentSubTab = $.trim(arrTabs[1]);
                        break;
                }
            }

        }

        public getTabSelectionbyDefalut() {
            CompetitionDetails.prototype.getTabSelectionIdentifiersFromURL();
            if (CompetitionDetails.currentMainTab) {
                CompetitionDetails.prototype.activateMainTab(CompetitionDetails.currentMainTab)
                if (CompetitionDetails.currentMainTab !== "tab3") {
                    var tabNumber = CompetitionDetails.currentMainTab.replace("tab", "")
                    CompetitionDetails.prototype.getLftTabsForCompetition(parseInt(tabNumber) - 1);
                }
            }
            else {
                CompetitionDetails.prototype.getLftTabsForCompetition(0);
            }
        }

        private redirectToCompetitionRules() {
            window.open("/competitions/details/" + $("#CompetitionId").val() + "#tab1-tab3");
        }
        private fmt2(val) {
            var s = val.toString();
            if (s.length == 1) {
                s = "0" + s;
            }
            return s;
        }
        public lastModifiedDateLabel(dtString: string) {
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
            var mstr = CompetitionDetails.prototype.fmt2(d.getMinutes());
            var sstr = CompetitionDetails.prototype.fmt2(d.getSeconds());
            return "Last modified: " + dstr + " at " + hstr + ":" + mstr + ":" + sstr;
        }

        public activateMainTab(classValue) {
            $('.competitionsDetailTabTop > li').removeClass('active');
            $("." + classValue).addClass('active');
            $('.competitionsDetailTabBlock > li').css('display', 'none');
            $('.competitionsDetailTabBlock').children("." + classValue).css('display', 'block');
        }
    }
}

$(function () {
    var CompetitionDetails = new Competition.CompetitionDetails();
    Competition.CompetitionDetails.page = 0;
    CompetitionDetails.getTabSelectionIdentifiersFromURL();
    $(".headerContent li.active").removeClass("active");
    $("#liCompetition").addClass("active");
    $("#registerCompetition").click(function () { if ($("#registerCompetition").hasClass("disabledStatus")) { return; } $("#registerOptionContainer").hide(); CompetitionDetails.saveUserRegisterStatus(); });
    $(".preloader").show();
    $(".tabArea").hide();
    $("#registerCompetition").addClass("disabledStatus");
    $("#chkRegister").click(function (e) { CompetitionDetails.allowRegister(); });
    $('.competitionsDetailTabTop > li').click(function () {
        var myClass = $(this).attr("class");
        CompetitionDetails.getTabSelectionIdentifiersFromURL();
        if (!$(this).hasClass('active')) {
            CompetitionDetails.activateMainTab(myClass);
            if (!Competition.CompetitionDetails.currentMainTab) {
                window.location.hash = "";
            }
            if ($(this).hasClass("tab3")) {
                if (Competition.CompetitionDetails.currentMainTab !== "tab3") {
                    window.location.hash = "tab3";
                }
                Competition.CompetitionDetails.page = 0;
                $("#seeTheResults > tr").remove();
                $("#selctedPhaseButton").val($("#activePhase").val());
                CompetitionDetails.getCompetitionResults($("#activePhase").val());
            } else if ($(this).hasClass("tab2")) {
                if ((Competition.CompetitionDetails.currentMainTab) !== "tab2") {
                    window.location.hash = "tab2";
                }
                $(".tabArea").hide();
                $("#subContainerBlockForParticipate").html("");
                $('.CompetitionsDetailLftUl > li').removeClass('active');
                CompetitionDetails.getLftTabsForCompetition(1);

            }
            else {
                if (Competition.CompetitionDetails.currentMainTab !== "tab1") {
                    window.location.hash = "tab1";
                }
                $("#subContainerBlock").html("");
                $('.CompetitionsDetailLftUl > li').removeClass('active');
                CompetitionDetails.getLftTabsForCompetition(0);

            }
        }

    })

    window.onresize = function () { if (Competition.CompetitionDetails.loadSucess) { CompetitionDetails.getCompetitionResults($("#selctedPhaseButton").val()) } };
    CompetitionDetails.getAcivePhase();
    CompetitionDetails.getTabSelectionbyDefalut();
    $("#lblLastModifiedDate").text($("#lblLastModifiedDate").text() + " " + CompetitionDetails.lastModifiedDateLabel($("#LastModified").val()));
    window.onscroll = function () {
        if ($(window).scrollTop() == $(document).height() - $(window).height() - 1) {
            if ($(".competitionsDetailTabTop > li.active").hasClass("tab3")) {
                CompetitionDetails.getCompetitionResults($("#selctedPhaseButton").val());
            }
            else if ($(".competitionsDetailTabTop > li.active").hasClass("tab2")) {
                if ($("#tab10").hasClass("active")) {
                    CompetitionDetails.getSubmissionsPageResults($("#selctedPhaseButton").val());
                }
            }
        }
    };

});
