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
                    $('#user_results button.leaderBoardRemove').each(function(index) {
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
                            var description = $('#submission_description_textarea').val();
                            var method_name = $('#submission_method_name').val();
                            var method_description = $('#submission_method_description').val();
                            var project_url = $('#submission_project_url').val();
                            var publication_url = $('#submission_publication_url').val();
                            var bibtex = $('#submission_bibtex').val();

                            $('#submission_description_textarea').val('');
                            $.ajax({
                                url: '/api/competition/' + competitionId + '/submission?description=' + encodeURIComponent(description) +
                                                                                      '&method_name=' + encodeURIComponent(method_name) +
                                                                                      '&method_description=' + encodeURIComponent(method_description) +
                                                                                      '&project_url=' + encodeURIComponent(project_url) +
                                                                                      '&publication_url=' + encodeURIComponent(publication_url) +
                                                                                      '&bibtex=' + encodeURIComponent(bibtex),
                                type: 'post',
                                cache: false,
                                data: { 'id': trackingId, 'name': file.name, 'type': file.type, 'size': file.size }
                            }).done(function(response) {
                                $('#details').html('');
                                $('#user_results tr.noData').remove();
                                $('#user_results').append(Competition.displayNewSubmission(response, description, method_name, method_description, project_url, publication_url, bibtex));
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

    Competition.displayNewSubmission = function(response, description, method_name, method_description, project_url, publication_url, bibtex) {
        var elemTr = $('#submission_details_template #submission_row_template tr').clone();
        $(elemTr).attr('id', response.id.toString());
        $(elemTr).addClass(Competition.oddOrEven(response.submission_number));

        if (description) {
            $(elemTr).attr('data-description', $(description).text());
        }
        if (method_name) {
            $(elemTr).attr('data-method-name', $(method_name).text());
        }
        if (method_description) {
            $(elemTr).attr('data-method-description', $(method_description).text());
        }
        if (project_url) {
            $(elemTr).attr('data-project-url', $(project_url).text());
        }
        if (publication_url) {
            $(elemTr).attr('data-publication-url', $(publication_url).text());
        }
        if (bibtex) {
            $(elemTr).attr('data-bibtex', $(bibtex).text());
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
                    var d = dt.getDate().toString() + '/' + dt.getMonth().toString() + '/' + dt.getFullYear();
                    var h = dt.getHours().toString();
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
            if ($(nTr).attr('data-description')) {
                elem.find('.submission_description').html('<b>Description:</b> <br><pre>' + $(nTr).attr('data-description') + '</pre>');
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
            if ($(nTr).attr('data-exception')) {
                elem.find('.traceback').html('Error: <br><pre>' + $(nTr).attr('data-exception') + '</pre>');
            }
            var phasestate = $('#phasestate').val();
            var state = $(nTr).find("input[name='state']").val();
            if ((phasestate == 1) && (state == 1)) {
                var btn = elem.find('button');
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
                var btn = elem.find('button').addClass('hide');
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
