var Competition;
(function (Competition) {
    var CompetitionList = (function () {
        function CompetitionList() { }
        CompetitionList.pageIManage = 0;
        CompetitionList.pageIParticipate = 0;
        CompetitionList.loadSucess = true;
        CompetitionList.prototype.articleClick = function (obj) {
            window.location.href = "/competition/list/" + $(obj).parent().children("#competitionID").val();
        };
        CompetitionList.doAjaxRequest = function doAjaxRequest(url, containerId, noDataString, page) {
            $("#" + containerId).children("#competitionTilePreload").remove();
            if(page > -1 && CompetitionList.loadSucess) {
                CompetitionList.loadSucess = false;
                $("#" + containerId).append($("#competitionTilePreload").clone());
                $("#" + containerId).children("#competitionTilePreload").css("display", "block");
                var data = {
                    "page": page,
                    "per_page": 6
                };
                var query_s = "page=" + page + "&per_page=6";
                console.log(query_s);
                var xUrl = url;
                var onSuccess = function (data) {
                    if(containerId === "tabAreaCompetitionIManage") {
                        CompetitionList.pageIManage++;
                    } else {
                        CompetitionList.pageIParticipate++;
                    }
                    if($(data).text() !== noDataString) {
                        CompetitionList.loadSucess = true;
                        $("#" + containerId).append(data);
                        $("#" + containerId).children("#competitionTilePreload").remove();
                        $(".articleImageContainer").click(function () {
                            CompetitionList.prototype.articleClick(this);
                        });
                        $(".articleTextArea").click(function () {
                            CompetitionList.prototype.articleClick(this);
                        });
                        if($('body').outerHeight() < $(window).height()) {
                            if(containerId === "tabAreaCompetitionIManage") {
                                CompetitionList.doAjaxRequest(url, containerId, noDataString, CompetitionList.pageIManage);
                            } else {
                                CompetitionList.doAjaxRequest(url, containerId, noDataString, CompetitionList.pageIParticipate);
                            }
                        }
                    } else {
                        if(containerId === "tabAreaCompetitionIManage") {
                            CompetitionList.pageIManage = -1;
                        } else {
                            CompetitionList.pageIParticipate = -1;
                        }
                        if(page === 0) {
                            $("#" + containerId).append("<div class=\"competitionTileNoRecord\">" + data + "</div>");
                        }
                        $("#" + containerId).children("#competitionTilePreload").remove();
                    }
                };
                var onError = function (xhr, status, err) {
                    $("#" + containerId).children("#competitionTilePreload").remove();
                };
                Ajax.AjaxRequest.prototype.ajaxGetRequest(xUrl, onSuccess, onError, data);
            }
        }
        CompetitionList.prototype.showCompetitionIParticipate = function () {
            CompetitionList.loadSucess = true;
            $("#tabAreaCopetitionIParticipate").append($("#competitionTilePreload").clone());
            $("#tabAreaCopetitionIParticipate").children("#competitionTilePreload").css("display", "block");
            var xUrl = "/My/CompetitionsEntered";
            xUrl = Urls.my_competitions_entered();
            CompetitionList.doAjaxRequest(xUrl, "tabAreaCopetitionIParticipate", "You have not participated in any competitions.", CompetitionList.pageIParticipate);
        };
        CompetitionList.prototype.showCompetitionIManage = function () {
            $("#tabAreaCompetitionIManage").append($("#competitionTilePreload").clone());
            $("#tabAreaCompetitionIManage").children("#competitionTilePreload").css("display", "block");
            var xUrl = "/My/CompetitionsManaged";
            xUrl = Urls.my_competitions_managed();
            CompetitionList.doAjaxRequest(xUrl, "tabAreaCompetitionIManage", "You do not manage any competitions.", CompetitionList.pageIManage);
        };
        return CompetitionList;
    })();
    Competition.CompetitionList = CompetitionList;    
})(Competition || (Competition = {}));

$(document).ready(function () {
    var CompetitionList = new Competition.CompetitionList();
    $("li.active").removeClass("active");
    $("#liMycodeLab").addClass("active");
    $('.myCodalabTabArea > li').click(function () {
        var myClass = $(this).attr("class");
        if(!$(this).hasClass('highlightactive')) {
            $('.myCodalabTabArea > li').removeClass('highlightactive');
            $(this).addClass('highlightactive');
            $('.myCodalabTabContent > li').css('display', 'none');
            $('.myCodalabTabContent').children("." + myClass).css('display', 'block');
        }
    });
    $("#tabCompetitionIParticipate").click(function (e) {
        CompetitionList.showCompetitionIParticipate();
    });
    CompetitionList.showCompetitionIManage();
    window.onresize = function () {
        if($('body').outerHeight() < $(window).height()) {
            if($(".highlightactive").attr("id") === "tabCompetitionIManage") {
                CompetitionList.showCompetitionIManage();
            } else {
                CompetitionList.showCompetitionIParticipate();
            }
        }
    };
    window.onscroll = function () {
        if($(window).scrollTop() == $(document).height() - $(window).height()) {
            if($(".highlightactive").attr("id") === "tabCompetitionIManage") {
                CompetitionList.showCompetitionIManage();
            } else {
                CompetitionList.showCompetitionIParticipate();
            }
        }
    };
});
