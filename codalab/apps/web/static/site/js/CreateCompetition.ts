/// <reference path="../../lib/jq/jquery.d.ts" />
/// <reference path="../../lib/jq/jqueryui.d.ts" />
/// <reference path="./FileUpload.ts" />
module Competition {
    export class CreateCompetition extends FileUpload.FileUploadFile {

        private tabSelection() {
            $("#tabs").tabs('enable', parseInt($("#Step").val()) - 1)
           .tabs("option", "active", parseInt($("#Step").val()) - 1)
            // .tabs("option", "disabled", [0, 1]);
            CreateCompetition.prototype.activateSaveButtons();
        }

        public tabOnClick(obj) {
            if (!CreateCompetition.prototype.confirmNavigation()) { return; };
            var objLength = $(obj).attr("id").length;
            $("#Step").val($(obj).attr("id").substring(objLength - 1, objLength));
            CreateCompetition.prototype.tabSelection();
            CreateCompetition.prototype.changeSaveButtonText();
            CreateCompetition.prototype.activateSaveButtons();
        }

        private activateSaveButtons() {
            if ($("#Step").val() === "4") {
                $("#btnSave").hide();
            }
            else { $("#btnSave").show(); }
        }

        private changeSaveButtonText() {
            if ($("#Step").val() === "4") {
                $("#btnSaveConti").val("finish");
            } else {
                $("#btnSaveConti").val("next");
            }
            if ($("#Step").val() === "1") {
                $("#btnSavePrev").addClass("disabledStatus");
            }
            else {
                $("#btnSavePrev").removeClass("disabledStatus");
            }
        }

        public save(event, obj) {
            $("#SaveFlag").val("True")
            var step = parseInt($("#Step").val());
            switch (step) {
                case 1:
                    CreateCompetition.prototype.ajaxRequestForSavingCompetitionInfo(obj);
                    event.preventDefault();
                    break;
                case 2:
                    CreateCompetition.prototype.savePhases(obj);
                    event.preventDefault();
                    break;
                case 3:
                    $(obj).removeClass("disabledStatus")
                    CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageContent(obj)
                    event.preventDefault();
                    break;
            }
        }
        public saveContinue(event, obj) {
            CreateCompetition.prototype.nextStep(obj, event);
        }

        public setValueChanged(event, obj) {
            $("#valueChanged").val("True");
            //var keyCode = event.keyCode || event.which;
            //if (keyCode === 13 || keyCode === 9 || event.type == "blur") {
            //    event.preventDefault();
            //    CreateCompetition.prototype.ajaxRequestForSavingCompetitionInfo(obj)
            //    $("#valueChanged").val("");
            //}
        }

        private ajaxRequestForSavingCompetitionInfo(obj) {
            //  $(obj).siblings(".preloaderInput").remove();
            // $(obj).parent().append($(".preloaderInput").clone());
            // $(obj).siblings(".preloaderInput").css("display", "inline-block");
            var data;
            //switch ($(obj).attr("id")) {
            //    case "Title":
            //        data = { "title": $(obj).val() };
            //        break;
            //    case "Description":
            //        data = { "description": $(obj).val() };
            //        break;
            //}
            data = { "title": $("#Title").val(), "description": $("#Description").val() };
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/info";
            var onSuccess = function (data) {
                CreateCompetition.prototype.managePublishButton(data.published)
                //  CreateCompetition.prototype.makePublicNotification();
                $(obj).removeClass("disabledStatus");
                $("#valueChanged").val("");
                // $(obj).siblings(".preloaderInput").remove();

            };
            var onError = function (xhr, status, err) {
                // $(obj).siblings(".preloaderInput").remove();
                $(obj).removeClass("disabledStatus");
            }
            super.ajaxJSONRequest(xUrl, onSuccess, onError, data);

        }

        private managePublishButton(data) {
            switch (data) {
                case 1:
                    (<HTMLInputElement>$("#Public")[0]).checked = false;
                    $("#btnPublish").addClass("disabledStatus");
                    break;
                case 2:
                    (<HTMLInputElement>$("#Public")[0]).checked = true;
                    $("#btnPublish").addClass("disabledStatus");
                    break;
                case 3:
                    (<HTMLInputElement>$("#Public")[0]).checked = true;
                    $("#btnPublish").removeClass("disabledStatus");
                    break;
            }
            CreateCompetition.prototype.makePublicNotification();
        }

