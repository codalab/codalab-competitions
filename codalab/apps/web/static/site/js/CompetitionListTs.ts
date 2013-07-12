/// <reference path="../../lib/jq/jquery.d.ts" />
/// <reference path="./AjaxRequest.ts" />
declare var Urls: any;
module Competition {
    export class CompetitionList {
        static pageIManage = 0;
        static pageIParticipate = 0;
        static loadSucess = true;

        private articleClick(obj) {
            window.location.href = "/competition/list/" + $(obj).parent().children("#competitionID").val();
        }
        static doAjaxRequest(url, containerId, noDataString, page) {
            $("#" + containerId).children("#competitionTilePreload").remove();
            if (page > -1 && loadSucess) {
                loadSucess = false;
                $("#" + containerId).append($("#competitionTilePreload").clone());
                $("#" + containerId).children("#competitionTilePreload").css("display", "block");
                var data = { "page": page, "per_page": 6 };
                var query_s = "page=" + page + "&per_page=6";
		console.log(query_s);
                var xUrl = url;
                var onSuccess = function (data) {
                    if (containerId === "tabAreaCompetitionIManage") { pageIManage++ } else { pageIParticipate++ }
                    if ($(data).text() !== noDataString) {
                        loadSucess = true;
                        $("#" + containerId).append(data);
                        $("#" + containerId).children("#competitionTilePreload").remove();
                        $(".articleImageContainer").click(function () { CompetitionList.prototype.articleClick(this); });
                        $(".articleTextArea").click(function () { CompetitionList.prototype.articleClick(this); });
                        if ($('body').outerHeight() < $(window).height()) {
                            if (containerId === "tabAreaCompetitionIManage") {
                                doAjaxRequest(url, containerId, noDataString, pageIManage);
                            } else {
                                doAjaxRequest(url, containerId, noDataString, pageIParticipate);
                            }
                        }
                    }
                    else {
                        if (containerId === "tabAreaCompetitionIManage") { pageIManage = -1 } else { pageIParticipate = -1 }
                        if (page === 0) { $("#" + containerId).append("<div class=\"competitionTileNoRecord\">" + data + "</div>") }
                        $("#" + containerId).children("#competitionTilePreload").remove();
                    }
                };
                var onError = function (xhr, status, err) {
                    $("#" + containerId).children("#competitionTilePreload").remove();
                };
                Ajax.AjaxRequest.prototype.ajaxGetRequest(xUrl, onSuccess, onError, data);
            }
        }

        showCompetitionIParticipate() {
            CompetitionList.loadSucess = true;
            $("#tabAreaCopetitionIParticipate").append($("#competitionTilePreload").clone());
            $("#tabAreaCopetitionIParticipate").children("#competitionTilePreload").css("display", "block");
            var xUrl = "/My/CompetitionsEntered";
	    xUrl = Urls.my_competitions_entered();
            CompetitionList.doAjaxRequest(xUrl, "tabAreaCopetitionIParticipate", "You have not participated in any competitions.", CompetitionList.pageIParticipate);
        }

        showCompetitionIManage() {
            $("#tabAreaCompetitionIManage").append($("#competitionTilePreload").clone());
            $("#tabAreaCompetitionIManage").children("#competitionTilePreload").css("display", "block");
            var xUrl = "/My/CompetitionsManaged";
	    xUrl = Urls.my_competitions_managed();
            CompetitionList.doAjaxRequest(xUrl, "tabAreaCompetitionIManage", "You do not manage any competitions.", CompetitionList.pageIManage);
        }
    }
}

$(document).ready(function () {
    var CompetitionList = new Competition.CompetitionList();
    $("li.active").removeClass("active");
    $("#liMycodeLab").addClass("active");
    $('.myCodalabTabArea > li').click(function () {
        var myClass = $(this).attr("class");
        if (!$(this).hasClass('highlightactive')) {
            $('.myCodalabTabArea > li').removeClass('highlightactive');
            $(this).addClass('highlightactive');
            $('.myCodalabTabContent > li').css('display', 'none');
            $('.myCodalabTabContent').children("." + myClass).css('display', 'block');
        }
    })
    $("#tabCompetitionIParticipate").click(function (e) { CompetitionList.showCompetitionIParticipate(); });
    CompetitionList.showCompetitionIManage();
    window.onresize = function () {
        if ($('body').outerHeight() < $(window).height()) {
            if ($(".highlightactive").attr("id") === "tabCompetitionIManage") {
                CompetitionList.showCompetitionIManage();
            }
            else { CompetitionList.showCompetitionIParticipate(); }
        }
    };
    window.onscroll = function () {
        if ($(window).scrollTop() == $(document).height() - $(window).height()) {
            if ($(".highlightactive").attr("id") === "tabCompetitionIManage") {
                CompetitionList.showCompetitionIManage();
            }
            else { CompetitionList.showCompetitionIParticipate(); }
        }
    };
});
