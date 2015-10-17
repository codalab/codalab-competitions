//// THIS FILE IS AUTO-GENERATED - DO NOT EDIT!

//// scripts/../codalab/apps/web/static/js/app.js
(function($, window, undefined) {
  'use strict';

  var $doc = $(document),
      Modernizr = window.Modernizr;

  $(document).ready(function() {
    if ($.fn.foundationAlerts) $doc.foundationAlerts();
    if ($.fn.foundationButtons) $doc.foundationButtons();
    if ($.fn.foundationAccordion) $doc.foundationAccordion();
    if ($.fn.foundationNavigation) $doc.foundationNavigation();
    if ($.fn.foundationTopBar) $doc.foundationTopBar();
    if ($.fn.foundationCustomForms) $doc.foundationCustomForms();
    if ($.fn.foundationMediaQueryViewer) $doc.foundationMediaQueryViewer();
    if ($.fn.foundationTabs) $doc.foundationTabs({callback: $.foundation.customForms.appendCustomMarkup});
    if ($.fn.foundationTooltips) $doc.foundationTooltips();
    if ($.fn.foundationMagellan) $doc.foundationMagellan();
    if ($.fn.foundationClearing) $doc.foundationClearing();

    if ($.fn.placeholder) $('input, textarea').placeholder();
  });

  // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
  // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
  // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
  // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
  // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

  // Hide address bar on mobile devices (except if #hash present, so we don't mess up deep linking).
  if (Modernizr.touch && !window.location.hash) {
    $(window).load(function() {
      setTimeout(function() {
        window.scrollTo(0, 1);
      }, 0);
    });
  }

})(jQuery, this);