        public makePublicNotification() {
            if (((<HTMLInputElement> $("#Public")[0]).checked) && !$("#btnPublish").hasClass("disabledStatus")) {
                $("#publishNotoficationdiv,#publishNotoficationIcon").show();
            }
            else { $("#publishNotoficationdiv,#publishNotoficationIcon").hide(); }
        }

        private ajaxRequestForSavingCompetitionPageLabel(obj) {
            $(obj).closest("li").children(".buttonPreloaderInput").remove();
            $(obj).closest("li").append($(".buttonPreloaderInput").clone());
            $(obj).closest("li").children(".buttonPreloaderInput").show();
            var lableUpdate = 0;
            var rank;
            var data;
            if ($(obj).parent().parent().hasClass("viewStateOff")) {
                if ($(obj).attr("type") !== undefined) {
                    lableUpdate = 1
                    rank = $.trim($(obj).parent().attr("id").replace("tab", ""))
                    data = data = { "rank": rank, "visible": "False", "label": $(obj).val() };
                } else {

                    rank = $.trim($(obj).parent().parent().attr("id").replace("tab", ""))
                    data = data = { "rank": rank, "visible": "False" };
                }
            } else {
                if ($(obj).attr("type") !== undefined) {
                    lableUpdate = 1
                    rank = $.trim($(obj).parent().attr("id").replace("tab", ""))
                    data = data = { "rank": rank, "visible": "True", "label": $(obj).val() };

                } else {
                    rank = $.trim($(obj).parent().parent().attr("id").replace("tab", ""))
                    data = { "rank": rank, "visible": "True" };
                }
            }
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/page";
            var onSuccess = function (data) {
                CreateCompetition.prototype.managePublishButton(data.published);
                // CreateCompetition.prototype.makePublicNotification();
                if (lableUpdate === 1) {
                    $(obj).hide();
                    $(obj).siblings("label").text($(obj).val())
                    $(obj).siblings().show();
                }
                $(obj).closest("li").children(".buttonPreloaderInput").remove();
                $("#valueChanged").val("");
            };
            var onError = function (xhr, status, err) {
                $(obj).closest("li").children(".buttonPreloaderInput").remove();
            }
            super.ajaxJSONRequest(xUrl, onSuccess, onError, data);
        }

        public ajaxRequestForSavingCompetitionPageContent(obj) {
            var rank;
            var data;
            var HTML;
            if ($(obj).hasClass("disabledStatus")) { return false; }
            $(obj).addClass("disabledStatus");
            $(".textEditor").append($(".buttonPreloaderTxtArea").clone());
            $(".textEditor > .buttonPreloaderTxtArea").show();
            if ($(".competitionsDetailTabTop > li.active").hasClass("tab1")) {
                HTML = $("#textEditorTxtArea").val();
            } else {
                HTML = $("#textEditorTxtArea1").val();
            };
            rank = $.trim($(".textEditorLftTab li.active").attr("id").replace("tab", ""))
            data = data = { "rank": rank, "markup": "", "html": HTML };
            var xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/pagecontent";
            var onSuccess = function (data) {
                CreateCompetition.prototype.managePublishButton(data.published);
                //CreateCompetition.prototype.makePublicNotification()
                $(".textEditor > .buttonPreloaderTxtArea").remove();
                $(obj).removeClass("disabledStatus");
                $("#valueChanged").val("");
            };
            var onError = function (xhr, status, err) {
                $(".textEditor > .buttonPreloaderTxtArea").remove();
                $(this).removeClass("disabledStatus");
            }
            super.ajaxJSONRequest(xUrl, onSuccess, onError, data);
        }

	private getContentPage(pageNumber,target) {
	    
	    var xUrl = Urls.api_competition_page_list(parseInt($("#CompetitionId").val())) + pageNumber

            var onSuccess = function (data) {
		console.log(data.html);
		$(target).val(data.html);
                
            };
            var onError = function (xhr, status, err) {
		console.log("Error requestion detail page")
            };
            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);

	}


