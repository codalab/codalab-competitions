var Competition;
(function (Competition) {
    var CompetitionView = (function () {
        function CompetitionView() { }
        CompetitionView.page = 0;
        CompetitionView.loadSucess = true;
        CompetitionView.prototype.articleClick = function (obj) {
            window.location.href = "/competitions/details/" + $(obj).parent().children("#competitionID").val();
        };
        CompetitionView.prototype.ajaxJSONRequest = function (xUrl, succ, err, data) {
            $.ajax({
                type: "GET",
                url: xUrl,
                cache: false,
                contentType: 'application/json',
                data: data,
                success: succ,
                error: err
            });
        };
        CompetitionView.prototype.getCompetitionList = function () {
            $("#competitionListContainer").children("#competitionTilePreload").remove();
            if(CompetitionView.page > -1 && CompetitionView.loadSucess) {
                CompetitionView.loadSucess = false;
                CompetitionView.page++;
                $("#competitionListContainer").append($("#competitionTilePreload").clone());
                $("#competitionListContainer").children("#competitionTilePreload").css("display", "block");
                var data = {
                    'page': CompetitionView.page,
                    'per_page': 6
                };
                var xUrl = "/competitions/_partials/indexpage";
                var onSuccess = function (data) {
                    if($(data).text() !== "There are no competitions.") {
                        CompetitionView.loadSucess = true;
                        $("#competitionListContainer").append(data);
                        $("#competitionListContainer").children("#competitionTilePreload").remove();
                        $(".articleImageContainer").click(function () {
                            CompetitionView.prototype.articleClick(this);
                        });
                        $(".articleTextArea").click(function () {
                            CompetitionView.prototype.articleClick(this);
                        });
                        if($('body').outerHeight() < $(window).height()) {
                            CompetitionView.prototype.getCompetitionList();
                        }
                    } else {
                        if(this.page === 1) {
                            $("#competitionListContainer").append("<div class=\"competitionTileNoRecord\">" + data + "</div>");
                        }
                        CompetitionView.page = -1;
                        $("#competitionListContainer").children("#competitionTilePreload").remove();
                    }
                };
                var onError = function (xhr, status, error) {
                    $("#competitionListContainer").children("#competitionTilePreload").remove();
                };
                CompetitionView.prototype.ajaxJSONRequest(xUrl, onSuccess, onError, data);
            }
        };
        return CompetitionView;
    })();
    Competition.CompetitionView = CompetitionView;    
})(Competition || (Competition = {}));

$(function () {
    var CompetitionView = new Competition.CompetitionView();
    $("#competitionListContainer").append($("#competitionTilePreload").clone());
    $("#competitionListContainer").children("#competitionTilePreload").css("display", "block");
    $("li.active").removeClass("active");
    $("#liCompetition").addClass("active");
    CompetitionView.getCompetitionList();
    window.onresize = function () {
        if($('body').outerHeight() < $(window).height()) {
            CompetitionView.getCompetitionList();
        }
    };
    window.onscroll = function () {
        if($(window).scrollTop() == $(document).height() - $(window).height()) {
            CompetitionView.getCompetitionList();
        }
    };
    $("#searchInput").bind("propertychange keyup input paste", function () {
        if($.trim($("#searchInput").val()) === "") {
            $("#searchInput").attr("value", "filter by keyword, title or author");
        }
    });
    $("#searchInput").on("focus", function () {
        if($("#searchInput").val() === "filter by keyword, title or author") {
            $("#searchInput").val("");
        } else {
            if($("#searchInput").val() === "") {
                $("#searchInput").val("filter by keyword, title or author");
            }
        }
    });
});