//// scripts/../codalab/apps/web/static/js/Competition.js
var Competition;
(function(Competition) {

    // Competition.invokePhaseButtonOnOpen = function(id) {
    //     var btn = $('#' + id + ' .btn.selected')[0];
    //     if (btn === undefined) {
    //         btn = $('#' + id + ' .btn.active')[0];
    //         if (btn === undefined) {
    //             btn = $('#' + id + ' .btn')[0];
    //         }
    //     }
    //     btn.click();
    // };

    function decorateLeaderboardButton(btn, submitted) {
        if ($('#disallow_leaderboard_modifying').length > 0) {
            btn.text('Leaderboard modifying disallowed').attr('disabled', 'disabled');
        } else {
            if (submitted) {
                btn.removeClass('leaderBoardSubmit');
                btn.addClass('leaderBoardRemove');
                btn.text('Remove from Leaderboard');
            } else {
                btn.removeClass('leaderBoardRemove');
                btn.addClass('leaderBoardSubmit');
                btn.text('Submit to Leaderboard');
            }
        }
    }

    function updateLeaderboard(competition, submission, cstoken, btn) {
        var url = '/api/competition/' + competition + '/submission/' + submission + '/leaderboard';
        var op = '';
        if (btn.hasClass('leaderBoardSubmit')) {
            op = 'post';
        } else if (btn.hasClass('leaderBoardRemove')) {
            op = 'delete';
        }
        request = $.ajax({
            url: url,
            type: op,
            datatype: 'text',
            data: {
                'csrfmiddlewaretoken': cstoken
            },
            success: function(response, textStatus, jqXHR) {
                var added = op == 'post';
                if (added) {
                    var rows = $('#user_results td.status');
                    rows.removeClass('submitted');
                    rows.addClass('not_submitted');
                    rows.html('');
                    var row = $('#' + submission + ' td.status');
                    row.addClass('submitted');
                    row.html('<span class="glyphicon glyphicon-ok"></span>');
                    $('#user_results .leaderboard_button.leaderBoardRemove').each(function(index) {
                        decorateLeaderboardButton($(this), false);
                    });
                } else {
                    var row = $('#' + submission + ' td.status');
                    row.removeClass('submitted');
                    row.addClass('not_submitted');
                    row.html('');
                }
                decorateLeaderboardButton(btn, added);
            },
            error: function(jsXHR, textStatus, errorThrown) {
                alert('An error occurred. Please try again or report the issue');
            },
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', cstoken);
            }
        });
    }

    Competition.getPhaseSubmissions = function(competitionId, phaseId, cstoken) {

        $('.competition_submissions').html('').append("<div class='competitionPreloader'></div>").children().css({ 'top': '200px', 'display': 'block' });
        var url = '/competitions/' + competitionId + '/submissions/' + phaseId;
        $.ajax({
            type: 'GET',
            url: url,
            cache: false,
            success: function(data) {
                $('.competition_submissions').html('').append(data);
                if (CodaLab.FileUploader.isSupported() === false) {
                    $('#fileUploadButton').addClass('disabled');
                    $('#details').html('Sorry, your browser does not support the HTML5 File API. Please use a newer browser.');
                } else {
                    new CodaLab.FileUploader({
                        buttonId: 'fileUploadButton',
                        sasEndpoint: '/api/competition/' + competitionId + '/submission/sas',
                        allowedFileTypes: ['application/zip', 'application/x-zip-compressed'],
                        maxFileSizeInBytes: 1024 * 1024 * 1024,
                        validateBeforeFilePrompt: function() {
                            if($('#submission_method_name').length == 0) {
                                // if we dont have submision method field, just skip this check
                                return true;
                            }

                            var team_name = $('#submission_team_name').val();
                            var method_name = $('#submission_method_name').val();
                            var method_description = $('#submission_method_description').val();

                            return (team_name && team_name !== '') &&
                                   (method_name && method_name !== '') &&
                                   (method_description && method_description !== '');
                        },
                        beforeSelection: function(info, valid) {
                            $('#fileUploadButton').addClass('disabled');
                        },
                        afterSelection: function(info, valid) {
                            if (valid === false) {
                                if (info.files.length > 0) {
                                    if (info.files[0].errors[0].kind === 'type-error') {
                                        $('#details').html('Please select a valid file. Only ZIP files are accepted.');
                                    } else {
                                        $('#details').html('The files that you selected is too large. There is a 1GB size limit.');
                                    }
                                }
                                $('#fileUploadButton').removeClass('disabled');
                            }
                        },
                        uploadProgress: function(file, bytesUploaded, bytesTotal) {
                            var pct = (100 * bytesUploaded) / bytesTotal;
                            $('#details').html('Uploading file <em>' + file.name + '</em>: ' + pct.toFixed(0) + '% complete.');
                        },
                        uploadError: function(info) {
                            $('#details').html('There was an error uploading the file. Please try again.');
                            $('#fileUploadButton').removeClass('disabled');
                        },
                        uploadSuccess: function(file, trackingId) {
                            $('#details').html('Creating new submission...');
                            var description = $('#submission_description_textarea').val() || '';
                            var method_name = $('#submission_method_name').val() || '';
                            var method_description = $('#submission_method_description').val() || '';
                            var project_url = $('#submission_project_url').val() || '';
                            var publication_url = $('#submission_publication_url').val() || '';
                            var bibtex = $('#submission_bibtex').val() || '';
                            var team_name = $('#submission_team_name').val() || '';
                            var organization_or_affiliation = $('#submission_organization_or_affiliation').val() || '';
                            var phase_id = $('#submission_phase_id').val();

                            $('#submission_description_textarea').val('');
                            $.ajax({
                                url: '/api/competition/' + competitionId + '/submission?description=' + encodeURIComponent(description) +
                                                                                      '&method_name=' + encodeURIComponent(method_name) +
                                                                                      '&method_description=' + encodeURIComponent(method_description) +
                                                                                      '&project_url=' + encodeURIComponent(project_url) +
                                                                                      '&publication_url=' + encodeURIComponent(publication_url) +
                                                                                      '&team_name=' + encodeURIComponent(team_name) +
                                                                                      '&organization_or_affiliation=' + encodeURIComponent(organization_or_affiliation) +
                                                                                      '&bibtex=' + encodeURIComponent(bibtex) +
                                                                                      '&phase_id=' + encodeURIComponent(phase_id),
                                type: 'post',
                                cache: false,
                                data: { 'id': trackingId, 'name': file.name, 'type': file.type, 'size': file.size }
                            }).done(function(response) {
                                $('#details').html('');
                                $('#user_results tr.noData').remove();
                                $('#user_results').append(Competition.displayNewSubmission(response, description, method_name, method_description, project_url, publication_url, bibtex, team_name, organization_or_affiliation));
                                $('#user_results #' + response.id + ' .glyphicon-plus').on('click', function() { Competition.showOrHideSubmissionDetails(this) });
                                $('#fileUploadButton').removeClass('disabled');
                                //$('#fileUploadButton').text("Submit Results...");
                                $('#user_results #' + response.id + ' .glyphicon-plus').click();
                            }).fail(function(jqXHR) {
                                var msg = 'An unexpected error occurred.';
                                if (jqXHR.status == 403) {
                                    msg = jqXHR.responseJSON.detail;
                                }
                                $('#details').html(msg);
                                //$('#fileUploadButton').text("Submit Results...");
                                $('#fileUploadButton').removeClass('disabled');
                            });
                        }
                    });
                }
                $('#user_results .glyphicon-plus').on('click', function() {
                    Competition.showOrHideSubmissionDetails(this);
                });
            },
            error: function(xhr, status, err) {
                $('.competition_submissions').html("<div class='alert alert-error'>An error occurred. Please try refreshing the page.</div>");
            }
        });
    };

    Competition.getPhaseResults = function(competitionId, phaseId) {
        $('.competition_results').html('').append("<div class='competitionPreloader'></div>").children().css({ 'top': '200px', 'display': 'block' });
        var url = '/competitions/' + competitionId + '/results/' + phaseId;
        $.ajax({
            type: 'GET',
            url: url,
            cache: false,
            success: function(data) {
                $('.competition_results').html('').append(data);
                $('.column-selectable').click(function(e) {
                    var table = $(this).closest('table');
                    $(table).find('.column-selected').removeClass();
                    $(this).addClass('column-selected');
                    var columnId = $(this).attr('name');
                    var rows = table.find('td').filter(function() {
                        return $(this).attr('name') === columnId;
                    }).addClass('column-selected');
                    if (rows.length > 0) {
                        var sortedRows = rows.slice().sort(function(a, b) {
                            var ar = parseInt($.text([$(a).find('span')]));
                            if (isNaN(ar)) {
                                ar = 100000;
                            }
                            var br = parseInt($.text([$(b).find('span')]));
                            if (isNaN(br)) {
                                br = 100000;
                            }
                            return ar - br;
                        });
                        var parent = rows[0].parentNode.parentNode;
                        var clonedRows = sortedRows.map(function() { return this.parentNode.cloneNode(true); });
                        for (var i = 0; i < clonedRows.length; i++) {
                            $(clonedRows[i]).find('td.row-position').text($(clonedRows[i]).find('td.column-selected span').text());
                            parent.insertBefore(clonedRows[i], rows[i].parentNode);
                            parent.removeChild(rows[i].parentNode);
                        }
                    }
                });
            },
            error: function(xhr, status, err) {
                $('.competition_results').html("<div class='alert alert-error'>An error occurred. Please try refreshing the page.</div>");
            }
        });
    };

    Competition.registationCanProceed = function() {
        if ($('#checkbox').is(':checked') === true) {
            $('#participateButton').removeClass('disabledStatus');
        } else {
            $('#participateButton').addClass('disabledStatus');
        }
    };

    Competition.displayRegistrationStatus = function(competitionId) {
        var sOut = '';
        $.ajax({
            type: 'GET',
            url: '/api/competition/' + competitionId + '/mystatus/',
            cache: false,
            success: function(data) {
                console.log(data);
                if (data['status'] == 'approved') {
                    location.reload();
                } else if (data['status'] == 'pending') {
                    sOut = "<div class='participateInfoBlock pendingApproval'>";
                    sOut += "<div class='infoStatusBar'></div>";
                    sOut += "<div class='labelArea'>";
                    sOut += "<label class='regApprovLabel'>Your request to participate in this challenge has been received and a decision is pending.</label>";
                    sOut += '<label></label>';
                    sOut += '</div>';
                    sOut += '</div>';
                } else if (data['status'] == 'denied') {
                    sOut = "<div class='participateInfoBlock'>";
                    sOut += "<div class='infoStatusBar'></div>";
                    sOut += "<div class='labelArea'>";
                    sOut += "<label class='regDeniedLabel'>Your request to participate in this challenge has been denied. The reason for your denied registrations is: " + data['reason'] + '</label>';
                    sOut += '<label></label>';
                    sOut += '</div>';
                    sOut += '</div>';
                }
                location.reload();
            },
            error: function(xhr, status, err) {
                $('.competition_results').html("<div class='alert - error'>An error occurred. Please try refreshing the page.</div>");
            }
        });


        return sOut;
    };

    function fmt2(val) {
        var s = val.toString();
        if (s.length == 1) {
            s = '0' + s;
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
        return 'Last modified: ' + dstr + ' at ' + hstr + ':' + mstr + ':' + sstr;
    }

    Competition.displayNewSubmission = function(response, description, method_name, method_description, project_url, publication_url, bibtex, team_name, organization_or_affiliation) {
        var elemTr = $('#submission_details_template #submission_row_template tr').clone();
        $(elemTr).attr('id', response.id.toString());
        $(elemTr).addClass(Competition.oddOrEven(response.submission_number));

        if (description !== undefined && description !== '') {
            $(elemTr).attr('data-description', description);
        }
        if (method_name !== undefined && method_name !== '') {
            $(elemTr).attr('data-method-name', method_name);
        }
        if (method_description !== undefined && method_description !== '') {
            $(elemTr).attr('data-method-description', method_description);
        }
        if (project_url !== undefined && project_url !== '') {
            $(elemTr).attr('data-project-url', project_url);
        }
        if (publication_url !== undefined && publication_url !== '') {
            $(elemTr).attr('data-publication-url', publication_url);
        }
        if (bibtex !== undefined && bibtex !== '') {
            $(elemTr).attr('data-bibtex', bibtex);
        }
        if (team_name !== undefined && team_name !== '') {
            $(elemTr).attr('data-team-name', team_name);
        }
        if (organization_or_affiliation !== undefined && organization_or_affiliation !== '') {
            $(elemTr).attr('data-organization-or-affiliation', organization_or_affiliation);
        }

        $(elemTr).children().each(function(index) {
            switch (index) {
                case 0:
                    if (response.status === 'finished') {
                        $(this).val('1');

                        // Add the check box if auto submitted to leaderboard
                        if ($('#forced_to_leaderboard').length > 0) {
                            // Remove previous checkmarks
                            $('.glyphicon-ok').remove();

                            $($(elemTr).children('td')[4]).html('<span class="glyphicon glyphicon-ok"></span>');
                        }
                    }
                    break;
                case 1: $(this).html(response.submission_number.toString()); break;
                case 2: $(this).html(response.filename); break;
                case 3:
                    var fmt = function(val) {
                        var s = val.toString();
                        if (s.length == 1) {
                            s = '0' + s;
                        }
                        return s;
                    };
                    var dt = new Date(response.submitted_at);
                    var d = ('0' + (dt.getMonth() + 1).toString()).slice(-2) + '/' + dt.getDate().toString() + '/' + dt.getFullYear();
                    var h = ('0' + dt.getHours().toString()).slice(-2);
                    var m = fmt(dt.getMinutes());
                    var s = fmt(dt.getSeconds());
                    $(this).html(d + ' ' + h + ':' + m + ':' + s);
                    break;
                case 4: $(this).html(Competition.getSubmissionStatus(response.status)); break;
            }
        }
      );
        return elemTr;
    };

    Competition.oddOrEven = function(x) {
        return (x & 1) ? 'odd' : 'even';
    };

    Competition.getSubmissionStatus = function(status) {
        var subStatus = 'Unknown';
        if (status === 'submitting') {
            subStatus = 'Submitting';
        } else if (status === 'submitted') {
            subStatus = 'Submitted';
        } else if (status === 'running') {
            subStatus = 'Running';
        } else if (status === 'failed') {
            subStatus = 'Failed';
        } else if (status === 'cancelled') {
            subStatus = 'Cancelled';
        } else if (status === 'finished') {
            subStatus = 'Finished';
        }
        return subStatus;
    };

    Competition.toggleSubmissionPublic = function(event) {
        event.preventDefault();

        // Remove focus from link
        this.blur();

        var submissionId = $(this).attr('submission-id');
        var linkElement = $(this);

        $.get('/my/competition/submission/' + submissionId + '/toggle_make_public')
            .success(function(data) {
                var isPublic = data == 'True' ? 'private':'public';
                linkElement.html('Make your submission ' + isPublic);
            })
            .error(function() {
                alert('Error making submission public, is your Internet connection working?')
            });

        return false;
    };

    Competition.updateSubmissionDescription = function(event) {
        event.preventDefault();

        var element = this;

        // Remove focus from link
        element.blur();

        var submission_id = $(this).attr('submission-id');
        var new_description = $(this).parent().find('textarea[name="updated_description"]').val() || '';
        // Escape html
        new_description = new_description.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

        $.post('/competitions/update_description/' + submission_id, {'updated_description': new_description})
            .success(function() {
                $(element).parent().find('.submission_description').html("<b>Description:</b> <br><pre>" + new_description + "</pre>");
                $(element).parent().find('textarea[name="updated_description"]').val('').hide();
                $(element).parent().find('.update_description_btn').removeClass('hide').show();
                $(element).hide();
            })
            .error(function() {
                alert('Error updating description, is your Internet connection working?')
            });
    };

    Competition.showOrHideSubmissionDetails = function(obj) {
        var nTr = $(obj).parents('tr')[0];
        if ($(obj).hasClass('glyphicon-minus')) {
            $(obj).removeClass('glyphicon-minus');
            $(obj).addClass('glyphicon-plus');
            $(nTr).next('tr.trDetails').remove();
        }
        else {
            $(obj).removeClass('glyphicon-plus');
            $(obj).addClass('glyphicon-minus');
            var elem = $('#submission_details_template .trDetails').clone();
            elem.find('.tdDetails').attr('colspan', nTr.cells.length);
            elem.find('a').each(function(i) { $(this).attr('href', $(this).attr('href').replace('_', nTr.id)) });

            if ($(nTr).attr('data-description') !== undefined) {
                elem.find('.submission_description').html('<b>Description:</b> <br><pre>' + $(nTr).attr('data-description') + '</pre>');
            }
            if ($(nTr).attr('data-team-name')) {
                elem.find('.submission_team_name').html('<b>Team name:</b> ' + $(nTr).attr('data-team-name'));
            }
            if ($(nTr).attr('data-method-name')) {
                elem.find('.submission_method_name').html('<b>Method name:</b> ' + $(nTr).attr('data-method-name'));
            }
            if ($(nTr).attr('data-method-description')) {
                elem.find('.submission_method_description').html('<b>Method description:</b><br><pre>' + $(nTr).attr('data-method-description') + '</pre>');
            }
            if ($(nTr).attr('data-project-url')) {
                elem.find('.submission_project_url').html('<b>Project URL:</b> <a href="' + $(nTr).attr('data-project-url') + '">' + $(nTr).attr('data-project-url') + '</a>');
            }
            if ($(nTr).attr('data-publication-url')) {
                elem.find('.submission_publication_url').html('<b>Publication URL:</b> <a href="' + $(nTr).attr('data-publication-url') + '">' + $(nTr).attr('data-publication-url') + '</a>');
            }
            if ($(nTr).attr('data-bibtex')) {
                elem.find('.submission_bibtex').html('<b>Bibtex:</b><br><pre>' + $(nTr).attr('data-bibtex') + '</pre>');
            }
            if ($(nTr).attr('data-organization-or-affiliation')) {
                elem.find('.submission_organization_or_affiliation').html('<b>Organization/affiliation:</b> ' + $(nTr).attr('data-organization-or-affiliation'));
            }
            if ($(nTr).attr('data-exception')) {
                elem.find('.traceback').html('Error: <br><pre>' + $(nTr).attr('data-exception') + '</pre>');
            }

            var isPublic = $(nTr).attr('data-is-public') ? 'private':'public';
            elem.find('.public_link').html('Make your submission ' + isPublic);
            elem.find('.public_link').click(Competition.toggleSubmissionPublic);
            elem.find('.public_link').attr('submission-id', nTr.id);

            elem.find('.save_description_btn').click(Competition.updateSubmissionDescription);
            elem.find('.save_description_btn').attr('submission-id', nTr.id);

            elem.find('.update_description_btn').click(function() {
                var current_text = $(this).parent().find('.submission_description').text();
                if(current_text.indexOf('Description: ') !== -1) {
                    current_text = current_text.substr('Description: '.length);
                } else {
                    current_text = '';
                }
                $(this).parent().find('.save_description_btn').removeClass('hide').show();
                $(this).parent().find('textarea[name="updated_description"]').removeClass('hide').show().val(current_text);
                $(this).hide();
            });

            var phasestate = $('#phasestate').val();
            var state = $(nTr).find("input[name='state']").val();
            if ((phasestate == 1) && (state == 1)) {
                var btn = elem.find('.leaderboard_button');
                btn.removeClass('hide');
                var submitted = $(nTr).find('.status').hasClass('submitted');
                var competition = $('#competitionId').val();
                decorateLeaderboardButton(btn, submitted);
                btn.on('click', function() {
                    updateLeaderboard(competition, nTr.id, $('#cstoken').val(), btn);
                });
            }
            else {
                var status = $.trim($(nTr).find('.statusName').html());
                var btn = elem.find('.leaderboard_button').addClass('hide');
                if (status === 'Submitting' || status === 'Submitted' || status === 'Running') {
                    btn.removeClass('hide');
                    btn.text('Refresh status');
                    btn.on('click', function() {
                        Competition.updateSubmissionStatus($('#competitionId').val(), nTr.id, this);
                    });
                }
                if (status === 'Failed' || status === 'Cancelled') {
                    elem.find('a').removeClass('hide');
                }
            }
            $(nTr).after(elem);
        }
    };

    Competition.updateSubmissionStatus = function(competitionId, submissionId, obj) {
        $(obj).parents('.submission_details').find('.preloader-handler').append("<div class='competitionPreloader'></div>").children().css({ 'top': '25px', 'display': 'block' });
        var url = '/api/competition/' + competitionId + '/submission/' + submissionId;
        $.ajax({
            type: 'GET',
            url: url,
            cache: false,
            success: function(data) {
                $('#user_results #' + submissionId).find('.statusName').html(Competition.getSubmissionStatus(data.status));
                if (data.status === 'finished') {
                    $('#user_results #' + submissionId + 'input:hidden').val('1');
                    var phasestate = $('#phasestate').val();
                    if (phasestate == 1) {
                        if ($('#disallow_leaderboard_modifying').length > 0) {
                            $(obj).text('Leaderboard modifying disallowed').attr('disabled', 'disabled');

                            if ($('#forced_to_leaderboard').length > 0) {
                                // Remove all checkmarks
                                $('.glyphicon-ok').remove();
                                // Get the 4th table item and put a checkmark there
                                $($('#' + submissionId + ' td')[4]).html('<span class="glyphicon glyphicon-ok"></span>');
                            }
                        } else {
                            if ($('#forced_to_leaderboard').length == 0) {
                                $(obj).addClass('leaderBoardSubmit');
                                $(obj).text('Submit to Leaderboard');
                            } else {
                                // Remove all checkmarks
                                $('.glyphicon-ok').remove();
                                // Get the 4th table item and put a checkmark there
                                $($('#' + submissionId + ' td')[4]).html('<span class="glyphicon glyphicon-ok"></span>');

                                $(obj).removeClass('leaderBoardSubmit');
                                $(obj).addClass('leaderBoardRemove');
                                $(obj).text('Remove from Leaderboard');
                            }
                        }

                        $(obj).unbind('click').off('click').on('click', function() {
                            updateLeaderboard(competitionId, submissionId, $('#cstoken').val(), $(obj));
                        });
                    } else {
                        $(obj).addClass('hide');
                    }
                }
                else if (data.status === 'failed' || data.status === 'cancelled') {
                    $(obj).addClass('hide');
                    $(obj).parent().parent().find('a').removeClass('hide');
                    if (data.exception_details) {
                        $('a[href="traceback/' + submissionId + '/"]').parent().html('Error: <br><pre>' + data.exception_details + '</pre>');
                    }
                }
                $('.competitionPreloader').hide();
            },
            error: function(xhr, status, err) {

            }
        });
    };

    Competition.initialize = function() {
        var prTable;
        $(document).ready(function() {
            $('#participate_form').submit(function(event) {
                event.preventDefault();
                if ($('#participateButton').hasClass('disabledStatus')) {
                    return false;
                }
                $('#result').html('');
                var values = $(this).serialize();
                var competitionId = $('#competitionId').val();
                request = $.ajax({
                    url: '/api/competition/' + competitionId + '/participate/',
                    type: 'post',
                    dataType: 'text',
                    data: values,
                    success: function(response, textStatus, jqXHR) {
                        $('.content form').replaceWith(Competition.displayRegistrationStatus(competitionId));
                    },
                    error: function(jsXHR, textStatus, errorThrown) {
                        alert('There was a problem registering for this competition.');
                    }
                });
                return false;
            });

            $('#submissions_phase_buttons .btn').each(function(e, index) {
                $(this).click(function() {
                    var phaseId = $.trim($(this).attr('id').replace('submissions_phase_', ''));
                    $('#submissions_phase_buttons .btn').removeClass('selected');
                    $(this).addClass('selected');
                    var competitionId = $('#competitionId').val();
                    var cstoken = $('#cstoken').val();
                    Competition.getPhaseSubmissions(competitionId, phaseId, cstoken);
                });
            });

            // $("a[href='#participate-submit_results']").click(function(obj) {
            //     Competition.invokePhaseButtonOnOpen('submissions_phase_buttons');
            // });

            $('#results_phase_buttons .btn').each(function(e, index) {
                $(this).click(function() {
                    var phaseId = $.trim($(this).attr('id').replace('results_phase_', ''));
                    $('#results_phase_buttons .btn').removeClass('selected');
                    $(this).addClass('selected');
                    var competitionId = $('#competitionId').val();
                    Competition.getPhaseResults(competitionId, phaseId);
                });
            });

            // $('#Results').click(function(obj) {
            //     Competition.invokePhaseButtonOnOpen('results_phase_buttons');
            // });

            // This helps make sections appear with Foundation
            // $(this).foundation('section', 'reflow');

            $('.top-bar-section ul > li').removeClass('active');

            $('#liCompetitions').addClass('active');


            $('#competition-publish-button').click(function(e) {
                e.preventDefault();
                var competition_actions = $(this).parent()[0];
                request = $.ajax({
                    url: $(this).attr('href'),
                    success: function(response, textStatus, jqXHR) {
                        console.log('Published competition.');
                        $(competition_actions).children('#competition-publish-button').hide();
                        $(competition_actions).children('#competition-delete-button').hide();
                        $(competition_actions).children('#competition-unpublish-button').show();
                    },
                    error: function(jsXHR, textStatus, errorThrown) {
                        var data = $.parseJSON(jsXHR.responseJSON);
                        if (data.error) {
                            alert(data.error);
                        }
                        console.log('Error publishing competition!');
                    }
                });
            });

            $('#competition-unpublish-button').click(function(e) {
                e.preventDefault();
                // This shows how unpublishing a competition works. We have this commented out
                // because we don't want competition owners to inadvertantly unpublish, then delete
                // competitions that have submissions and results.
                // If this decision is changed in the future simply uncommenting this code will enable
                // competitions to be unpublished.
                // Only unpublished competitions are able to be deleted.
                var competition_actions = $(this).parent()[0];
                request = $.ajax({
                   url: $(this).attr('href'),
                   success: function(response, textStatus, jqXHR) {
                       console.log('Unpublished competition.');
                       $(competition_actions).children('#competition-publish-button').show();
                       $(competition_actions).children('#competition-delete-button').show();
                       $(competition_actions).children('#competition-unpublish-button').hide();
                   },
                   error: function(jsXHR, textStatus, errorThrown) {
                       console.log('Error unpublishing competition!');
                   }
                });
            });

            $('#my_managing .competition-tile .competition-actions').each(function(e, index) {
                if ($(this)[0].getAttribute('published') == 'True') {
                    $(this).find('#competition-delete-button').hide();
                    $(this).find('#competition-publish-button').hide();
                    $(this).find('#competition-unpublish-button').show();
                } else {
                    $(this).find('#competition-delete-button').show();
                    $(this).find('#competition-publish-button').show();
                    $(this).find('#competition-unpublish-button').hide();
                }
            });

        });
    };
})(Competition || (Competition = {}));