        private ajaxRequestForGettingCompetitionPageContent(pageNumber) {
            var xUrl = "/My/competitions/details/" + parseInt($("#CompetitionId").val()) + "/page/" + pageNumber;
	    xUrl = Urls.api_competition_page(parseInt($("#CompetitionId").val(), pageNumber));

            var onSuccess = function (data) {
		// $(target).val(data.html);
                
            };
            var onError = function (xhr, status, err) {
		console.log("Error requestion detail page")
            };
            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        public ajaxRequestForManagingPublishTab() {
            var xUrl;
            if ((<HTMLInputElement>$("#Public")[0]).checked === true) {
                xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/public";
            } else {
                xUrl = "/api/competition/" + parseInt($("#CompetitionId").val()) + "/private";
            };
            var onSuccess = function (data) {
                CreateCompetition.prototype.managePublishButton(data);
                $("#valueChanged").val("");
            };
            var onError = function (xhr, status, err) {

            };
            CreateCompetition.prototype.ajaxPostRequest(xUrl, onSuccess, onError);
        }

        private confirmNavigation() {
            if ($("#valueChanged").val() === "True") {
                if (confirm("You have changed the input value and Do you want to continue")) { $("#valueChanged").val(""); return true; } else {
                    $("#Step").val($("#Step").val());
                    CreateCompetition.prototype.tabSelection();
                    CreateCompetition.prototype.changeSaveButtonText();
                    return false;
                };
            } else { return true; }

        }
	public getDetailTabs() {
	    
	    console.log("OK");
	    var xUrl = Urls.api_contentcontainer_list();
	    console.log(xUrl);
	    var onSuccess = function(data) {
		for (var i=0; i < data.length; i++)
		{
		    var item = data[i];
		    var a = '';
		    if(i === 0) {
			a = ' active';
		    }
		    $("#competition_detail_tab_head").append('<li class="tab' + (item.rank +1) + a + '">' + item.label + '</li>');
		}
	    };
	    var onError = function (xhr, status, err) {
	    };
            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);
	}
	