//// scripts/../codalab/apps/web/static/js/main.js
// This contains the required functions and global vars used
// for validation, security and authentication mostly for API use

// CSRF Token needs to be sent with API requests.
var csrftoken;

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
}

$(function() {
    // Some of this copied from Django docs:
    // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax

    csrftoken = $.cookie('csrftoken');

    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
    }
    });
});


var CodaLab;
(function(CodaLab) {

    var FileUploader = (function() {
        function FileUploader(options) {
            var _this = this;
            this.defaultOptions = {
                buttonId: 'fileUploadButton',
                disabledClassName: 'disabled',
                validateBeforeFilePrompt: function() {
                    return true;
                },
                beforeSelection: function() {
                },
                afterSelection: function(info, valid) {
                },
                uploadProgress: function(file, bytesUploaded, bytesTotal) {
                },
                uploadSuccess: function(file) {
                },
                uploadError: function(info) {
                },
                allowedFileTypes: undefined,
                extensionToFileType: {'zip': 'application/zip'},
                maxFileSizeInBytes: undefined,
                maxBlockSizeInBytes: 1024 * 1024
            };
            this.options = $.extend({}, this.defaultOptions, options);
            var button = $('#' + this.options.buttonId);
            this.setupFileInput();
            button.after(this.fileInput);
            button.on('click', function(e) {
                var disabled = button.hasClass(_this.options.disabledClassName);
                if (!disabled) {
                    if(_this.options.validateBeforeFilePrompt()) {
                        _this.fileInput.click();
                    } else {
                        alert('Please fill in all required fields first!');
                    }
                }
            });
        }
        FileUploader.prototype.setupFileInput = function() {
            var _this = this;
            var currentFileInput = this.fileInput;
            this.fileInput = $(document.createElement('input'));
            this.fileInput.attr('type', 'file');
            this.fileInput.attr('style', 'visibility: hidden; width: 1px; height: 1px;');
            this.fileInput.on('change', function(e) {
                _this.options.beforeSelection();
                var selectionInfo = _this.validate();
                var valid = selectionInfo.files.length > 0 && FileUploader.selectionIsValid(selectionInfo) === true;
                _this.options.afterSelection(selectionInfo, valid);
                if (valid) {
                    _this.beginUpload(selectionInfo, 0);
                } else {
                    _this.setupFileInput();
                }
            });
            if (currentFileInput !== undefined) {
                currentFileInput.replaceWith(this.fileInput);
            }
        };

        FileUploader.prototype.validate = function() {
            var _this = this;
            var inputFiles = this.fileInput.get(0).files;
            var validatedFiles = [];
            if (inputFiles.length > 0) {
                $.each(inputFiles, function(i, file) {
                    var errors = [];
                    if (_this.options.maxFileSizeInBytes && file.size > _this.options.maxFileSizeInBytes) {
                        errors.push({ kind: 'size-error' });
                    }

                    var filetype = file.type;
                    if (filetype === '') {
                        var parts = file.name.split('.');
                        if (parts.length > 1) {
                            filetype = _this.options.extensionToFileType[parts.pop().toLowerCase()];
                        }
                    }
                    if (_this.options.allowedFileTypes && ($.inArray(filetype, _this.options.allowedFileTypes)) === -1) {
                        errors.push({ kind: 'type-error' });
                    }
                    validatedFiles.push({ file: file, errors: errors });
                });
            }
            return { files: validatedFiles };
        };

        FileUploader.selectionIsValid = function(selection) {
            var numErrors = selection.files.map(function(item) {
                return item['errors'].length;
            }).reduce(function(s, v, index, array) {
                return s + v;
            }, 0);
            return numErrors === 0;
        };

        FileUploader.prototype.getCurrentFile = function() {
            if (this.state !== undefined) {
                return this.state.selection.files[this.state.fileIndex].file;
            }

            return undefined;
        };

        FileUploader.prototype.getFileReader = function() {
            var _this = this;
            var reader = new FileReader();
            var onload_success = function(data, status) {
                var file = _this.getCurrentFile();
                _this.options.uploadProgress(file, _this.state.bytesUploaded, file.size);
                if (_this.state.bytesUploaded < file.size) {
                    _this.upload();
                } else {
                    _this.endUpload();
                }
            };
            var onload_error = function(xhr, desc, err) {
                _this.options.uploadError({ kind: 'write-error', jqXHR: xhr, file: _this.getCurrentFile() });
            };
            reader.onload = function(e) {
                var uri = _this.state.sasUrl + '&comp=block&blockid=' + _this.state.blockIds[_this.state.blockIds.length - 1];
                var data = new Uint8Array(e.target.result);
                var xmsversion = _this.state.sasVersion;
                $.ajax({
                    url: uri,
                    type: 'PUT',
                    data: data,
                    processData: false,
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader('x-ms-version', xmsversion);
                        xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob');
                    },
                    success: function(data, status) {
                        onload_success(data, status);
                    },
                    error: function(xhr, desc, err) {
                        onload_error(xhr, desc, err);
                    }
                });
            };
            reader.onerror = function(e) {
                _this.options.uploadError({ kind: 'read-error', message: e.message, file: _this.getCurrentFile() });
            };
            return reader;
        };

        FileUploader.prototype.beginUpload = function(selection, index) {
            this.state = {
                sasUrl: undefined,
                sasVersion: undefined,
                trackingId: undefined,
                reader: undefined,
                selection: selection,
                fileIndex: index,
                blockIds: [],
                bytesUploaded: 0
            };
            var file = this.getCurrentFile();
            var that = this;
            $.ajax({
                url: that.options.sasEndpoint,
                type: 'POST',
                data: { 'name': file.name, 'type': file.type, 'size': file.size },
                success: function(data, status) {
                    that.state.sasUrl = data.url;
                    that.state.sasVersion = data.version;
                    that.state.trackingId = data.id;
                    that.state.reader = that.getFileReader();
                    that.options.uploadProgress(file, that.state.bytesUploaded, file.size);
                    that.upload();
                },
                error: function(xhr, desc, err) {
                    that.options.uploadError({ kind: 'sas-error', jqXHR: xhr, file: that.getCurrentFile() });
                }
            });
        };

        FileUploader.prototype.upload = function() {
            var file = this.getCurrentFile();
            var sliceStart = this.state.bytesUploaded;
            var sliceEnd = sliceStart + Math.min(file.size - sliceStart, this.options.maxBlockSizeInBytes);
            var slice = file.slice(sliceStart, sliceEnd);
            var tempId = '000000' + (this.state.blockIds.length + 1);
            var blockId = btoa(tempId.substring(tempId.length - 6));
            this.state.blockIds.push(blockId);
            this.state.bytesUploaded = sliceEnd;
            this.state.reader.readAsArrayBuffer(slice);
        };

        FileUploader.prototype.endUpload = function() {
            var uri = this.state.sasUrl + '&comp=blocklist';
            var file = this.getCurrentFile();
            var xmlLines = ['<?xml version="1.0" encoding="utf-8"?>'];
            xmlLines.push('<BlockList>');
            for (var i = 0; i < this.state.blockIds.length; i++) {
                xmlLines.push('  <Latest>' + this.state.blockIds[i] + '</Latest>');
            }
            xmlLines.push('</BlockList>');
            var that = this;
            $.ajax({
                url: uri,
                type: 'PUT',
                contentType: 'application/xml',
                processData: false,
                data: xmlLines.join('\n'),
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('x-ms-version', that.state.sasVersion);
                    xhr.setRequestHeader('x-ms-blob-content-type', file.type);
                    xhr.setRequestHeader('x-ms-meta-name', file.name);
                    xhr.setRequestHeader('x-ms-meta-size', file.size.toString());
                },
                success: function(data, status) {
                    that.options.uploadSuccess(file, that.state.trackingId);
                    var nextFileIndex = 1 + that.state.fileIndex;
                    if (nextFileIndex < that.state.selection.files.length) {
                        that.beginUpload(that.state.selection, nextFileIndex);
                    } else {
                        that.setupFileInput();
                    }
                },
                error: function(xhr, desc, err) {
                    that.options.uploadError({ kind: 'write-error', jqXHR: xhr, file: that.getCurrentFile() });
                }
            });
        };

        FileUploader.isSupported = function() {
            if (window.File && window.FileReader && window.FileList && window.Blob) {
                return true;
            }
            return false;
        };
        return FileUploader;
    })();
    CodaLab.FileUploader = FileUploader;

    (function(Competitions) {

        function CreateReady() {
            if (FileUploader.isSupported() === false) {
                $('#uploadButton').addClass('disabled');
                $('#details').html('Sorry, your browser does not support the HTML5 File API. Please use a newer browser.');
                return;
            }
            new FileUploader({
                buttonId: 'uploadButton',
                sasEndpoint: '/api/competition/create/sas',
                allowedFileTypes: ['application/zip', 'application/x-zip-compressed'],
                maxFileSizeInBytes: 1024 * 1024 * 1024,

                beforeSelection: function(info, valid) {
                    $('#uploadButton').addClass('disabled');
                },
                afterSelection: function(info, valid) {
                    if (valid === false) {
                        if (info.files.length > 0) {
                            if (info.files[0].errors[0].kind === 'type-error') {
                                $('#details').html('<div class="alert alert-error">Please select a valid file. Only ZIP files are accepted.</div>');
                            } else {
                                $('#details').html('<div class="alert alert-error">The files that you selected is too large. There is a 1GB size limit.</div>');
                            }
                        }
                        $('#uploadButton').removeClass('disabled');
                    }
                },
                uploadProgress: function(file, bytesUploaded, bytesTotal) {
                    var pct = (100 * bytesUploaded) / bytesTotal;
                    pct = pct.toFixed(0);
                    $('#details').html('<div class="alert alert-info">Uploading file <strong>' + file.name + '</strong>: ' + pct +
                        '% complete.</div><div class="progress"><div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="' +
                        pct + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + pct + '%"></div></div>');
                },
                uploadError: function(info) {
                    $('#details').html('<div class="alert alert-error">There was an error uploading the file. Please try again.</div>');
                    $('#uploadButton').removeClass('disabled');
                },
                uploadSuccess: function(file, trackingId) {
                    $('#details').html('<div class="alert alert-info alert-waiting">Creating competition... This may take a while. Please be patient.</div>');
                    $.ajax({
                        url: '/api/competition/create',
                        type: 'post',
                        cache: false,
                        data: { 'id': trackingId, 'name': file.name, 'type': file.type, 'size': file.size }
                    }).done(function(data) {
                        var wait_for_competition = function() {
                            $.ajax({
                                url: '/api/competition/create/' + data.token,
                                type: 'get',
                                cache: false,
                                data: { 'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val() }
                            }).done(function(data) {
                                if (data.status == 'finished') {
                                    $('#details').html('Congratulations! ' +
                                        "Your new competition is ready to <a href='/competitions/" + data.id + "'>view</a>. " +
                                        "You can also manage it from <a href='/my/#manage'>your CodaLab dashboard.</a>"
                                    );
                                    $('#uploadButton').removeClass('disabled');
                                } else if (data.status == 'failed') {
                                    $('#details').html('<div class="alert alert-error">Oops! There was a problem creating the competition: <br><pre>' + data.error + '</pre></div>');
                                    $('#uploadButton').removeClass('disabled');
                                } else {
                                    setTimeout(wait_for_competition, 1000);
                                }
                            }).fail(function() {
                                $('#details').html('<div class="alert alert-error">An unexpected error occurred.</div>');
                                $('#uploadButton').removeClass('disabled');
                            });
                        };
                        wait_for_competition();
                    }).fail(function() {
                        $('#details').html('<div class="alert alert-error">An unexpected error occurred.</div>');
                        $('#uploadButton').removeClass('disabled');
                    });
                }
            });

        }
        Competitions.CreateReady = CreateReady;

    })(CodaLab.Competitions || (CodaLab.Competitions = {}));
    var Competitions = CodaLab.Competitions;

})(CodaLab || (CodaLab = {}));