	public bindCompetitionDetailEvents() {
	    $('.textEditorLftTab > li').click(function () {
                if ($(this).hasClass("viewStateDisabled")) { return false; }
		    var el = $("div:first",this);
		   
		    var tab_id =  $("input.t_tab_id",el).val();
		    var target = $("#textEditorTxtArea"+tab_id);
		    
         	    var pagenum = $(el).find('input.t_id').val()
                    var myClass = $(this).attr("class");
                    if (!$(this).hasClass('active')) {
                        $('.textEditorLftTab > li').removeClass('active');
                        $(this).addClass('active');
                        $(target).val("");
                        CreateCompetition.prototype.getContentPage(pagenum,target);
                    }
                });

                $('.textEditorLftTab > li > div > a').click(function (e) {
                    $(this).parent().parent().children("label").show();
                    $(this).parent().parent().children("input").hide();
                    if (!$(this).parent().parent().hasClass("viewStateOff")) {
                        $(this).parent().parent().addClass("viewStateOff");
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                        e.stopPropagation();
                    } else {
                        $('.textEditorLftTab > li').removeClass('active');
                        $(this).parent().parent().removeClass("viewStateOff");
                        $(this).parent().parent().addClass("active");
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                    }
                });
                $('.textEditorLftTab > li > label').dblclick(function (e) {
                    if (!$(this).parent().hasClass("viewStateAlwaysOn") && !$(this).parent().hasClass("viewStateOff")) {
                        $(this).hide();
                        $(this).siblings().show();
                        e.stopPropagation();
                    }
                });
                $('.textEditorLftTab > li > input').bind("keypress blur", function (e) {
                    var keyCode = e.keyCode || e.which;
                    if (keyCode === 13 || keyCode === 9 || e.type == "blur") {
                        e.preventDefault();
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                    }
                });
	    

	}
        public getLftTabsForCompetition(tabNumber) {
            var xUrl = "/My/competitions/details/" + $("#CompetitionId").val() + "/tab/ " + tabNumber;
            var onSuccess = function (data) {
                if (tabNumber === 0) {
                    $("#textEditorLftTab").html(""); $("#textEditorLftTab").append(data);
                    $('.textEditorLftTab > li').removeClass('active');
                    $("#textEditorLftTab > li:first").addClass("active");
                    CreateCompetition.prototype.ajaxRequestForGettingCompetitionPageContent(parseInt($.trim($("#textEditorLftTab > li:first").attr("id").replace("tab", ""))));
                }
                else {
                    $("#CompetitionsDetailLftParticipateNav").html(""); $("#CompetitionsDetailLftParticipateNav").append(data);
                    $('.textEditorLftTab > li').removeClass('active');
                    $("#CompetitionsDetailLftParticipateNav > li:first").addClass("active");
                    CreateCompetition.prototype.ajaxRequestForGettingCompetitionPageContent(parseInt($.trim($("#CompetitionsDetailLftParticipateNav > li:first").attr("id").replace("tab", ""))));
                }
                $('.textEditorLftTab > li').click(function () {
                    if ($(this).hasClass("viewStateDisabled")) { return false; }
                    var myClass = $(this).attr("class");
                    if (!$(this).hasClass('active')) {
                        $('.textEditorLftTab > li').removeClass('active');
                        $(this).addClass('active');
                        $("#textEditorTxtArea").val("");
                        CreateCompetition.prototype.ajaxRequestForGettingCompetitionPageContent(parseInt($.trim($(this).attr("id").replace("tab", ""))));
                    }
                });

                $('.textEditorLftTab > li > div > a').click(function (e) {
                    $(this).parent().parent().children("label").show();
                    $(this).parent().parent().children("input").hide();
                    if (!$(this).parent().parent().hasClass("viewStateOff")) {
                        $(this).parent().parent().addClass("viewStateOff");
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                        e.stopPropagation();
                    } else {
                        $('.textEditorLftTab > li').removeClass('active');
                        $(this).parent().parent().removeClass("viewStateOff");
                        $(this).parent().parent().addClass("active");
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                    }
                });
                $('.textEditorLftTab > li > label').dblclick(function (e) {
                    if (!$(this).parent().hasClass("viewStateAlwaysOn") && !$(this).parent().hasClass("viewStateOff")) {
                        $(this).hide();
                        $(this).siblings().show();
                        e.stopPropagation();
                    }
                });
                $('.textEditorLftTab > li > input').bind("keypress blur", function (e) {
                    var keyCode = e.keyCode || e.which;
                    if (keyCode === 13 || keyCode === 9 || e.type == "blur") {
                        e.preventDefault();
                        CreateCompetition.prototype.ajaxRequestForSavingCompetitionPageLabel(this);
                    }
                });
            };
            var onError = function (xhr, status, err) {
            };

            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        public genaraltabSelection() {
            CreateCompetition.prototype.tabSelection();

        }
        public changeSaveButtonTextValue() {
            CreateCompetition.prototype.changeSaveButtonText();
        }

        public savePhases(obj) {
            $("#savePhaseProcess").show();
            $(obj).addClass("disabledStatus");
	    
            var xUrl = "/api/competition/" + $("#CompetitionId").val() + "/phases/";
	    xUrl = Urls.api_competitionphases_list($("#CompetitionId").val());
            var p1 = { "label": $("#ph1title").val(), "maxSubmissions": $("#ph1SubmissionLmt").val(), startDate: $("#ph1StartDate").val() };
            var p2 = { "label": $("#ph2title").val(), "maxSubmissions": $("#ph2SubmissionLmt").val(), startDate: $("#ph2StartDate").val() };
            var data = { "endDate": $("#competitionEndDate").val(), "phases": [p1, p2] };
            var onSuccess = function (data) {
                $(obj).removeClass("disabledStatus");
                $("#savePhaseProcess").hide();
                if ((<HTMLInputElement>$("#Public")[0]).checked) {
                    $("#btnPublish").removeClass("disabledStatus");
                }
                CreateCompetition.prototype.makePublicNotification();
                $("#valueChanged").val("");
            };
            var onError = function (xhr, status, err) {
                alert('An error occured [' + err + ']');
                $(obj).removeClass("disabledStatus");
                $("#savePhaseProcess").hide();

            };
            CreateCompetition.prototype.ajaxJSONRequest(xUrl, onSuccess, onError, data);
        }

        public getPhasesDetails() {
            var xUrl = "/api/competition/" + $("#CompetitionId").val() + "/phases/";

	    xUrl = Urls.api_competitionphases_list($("#CompetitionId").val());

            var onSuccess = function (data) {
		if(data.length > 0) {
                    $("#ph1title").val(data.phases[0].label)
                    $("#ph2title").val(data.phases[1].label)
                    $("#ph1SubmissionLmt").val(data.phases[0].maxSubmissions)
                    $("#ph2SubmissionLmt").val(data.phases[1].maxSubmissions)
                    if (data.phases[0].startDate !== null && data.phases[0].startDate !== undefined) {
			$("#ph1StartDate").val($.datepicker.formatDate('mm/dd/yy', new Date(data.phases[0].startDate)));
                    }
                    else { $("#ph1StartDate").val(""); }
                    if (data.phases[0].startDate !== null && data.phases[0].startDate !== undefined) {
			$("#ph2StartDate").val($.datepicker.formatDate('mm/dd/yy', new Date(data.phases[1].startDate)));
                    } else { $("#ph2StartDate").val(""); }
                    if (data.endDate !== null && data.endDate !== undefined) {
			$("#competitionEndDate").val($.datepicker.formatDate('mm/dd/yy', new Date(data.endDate)));
                    } else { $("#competitionEndDate").val(""); }
		}
            };
            var onError = function (xhr, status, err) {
                alert('An error occured [' + err + ']');
            };
            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        public toggleDataset(obj) {
            if ($(obj).parents("section").siblings(".downloadedContainer").is(":visible")) {
                $(obj).children("div").removeClass().addClass('expCollDatasetExp');
                $(obj).parents("section").siblings(".downloadedContainer").hide();
            } else {
                $(obj).children("div > div").removeClass().addClass('expCollDatasetColl');
                $(obj).parents("section").siblings(".downloadedContainer").show();
                var phaseValue = $(obj).parents("section").siblings(".downloadedContainer").children("input:hidden").val()
                CreateCompetition.prototype.getDataSet(parseInt(phaseValue));
            }
        }

        public getDataSet(phaseValue: number) {
            if (phaseValue === 1) {
                $("#downloadedContainer .phaseDatasetDetails").remove();
                $("#preLoaderPh1").show();
            } else {
                $("#preLoaderPh2").show();
                $("#downloadedContainer2 .phaseDatasetDetails").remove();
            }
            var xUrl = "/api/competition/" + $("#CompetitionId").val() + "/phase/" + phaseValue + "/dataset";
            var onSuccess = function (data) {
                for (var v in data) {
                    var dataSet = $("#divDownloadedContainer").clone()
                    $(dataSet).attr("id", v + "divDownloadedContainer")
                    $(dataSet).find("input:#hidDatasetId").val(data[v].DatasetId)
                    $(dataSet).find("input:#SourceUrl").val(data[v].SourceUrl)
                    $(dataSet).find("input:#DownloadUrl").val(data[v].DownloadUrl)
                    if (data[v].Type === 2) {
                        $(dataSet).find("input:#dataSetType").val("Azure Blob")
                    } else { $(dataSet).find("input:#dataSetType").val("Azure Blob Shared Access Signature") }
                    if (phaseValue === 1) {
                        $("#downloadedContainer").append($(dataSet).show());
                    }
                    else {
                        $("#downloadedContainer2").append($(dataSet).show());
                    }
                }
                $("#preLoaderPh1").hide(); $("#preLoaderPh2").hide();

            };
            var onError = function (xhr, status, err) {
                alert('An error occured [' + err + ']');
                $("#preLoaderPh1").hide(); $("#preLoaderPh2").hide();
            };

            CreateCompetition.prototype.ajaxGetRequest(xUrl, onSuccess, onError, null);
        }

        public previousStep(obj, event) {
            $("#Step").val((parseInt($("#Step").val()) - 1).toString());
            CreateCompetition.prototype.tabSelection();
            CreateCompetition.prototype.changeSaveButtonText();
            event.preventDefault();
        }

        private nextStep(obj, event) {
            $("#Step").val((parseInt($("#Step").val()) + 1).toString());
            if ($("#Step").val() > 4) {
                $("#SaveFlag").val("False")
            }
            else {
                CreateCompetition.prototype.tabSelection();
                CreateCompetition.prototype.changeSaveButtonText();
                $(obj).removeClass("disabledStatus");
                event.preventDefault();
            }
        }

    }

}

$(function () {
    var CreateCompetition = new Competition.CreateCompetition();
    $(".uploadLabel").click(function () {
        $("#UploadReason").val("1");
        $("#uploadFile").click();
    });
    //CreateCompetition.getDetailTabs();
    $("#tabs").tabs();
    $(".headerNavigation li.active").removeClass("active");
    $("#liMycodeLab").addClass("active");
    
    CreateCompetition.genaraltabSelection();
    CreateCompetition.changeSaveButtonTextValue();
   
    $("#btnSaveConti").click(function (e) {
        if ($(this).hasClass("disabledStatus")) { e.preventDefault(); }
        $(this).addClass("disabledStatus");
        CreateCompetition.saveContinue(e, this);
    });

    $("#btnSave").click(function (e) {
        if ($(this).hasClass("disabledStatus")) { e.preventDefault(); }
        $(this).addClass("disabledStatus");
        CreateCompetition.save(e, this);
    });

    $("#aTab1").click(function (e) {
        CreateCompetition.tabOnClick(this);
    });
    $("#aTab2").click(function (e) {
        CreateCompetition.tabOnClick(this);
    });
    $("#aTab3").click(function (e) {
        CreateCompetition.tabOnClick(this);
    });
    $("#aTab4").click(function (e) {
        CreateCompetition.tabOnClick(this);
    });
    $('input[type=Text]').bind("change input keydown keypress blur", function (e) {
        CreateCompetition.setValueChanged(e, this);
    });

    $('.competitionsDetailTabTop > li').click(function () {
        if ($(this).hasClass('viewStateOff')) { return; }
        var myClass = $(this).attr("class");
        if (!$(this).hasClass('active')) {
            $('.competitionsDetailTabTop > li').removeClass('active');
            $(this).addClass('active');
            $('.competitionsDetailTabBlock > li').css('display', 'none');
            $('.competitionsDetailTabBlock').children("." + myClass).css('display', 'block');
            CreateCompetition.getLftTabsForCompetition(parseInt($.trim(myClass.replace("tab", ""))) - 1);
        }
        if (myClass === "tab1") {
            $("#applyChanges").css("display", "table-cell");
            $("#applyChangesparticep").hide();

        } else {
            $("#applyChangesparticep").css("display", "table-cell");
            $("#applyChanges").hide();

        }
    });

    // CreateCompetition.getLftTabsForCompetition(0);
    CreateCompetition.bindCompetitionDetailEvents();
    $('.textEditorLftTab > li').click(function () {
        var myClass = $(this).attr("class");
        if (!$(this).hasClass("active")) {
            $('.textEditorLftTab > li').removeClass("active");
            $(this).addClass('active');
            $("#textEditorTxtArea").text("");
        }
    });
    $("#applyChanges,#applyChangesparticep").click(function (e) { CreateCompetition.ajaxRequestForSavingCompetitionPageContent(this); });

    $("#Public").click(function (e) { CreateCompetition.ajaxRequestForManagingPublishTab(); });
    $("#btnPublish").click(function (e) { if ($("#btnPublish").hasClass("disabledStatus")) { return } CreateCompetition.ajaxRequestForManagingPublishTab(); });

    $("#uploadFile").change(function () {
        if ($("#UploadReason").val() === "3") {
            var onSuccess = function (data) {
                CreateCompetition.ajaxRequestForManagingPublishTab();
                if (FileUpload.FileUploadFile.phaseValue === 1) {
                    $("#errorLabelPh1").text("");
                    $("#errorLabelPh1").css("display", "inline-block");
                    $("#errorLabelPh1").text(data.message)
                    $("#ph1datasetimg div").removeClass().addClass('expCollDatasetExp')
                    $("#ph1datasetimg").parents("section").siblings(".downloadedContainer").hide();
                } else {
                    $("#errorLabelPh2").text("");
                    $("#errorLabelPh2").css("display", "inline-block");
                    $("#errorLabelPh2").text(data.message)
                    $("#ph2datasetimg div").removeClass().addClass('expCollDatasetExp')
                    $("#ph2datasetimg").parents("section").siblings(".downloadedContainer").hide();
                }
            };
            CreateCompetition.uploadFile(3, onSuccess);

        }
        else {
            var onSuccess = function (token) {
                (<HTMLImageElement> $("#imgProfileImage")[0]).src = "/file/download/" + token;
            };
            CreateCompetition.uploadFile(1, onSuccess);
        }
    });

    $("#ph1StartDate").datepicker();
    $("#ph1StartDateIcon").click(function () {
        $("#ph1StartDate").datepicker("show");
    });
    $("#ph2StartDateIcon").click(function () {
        $("#ph2StartDate").datepicker("show");

    });
    $("#ph2StartDate").datepicker({
        onSelect: function () {
            if ($("#ph1StartDate").val() === "") {
                alert("Please enter phase1 start date")
                $("#ph2StartDate").val("");
                return false;
            }
            var phase2 = new Date($(this).datepicker('getDate').toString());
            var phase1 = new Date($("#ph1StartDate").datepicker('getDate').toString());
            var dayDiff = Math.ceil((phase2.getTime() - phase1.getTime()) / (1000 * 60 * 60 * 24));
            if (dayDiff < 1) {
                alert("There should be atleast one day differance between phase1 and phase2");
                $("#ph2StartDate").val("");
                return false;
            }
            if ($("#competitionEndDate").val() !== "") {
                var endDate = new Date($("#competitionEndDate").datepicker('getDate').toString());
                var dayDiffEndDate = Math.ceil((phase2.getTime() - endDate.getTime()) / (1000 * 60 * 60 * 24));
                if (dayDiffEndDate > 1) {
                    alert("competition end date cannot be less than the phase dates");
                    $("#ph2StartDate").val("");
                    return false;
                }
            }
        }
    });
    $("#competitionEndDate").datepicker({
        onSelect: function () {
            if ($("#ph1StartDate").val() === "") {
                alert("Please enter phase1 start date")
                $("#competitionEndDate").val("");
                return false;
            }
            if ($("#ph2StartDate").val() === "") {
                alert("Please enter phase2 start date")
                $("#competitionEndDate").val("");
                return false;
            }
            var phase2 = new Date($(this).datepicker('getDate').toString());
            var phase1 = new Date($("#ph2StartDate").datepicker('getDate').toString());
            var dayDiff = Math.ceil((phase2.getTime() - phase1.getTime()) / (1000 * 60 * 60 * 24));
            if (dayDiff < 1) {
                alert("There should be atleast one day differance between  phases and competition end date.");
                $("#competitionEndDate").val("");
            }
        }

    });
    $("#competitionEndDateIcon").click(function () {
        $("#competitionEndDate").datepicker("show");
    });

    $("#savePhase").click(function (e) {
        var TrStartDate = $("#ph1StartDate").val();
        var TeStartDate = $("#ph2StartDate").val();
        if (TrStartDate === "") {
            alert("Please enter Training phase start date");
            return false;
        }
        else if (TeStartDate === "") {
            alert("Please enter testing phase start date.")
            return false;
        }
        CreateCompetition.savePhases(this)
    });
    CreateCompetition.getPhasesDetails();
    $("#ph1dataset,#ph2dataset,#ph2datasetimg,#ph1datasetimg").click(function () {
        CreateCompetition.toggleDataset(this);
    });

    $("#btnSavePrev").click(function (e) {
        if ($(this).hasClass("disabledStatus")) { e.preventDefault(); }
        CreateCompetition.previousStep(this, e);
    });

    CreateCompetition.makePublicNotification();
    $("#uploadManifestph1").click(function () {
        $("#UploadReason").val("3");
        FileUpload.FileUploadFile.phaseValue = 1;
        $("#uploadFile").click();
    })
    $("#uploadManifestph2").click(function () {
        $("#UploadReason").val("3");
        FileUpload.FileUploadFile.phaseValue = 2;
        $("#uploadFile").click();
    })


});
function disableBeforeUnload() {
    window.onbeforeunload = null;
}

window.onbeforeunload = function () {
    if ($("#valueChanged").val() === "True") {
        return "You're about to end your session, are you sure?";
    }
}
