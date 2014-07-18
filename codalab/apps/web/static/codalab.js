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
﻿var BundleContentNode = (function() {
    function BundleContentNode(url, name, parent, children) {
        this.url = url;
        this.name = name;
        this.parent = parent;
        this.children = children;
    }
    BundleContentNode.prototype.isRootNode = function() {
        return this.parent === undefined;
    };
    BundleContentNode.prototype.isLeafNode = function() {
        return this.children === null;
    };
    BundleContentNode.prototype.getUrl = function() {
        return this.url;
    };
    BundleContentNode.prototype.getName = function() {
        return this.name;
    };
    BundleContentNode.prototype.getFullName = function() {
        if (this.isRootNode()) {
            return this.name;
        }
        return [this.parent.getFullName(), this.name].join('/');
    };
    BundleContentNode.prototype.getParent = function() {
        return this.parent;
    };
    BundleContentNode.prototype.getChildren = function() {
        return this.children;
    };
    BundleContentNode.prototype.setChildren = function(children) {
        this.children = children;
    };
    BundleContentNode.prototype.getData = function() {
        return this.data;
    };
    BundleContentNode.prototype.setData = function(data) {
        this.data = data;
    };
    return BundleContentNode;
})();

var BundleRenderer = (function() {
    function BundleRenderer(element) {
        this.template = element;
    }
    BundleRenderer.loadContentAsync = function(container, parent) {
        console.log('loadContentAsync');
        $.ajax({
            type: 'GET',
            url: [parent.getUrl(), parent.getFullName()].join('/'),
            cache: false,
            success: function(data) {
                console.log(data);
                console.log('');
                var children = [];
                if (Array.isArray(data) && data.length == 2) {
                    var set1 = data[0].map(function(item) {
                        return new BundleContentNode(parent.getUrl(), item, parent);
                    });
                    var set2 = data[1].map(function(item) {
                        return new BundleContentNode(parent.getUrl(), item, parent, null);
                    });
                    children = set1.concat(set2).sort(function(a, b) {
                        return a.getName().localeCompare(b.getName());
                    });
                }
                parent.setChildren(children);
                BundleRenderer.renderTable(container, BundleRenderer.getContentTableModel(parent, container));
            },
            error: function(xhr, status, err) {
            }
        });
    };

    BundleRenderer.loadFileContentAsync = function(container, node) {
        console.log('loadFileContentAsync');
        $.ajax({
            type: 'GET',
            url: [node.getUrl().replace('api/bundles/content', 'api/bundles/filecontent'), node.getFullName()].join('/'),
            cache: false,
            success: function(data) {
                console.log(data);
                console.log('');
                node.setData(data);
                BundleRenderer.renderTable(container, BundleRenderer.getContentTableModel(node, container));
            },
            error: function(xhr, status, err) {
            }
        });
    };

    BundleRenderer.getContentTableModel = function(node, container) {
        var numRows = 0;
        if (node.isRootNode() === false) {
            numRows += 1;
        }
        if (node.isLeafNode()) {
            numRows += 1;
        } else {
            var children = node.getChildren();
            if (children !== undefined) {
                numRows += children.length;
            }
        }

        var renderHeaderKey = function(element) {
            element.setAttribute('class', 'col bundle__file_view__icon');
            var innerElement = document.createElement('i');
            innerElement.setAttribute('class', 'fi-arrow-left');
            element.appendChild(innerElement);
            innerElement.onclick = function(e) {
                BundleRenderer.loadContentAsync(container, node.getParent());
                e.preventDefault();
            };
        };
        var renderHeaderValue = function(element) {
            element.setAttribute('class', 'col bundle-item-type-goup');

            var parents = [];
            var parent = node.getParent();
            while (parent !== undefined) {
                parents.push(parent);
                parent = parent.getParent();
            }
            parents.reverse().forEach(function(p) {
                var link = document.createElement('a');
                link.textContent = p.getName();
                link.setAttribute('href', '');
                link.onclick = function(e) {
                    BundleRenderer.loadContentAsync(container, p);
                    e.preventDefault();
                };
                element.appendChild(link);
                element.appendChild(document.createTextNode(' / '));
            });
            element.appendChild(document.createTextNode(node.getName()));
        };
        var renderKey = function(element, child) {
            element.setAttribute('class', 'col bundle__file_view__icon');
            var e = document.createElement('i');
            if (child !== undefined) {
                e.setAttribute('class', child.isLeafNode() ? 'fi-page' : 'fi-folder');
            }
            element.appendChild(e);
        };
        var renderValue = function(element, child) {
            if (child.isLeafNode()) {
                element.setAttribute('class', 'col');
                var link = document.createElement('a');
                link.textContent = child.getName();
                link.setAttribute('href', '');
                link.onclick = function(e) {
                    BundleRenderer.loadFileContentAsync(container, child);
                    e.preventDefault();
                };
                element.appendChild(link);
            } else {
                element.setAttribute('class', 'col bundle-item-type-folder');
                var link = document.createElement('a');
                link.textContent = child.getName();
                link.setAttribute('href', '');
                link.onclick = function(e) {
                    BundleRenderer.loadContentAsync(container, child);
                    e.preventDefault();
                };
                element.appendChild(link);
            }
        };
        var renderTextContent = function(element, node) {
            var block = document.createElement('pre');
            block.setAttribute('class', 'bundle__file_pre');
            block.textContent = node.getData();
            return [block];
        };
        var renderImageContent = function(element, node) {
            var img = document.createElement('img');
            var url = [node.getUrl().replace('api/bundles/content', 'api/bundles/filecontent'), node.getFullName()].join('/');
            img.setAttribute('src', url);
            img.setAttribute('style', 'max-width:900px');
            return [img];
        };
        var renderHtmlContent = function(element, node) {
            var iframe = document.createElement('iframe');
            var url = [node.getUrl().replace('api/bundles/content', 'api/bundles/filecontent'), node.getFullName()].join('/');
            iframe.setAttribute('src', url);
            iframe.setAttribute('style', 'width:100%; min-height:' + Math.max(200, Math.min(900, screen.height / 2)) + 'px;');
            return [iframe];
        };
        var render_methods = {
            'txt': renderTextContent,
            'htm': renderHtmlContent,
            'html': renderHtmlContent,
            'jpg': renderImageContent,
            'png': renderImageContent
    };
        var renderContentValue = function(element, node) {
            var fname = node.getName();
            var ext = '';
            if (fname.indexOf('.') > 0) {
                ext = fname.toLowerCase().split('.').pop();
            }
            var method = render_methods[ext];
            if (method === undefined) {
                method = render_methods['txt'];
            }
            element.setAttribute('class', 'col');
            method(element, node).forEach(function(e) { element.appendChild(e); });
        };

        return {
            tableDecorations: 'bundle__file_view expanded',
            rowDecorations: 'row',
            numRows: numRows,
            numCols: 2,
            render: function(row, col, td) {
                if ((node.isRootNode() === false) && (row <= 0)) {
                    if (col == 0) {
                        renderHeaderKey(td);
                    } else {
                        renderHeaderValue(td);
                    }
                    return;
                }

                if (node.isLeafNode() === true) {
                    if (col == 0) {
                        renderKey(td);
                    } else {
                        renderContentValue(td, node);
                    }
                } else {
                    var offset = 0;
                    if (node.isRootNode() === false) {
                        offset = 1;
                    }
                    var children = node.getChildren();
                    var child = children[row - offset];
                    if (col == 0) {
                        renderKey(td, child);
                    } else {
                        renderValue(td, child);
                    }
                }
            }
        };
    };

    BundleRenderer.getMetadataTableModel = function(data) {
        var rows = [];
        for (var k in data.metadata) {
            console.log(k);
            if(k == "description"){
                rows.push([k, data.metadata[k]]);
            }
            // if (k !== 'name') {
            //     rows.push([k, data.metadata[k]]);
            // }
        }

        var renderKey = function(element, row, col) {
            element.setAttribute('class', 'col bundle__meta_type');
            element.textContent = rows[row][col];
        };
        var renderValue = function(element, row, col) {
            element.setAttribute('class', 'col');
            element.textContent = rows[row][col];
        };

        return {
            tableDecorations: 'bundle__meta_table',
            rowDecorations: 'row',
            numRows: rows.length,
            numCols: 2,
            render: function(row, col, td) {
                if (col == 0) {
                    renderKey(td, row, col);
                } else {
                    renderValue(td, row, col);
                }
            }
        };
    };

    BundleRenderer.getElementType = function(value, defaultValue) {
        if (value !== undefined) {
            return value;
        }
        return defaultValue;
    };

    BundleRenderer.renderTable = function(container, model) {
        var tableElementType = BundleRenderer.getElementType(model.tableElementType, 'table');
        var rowElementType = BundleRenderer.getElementType(model.rowElementType, 'tr');
        var columnElementType = BundleRenderer.getElementType(model.columnElementType, 'td');
        var table = document.createElement(tableElementType);
        if (model.tableDecorations !== undefined) {
            table.setAttribute('class', model.tableDecorations);
        }
        for (var ir = 0; ir < model.numRows; ir++) {
            var tr = document.createElement(rowElementType);
            if (model.numCols > 0) {
                for (var ic = 0; ic < model.numCols; ic++) {
                    var td = document.createElement(columnElementType);
                    model.render(ir, ic, td);
                    tr.appendChild(td);
                }
            } else {
                model.render(ir, tr);
            }
            table.appendChild(tr);
        }
        if (container.firstChild != undefined) {
            container.removeChild(container.firstChild);
        }
        container.appendChild(table);
    };

    BundleRenderer.prototype.render = function(data) {
        var clone = $(this.template.cloneNode(true));

        clone.find('.bundle-name').text(data.metadata.name);
        clone.find('.bundle-icon-sm')
            .removeClass('bundle-icon-sm')
            .addClass('bundle-icon-sm--' + data.bundle_type + '--' + data.state);
        clone.find('.bundle-uuid').text(data.uuid);
        clone.find('.bundle-link').attr('href', '/bundles/' + data.uuid);
        clone.find('.bundle-download').on('click', function(e) {
            // alert('This will allow you to download the bundle TODO');
            e.preventDefault();
            console.log(e);
            console.log(container.get(0));
            root = new BundleContentNode('/api/bundles/content', data.uuid);
            console.log(root);


        });
        var metaContainer = clone.find('.bundle-meta-view-container').get(0);
        BundleRenderer.renderTable(metaContainer, BundleRenderer.getMetadataTableModel(data));

        var toggle = clone.find('.bundle__expand_button');
        var container = clone.find('.bundle-file-view-container');
        toggle.on('click', function(e) {
            var button = $(e.target);
            if (button.hasClass('expanded')) {
                container.removeClass('expanded');
                container.children().removeClass('expanded');
                button.removeClass('expanded');
                button.html('SHOW BUNDLE CONTENT<img src="/static/img/expand-arrow.png" alt="More">');
            } else {
                if (container.get(0).firstChild == undefined) {
                    var root = new BundleContentNode('/api/bundles/content', data.uuid);
                    BundleRenderer.loadContentAsync(container.get(0), root);
                } else {
                    container.children().addClass('expanded');
                }
                container.addClass('expanded');
                button.addClass('expanded');
                button.html('HIDE BUNDLE CONTENT<img src="/static/img/expand-arrow.png" alt="Less">');
            }
            e.preventDefault();
        });

        return clone.get(0);
    };
    return BundleRenderer;
})();

var WorkshhetDirectiveRenderer = (function() {
    function WorkshhetDirectiveRenderer() {
        var _this = this;
        _this.display = 'inline';

        _this.bundleBlock = null;

        _this.tableDirective = [];

        _this.applyDirective = function(element, item) {
            switch (item[1].directive) {
                case 'display': {
                    _this.display = item[1].display;
                    _this.applyPendingDirectives(element);
                    break;
                }
                case 'image': {
                    $(element).append(
                        $('<img />', {
                            'src': '/api/bundles/filecontent/' + _this.bundleBlock.uuid + '/' + encodeURI(item[1].path),
                            'class': 'bundleImage',
                            'alt': item[1].name
                        }));
                    break;
                }
                case 'metadata': {
                    _this.tableDirective.push(item[1]);
                    break;
                }
            }
        };

        _this.insertRowTable = function(element, data, cell) {
            var headerRow = $('<tr></tr>');
            data.forEach(function(datum) {
                headerRow.append($(cell).text(datum));
            });
            element.append(headerRow);
        };

        _this.getDataFromPath = function(path) {
            return _this.bundleBlock.metadata[path];
        };

        _this.applyPendingDirectives = function(element) {
            if (_this.tableDirective.length > 0) {
                var table = $('<table></table>');

                if (_this.display === 'table') {
                    var thead = $('<thead></thead>');
                    _this.insertRowTable(thead, _this.tableDirective.map(function(e) {
                        return e.name;
                    }), '<th></th>');
                }

                var tbody = $('<tbody></tbody>');
                if (_this.display === 'table') {
                    _this.insertRowTable(tbody, _this.tableDirective.map(function(e) {
                        return _this.getDataFromPath(e.path);
                    }), '<td></td>');
                }
                else {
                    _this.tableDirective.forEach(function(e) {
                        _this.insertRowTable(tbody, [e.name, _this.getDataFromPath(e.path)], '<td></td>');
                    });
                }

                table.append(thead);
                table.append(tbody);
                $(element).append(table);

                _this.tableDirective = [];
            }
        };
    }
    return WorkshhetDirectiveRenderer;
})();

var WorksheetRenderer = (function() {
    function WorksheetRenderer(element, renderer, data) {
        this.renderer = renderer;
        if (data && data.items && Array.isArray(data.items)) {
            var _this = this;
            var title = data.name;
            var title_items = data.items.filter(function(item) { return item[2] === 'title' });
            if (title_items.length > 0) {
                title = markdown.toHTML('#' + title_items[0][1]).replace(/^<h1>/, '').replace(/<\/h1>$/, '');
            }
            $('.worksheet-icon').html(title);
            $('.worksheet-author').html('by ' + data.owner);
            var directiveRenderer = new WorkshhetDirectiveRenderer();
            var markdownBlock = '';
            // Add an EOF block to ensure the block transitions always apply within the loop
            data.items.push([null, 'eof', null]);
            var blocks = data.items.forEach(function(item, idxItem, items) {
                // Apply directives when the markdown item type changes
                if (item[2] != 'directive')
                    directiveRenderer.applyPendingDirectives(element);

                if (item[2] != 'markup' && markdownBlock.length > 0) {
                    var e = document.createElement('div');
                    e.innerHTML = markdown.toHTML(markdownBlock);
                    element.appendChild(e);
                    markdownBlock = '';
                }
                switch (item[2]) {
                    case 'markup': {
                        markdownBlock += item[1] + '\n\r';
                        break;
                    }
                    case 'bundle': {

                        // Only display bundle if its not empty, this allows ability to hide bundles.
                        // if (item[1]) {
                            element.appendChild(_this.renderer.render(item[0]));
                        // }
                        break;
                    }
                    case 'directive': {
                        // Find bundle ID context
                        items.slice(idxItem + 1).forEach(function(bundleCandidate) {
                            if (bundleCandidate[2] == 'bundle') directiveRenderer.bundleBlock = bundleCandidate[0];
                        });
                        directiveRenderer.applyDirective(element, item);
                        break;
                    }
                }
            });

            MathJax.Hub.Queue(['Typeset', MathJax.Hub, element.id]);
            MathJax.Hub.Queue(function() {
                var all = MathJax.Hub.getAllJax();
                for (var i = 0; i < all.length; i += 1) {
                    $(all[i].SourceElement().parentNode).addClass('coda-jax');
                }
            });
        }
    }
    return WorksheetRenderer;
})();
var Competition;
(function(Competition) {

    Competition.invokePhaseButtonOnOpen = function(id) {
        var btn = $('#' + id + ' .button.selected')[0];
        if (btn === undefined) {
            btn = $('#' + id + ' .button.active')[0];
            if (btn === undefined) {
                btn = $('#' + id + ' .button')[0];
            }
        }
        btn.click();
    };

    function decorateLeaderboardButton(btn, submitted) {
        var force_submission_to_leaderboard = btn.attr('force_submission_to_leaderboard');

        if (force_submission_to_leaderboard) {
            if (submitted) {
                btn.text('Automatically submitted to leaderboard').attr('disabled', 'disabled');
            }
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
        var op = 'delete';
        if (btn.hasClass('leaderBoardSubmit')) {
            op = 'post';
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
                    row.html("<i class='fi-check'></i>");
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
                            $.ajax({
                                url: '/api/competition/' + competitionId + '/submission',
                                type: 'post',
                                cache: false,
                                data: { 'id': trackingId, 'name': file.name, 'type': file.type, 'size': file.size }
                            }).done(function(response) {
                                $('#details').html('');
                                $('#user_results tr.noData').remove();
                                $('#user_results').append(Competition.displayNewSubmission(response));
                                $('#user_results #' + response.id + ' .fi-plus').on('click', function() { Competition.showOrHideSubmissionDetails(this) });
                                $('#fileUploadButton').removeClass('disabled');
                                //$('#fileUploadButton').text("Submit Results...");
                                $('#user_results #' + response.id + ' .fi-plus').click();
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
                $('#user_results .fi-plus').on('click', function() {
                    Competition.showOrHideSubmissionDetails(this);
                });
            },
            error: function(xhr, status, err) {
                $('.competition_submissions').html("<div class='alert-error'>An error occurred. Please try refreshing the page.</div>");
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
                $('.competition_results').html("<div class='alert-error'>An error occurred. Please try refreshing the page.</div>");
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

    Competition.displayNewSubmission = function(response) {
        var elemTr = $('#submission_details_template #submission_row_template tr').clone();
        $(elemTr).attr('id', response.id.toString());
        $(elemTr).addClass(Competition.oddOrEven(response.submission_number));
        $(elemTr).children().each(function(index) {
            switch (index) {
                case 0: if (response.status === 'finished') { $(this).val('1'); } break;
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
                    var d = dt.getDate().toString() + "/" + dt.getMonth().toString() + "/" + dt.getFullYear();
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
        if ($(obj).hasClass('fi-minus')) {
            $(obj).removeClass('fi-minus');
            $(obj).addClass('fi-plus');
            $(nTr).next('tr.trDetails').remove();
        }
        else {
            $(obj).removeClass('fi-plus');
            $(obj).addClass('fi-minus');
            var elem = $('#submission_details_template .trDetails').clone();
            elem.find('.tdDetails').attr('colspan', nTr.cells.length);
            elem.find('a').each(function(i) { $(this).attr('href', $(this).attr('href').replace('_', nTr.id)) });
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
                        var force_submission_to_leaderboard = $(obj).attr('force_submission_to_leaderboard');

                        if (!force_submission_to_leaderboard) {
                            $(obj).addClass('leaderBoardSubmit');
                            $(obj).text('Submit to Leaderboard');
                            $(obj).on('click', function() {
                                updateLeaderboard(competitionId, submissionId, $('#cstoken').val(), $(obj));
                            });
                        } else {
                            $(obj).text('Automatically submitted to leaderboard').attr('disabled', 'disabled');
                        }
                    } else {
                        $(obj).addClass('hide');
                    }
                }
                else if (data.status === 'failed' || data.status === 'cancelled') {
                    $(obj).addClass('hide');
                    $(obj).parent().parent().find('a').removeClass('hide');
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

            $('#submissions_phase_buttons .button').each(function(e, index) {
                $(this).click(function() {
                    var phaseId = $.trim($(this).attr('id').replace('submissions_phase_', ''));
                    $('#submissions_phase_buttons .button').removeClass('selected');
                    $(this).addClass('selected');
                    var competitionId = $('#competitionId').val();
                    var cstoken = $('#cstoken').val();
                    Competition.getPhaseSubmissions(competitionId, phaseId, cstoken);
                });
            });

            $("a[href='#participate-submit_results']").click(function(obj) {
                Competition.invokePhaseButtonOnOpen('submissions_phase_buttons');
            });

            $('#results_phase_buttons .button').each(function(e, index) {
                $(this).click(function() {
                    var phaseId = $.trim($(this).attr('id').replace('results_phase_', ''));
                    $('#results_phase_buttons .button').removeClass('selected');
                    $(this).addClass('selected');
                    var competitionId = $('#competitionId').val();
                    Competition.getPhaseResults(competitionId, phaseId);
                });
            });

            $('#Results').click(function(obj) {
                Competition.invokePhaseButtonOnOpen('results_phase_buttons');
            });

            // This helps make sections appear with Foundation
            $(this).foundation('section', 'reflow');

            $('.top-bar-section ul > li').removeClass('active');
            $('#liCompetitions').addClass('active');

            $('.my_managing .competition-tile #competition-actions').each(function(e, index) {

                $(this).children('#competition-publish-button').click(function() {
                    var competition_actions = $(this).parent()[0];
                    request = $.ajax({
                        url: $(this)[0].value,
                        success: function(response, textStatus, jqXHR) {
                            console.log('Published competition.');
                            $(competition_actions).children('#competition-publish-button').hide();
                            $(competition_actions).children('#competition-delete-button').hide();
                            $(competition_actions).children('#competition-unpublish-button').show();
                        },
                        error: function(jsXHR, textStatus, errorThrown) {
                            console.log('Error publishing competition!');
                        }
                    });
                });

                $(this).children('#competition-unpublish-button').click(function() {
                    // This shows how unpublishing a competition works. We have this commented out
                    // because we don't want competition owners to inadvertantly unpublish, then delete
                    // competitions that have submissions and results.
                    // If this decision is changed in the future simply uncommenting this code will enable
                    // competitions to be unpublished.
                    // Only unpublished competitions are able to be deleted.
                    //var competition_actions = $(this).parent()[0];
                    //request = $.ajax({
                    //    url: $(this)[0].value,
                    //    success: function(response, textStatus, jqXHR) {
                    //        console.log('Unpublished competition.');
                    //        $(competition_actions).children('#competition-publish-button').show();
                    //        $(competition_actions).children('#competition-delete-button').show();
                    //        $(competition_actions).children('#competition-unpublish-button').hide()
                    //    },
                    //    error: function(jsXHR, textStatus, errorThrown) {
                    //        console.log('Error unpublishing competition!');
                    //    }
                    //});
                });

                if ($(this)[0].getAttribute('published') == 'True') {
                    $(this).children('#competition-delete-button').hide();
                    $(this).children('#competition-publish-button').hide();
                    $(this).children('#competition-unpublish-button').show();
                } else {
                    $(this).children('#competition-delete-button').show();
                    $(this).children('#competition-publish-button').show();
                    $(this).children('#competition-unpublish-button').hide();
                }
            });

            var loc = window.location.href;
            if (loc !== undefined) {
                if (loc.match(/#participate-submit_results$/i) !== null) {
                    Competition.invokePhaseButtonOnOpen('submissions_phase_buttons');
                } else if (loc.match(/#results$/i) !== null) {
                    Competition.invokePhaseButtonOnOpen('results_phase_buttons');
                }
            }
        });
    };
})(Competition || (Competition = {}));
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
                    _this.fileInput.click();
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
                                $('#details').html('Please select a valid file. Only ZIP files are accepted.');
                            } else {
                                $('#details').html('The files that you selected is too large. There is a 1GB size limit.');
                            }
                        }
                        $('#uploadButton').removeClass('disabled');
                    }
                },
                uploadProgress: function(file, bytesUploaded, bytesTotal) {
                    var pct = (100 * bytesUploaded) / bytesTotal;
                    $('#details').html('Uploading file <em>' + file.name + '</em>: ' + pct.toFixed(0) + '% complete.');
                },
                uploadError: function(info) {
                    $('#details').html('There was an error uploading the file. Please try again.');
                    $('#uploadButton').removeClass('disabled');
                },
                uploadSuccess: function(file, trackingId) {
                    $('#details').html('Creating competition... This may take a while. Please be patient.');
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
                                    $('#details').html('Oops! There was a problem creating the competition.');
                                    $('#uploadButton').removeClass('disabled');
                                } else {
                                    setTimeout(wait_for_competition, 1000);
                                }
                            }).fail(function() {
                                $('#details').html('An unexpected error occurred.');
                                $('#uploadButton').removeClass('disabled');
                            });
                        };
                        wait_for_competition();
                    }).fail(function() {
                        $('#details').html('An unexpected error occurred.');
                        $('#uploadButton').removeClass('disabled');
                    });
                }
            });

        }
        Competitions.CreateReady = CreateReady;

    })(CodaLab.Competitions || (CodaLab.Competitions = {}));
    var Competitions = CodaLab.Competitions;

})(CodaLab || (CodaLab = {}));
﻿'use strict';

angular.module('codalab.services', []);
angular.module('codalab.controllers', []);
angular.module('codalab.directives', []);

angular
    .module('codalab', [
        'ngRoute',
        'ngAnimate',
        'codalab.controllers',
        'codalab.services',
        'codalab.directives'
    ])
    .factory('$exceptionHandler', function() {
        return function(exception) {
            console.error(exception.message);
            error(exception);
        };
    })
    .config(['$routeProvider', '$locationProvider', '$httpProvider', '$interpolateProvider', function($routeProvider, $locationProvider, $httpProvider, $interpolateProvider) {
        $routeProvider
            .when('/worksheets/app/:uuid/', {
                templateUrl: '/static/app/partials/worksheet.html',
                controller: 'worksheet'
            })
            .when('/my', {
                templateUrl: '/static/app/partials/myworksheets.html',
                controller: 'worksheets'
            })
            .otherwise({
                templateUrl: '/static/app/partials/worksheets.html',
                controller: 'worksheets'
            });

        $locationProvider.html5Mode(true);

        // Since HTML static files are served through Django, avoid using their templating arguments
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
    }]);
﻿'use strict';

angular.module('codalab.services')
    .factory('worksheetsApi', ['$http', function($http) {
        var success = function(result, status, headers, config) {
            return result.data;
        };
        var failure = function(result, status, headers, config) {
            throw result;
        };
        var apiCall = function(url) {
            return function() {
                // Prevent some browsers from caching requests by adding a preventCache parameter.
                return $http.get(url + '?preventCache=' + Math.floor(Math.random() * 1000)).then(success, failure);
            }
        };
        var apiPostCall = function(url) {
            return function(data) {
                // For CSRF + DJango see: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
                var csrftoken = $.cookie('csrftoken');
                if (!csrfSafeMethod('POST') && sameOrigin(url)) {
                    $http.defaults.headers.common['X-CSRFToken'] = csrftoken;
                }

                return $http.post(url, data).then(success, failure);
            }
        };
        var factory = {
            info: apiCall('/api/worksheets/info/'),
            worksheets: apiCall('/api/worksheets/'),
            createWorksheet: apiPostCall('/api/worksheets/')
        };
        return factory;
    }]);
﻿'use strict';

angular.module('codalab.controllers')
    .controller('root', ['$scope', 'worksheetsApi', function($scope, worksheetsApi) {
        worksheetsApi.info().then(function(info) {
            $scope.config = info.config;
            $scope.user = info.user;
        });
    }]);
﻿'use strict';

angular.module('codalab.controllers')
    .controller('worksheets', ['$scope', '$location', 'worksheetsApi', function($scope, $location, worksheetsApi) {
        $scope.status = 'loading';
        $scope.selectionIndex = 0;
        $scope.worksheets = [];

        $scope.statusMessage = function(status) {
            var messages = {
                '': '',
                'loading': 'Loading worksheets...',
                'loaderror': 'Couldn\'t retrieve worksheets - Try refreshing the page',
                'empty': 'There are no worksheets.',
                'saving': 'Saving',
                'saveerror': 'Couldn\'t save - Try a different name'
            };
            switch (status) {
                case 'loaded':
                    return $scope.worksheets.length > 0 ? '' : messages['empty'];
            }
            return messages[status];
        };

        $scope.hasStatus = function(status) {
            return status && status.length > 0;
        };

        worksheetsApi.worksheets().then(function(worksheets) {
            $scope.status = 'loaded';
            if ($location.path().indexOf('/my') === 0) {
                worksheets = worksheets.filter(function(w) { return w.owner === $scope.user.name; });
            }
            angular.forEach(worksheets, function(worksheet) {
                worksheet.url = '/worksheets/' + worksheet.uuid;
                worksheet.target = '_self';
                worksheet.editable = false;
                var items = worksheet.items.filter(function(item) { return item.type == 'title' });
                if (items.length > 0) {
                    worksheet.title = items[0].value;
                } else {
                    worksheet.title = worksheet.name;
                }
                items = worksheet.items.filter(function(item) { return item.type == 'description' });
                if (items.length > 0) {
                    items.forEach(function(item) {
                        worksheet.description = item.value + '\n';
                    });
                }
                $scope.worksheets.push(worksheet);
            });
        }, function() {
            $scope.status = 'loaderror';
        });

        $scope.saveWorksheet = function(worksheet) {
            worksheet.status = 'saving';
            worksheetsApi.createWorksheet(worksheet).then(function(createdWorksheet) {
                worksheet.name = createdWorksheet.name;
                worksheet.title = createdWorksheet.name;
                worksheet.uuid = createdWorksheet.uuid;
                worksheet.owner = createdWorksheet.owner;
                worksheet.url = '/worksheets/' + worksheet.uuid;
                worksheet.editable = false;
                worksheet.target = '_self';
            }, function() {
                worksheet.status = 'saveerror';
            });
        };

        $scope.worksheetEnabled = function(worksheet) {
            return worksheet.name.length > 0;
        };

        $scope.addWorksheet = function(index, insertBellow) {
            $scope.selectionIndex = index + (insertBellow ? 1 : 0);
            $scope.worksheets.splice($scope.selectionIndex, 0, {
                'name': '',
                'editable': true,
                'url': '#',
                'owner': $scope.user.name
            });
        };

        $scope.keyPressed = function(e) {
            if (e.ctrlKey) {
                switch (e.keyCode) {
                    case 38:
                    case 40: {
                        if ($scope.user.authenticated) {
                            var insertBellow = (e.keyCode === 40);
                            $scope.addWorksheet($scope.selectionIndex, insertBellow);
                            e.preventDefault();
                        }
                        break;
                    }
                }
            }
            else {
                switch (e.keyCode) {
                    // Move Up
                    case 38:
                        if ($scope.selectionIndex > 0) $scope.selectionIndex -= 1;
                        else $scope.selectionIndex = 0;
                        e.preventDefault();
                        break;
                    // Move Down
                    case 40:
                        if ($scope.selectionIndex < $scope.worksheets.length - 1) $scope.selectionIndex += 1;
                        else $scope.selectionIndex = $scope.worksheets.length - 1;
                        e.preventDefault();
                        break;
                }
            }
        };

        $scope.gotFocus = function(index) {
            $scope.selectionIndex = index;
        };

        $scope.lostFocus = function(index) {
            if ($scope.selectionIndex === index)
                $scope.selectionIndex = ($scope.selectionIndex === $scope.worksheets.length - 1) ? $scope.selectionIndex = $scope.worksheets.length : -1;
        };
    }]);
﻿'use strict';

angular.module('codalab.controllers')
    .controller('worksheet', ['$scope', 'worksheetsApi', function($scope, worksheetsApi) {
        $scope.status = 'Loading worksheet...';
    }]);
﻿'use strict';

angular.module('codalab.directives')
    .directive('shortcut', function() {
        return {
            restrict: 'E',
            replace: true,
            scope: true,
            link: function postLink($scope, iElement, iAttrs) {
                var keyHandler = function(e) {
                    $scope.$apply($scope.keyPressed(e));
                };
                $(document).on('keydown', keyHandler);
                $scope.$on('$destroy', function() {
                    $(document).off('keydown', keyHandler);
                });
            }
        };
    });
﻿'use strict';

angular.module('codalab.directives')
    .directive('setFocus', ['$timeout', function($timeout) {
        return {
            scope: {
                trigger: '@setFocus'
            },
            restrict: 'A',
            link: function($scope, element, attrs) {
                attrs.$observe('setFocus', function(value) {
                    if (value === 'true' && document.activeElement != element) {
                        $timeout(function() {
                            if ($scope.trigger === 'true') {
                                element[0].focus();
                                $scope.trigger = false;
                            }
                        });
                    }
                });
            }
        };
    }]);
﻿'use strict';

angular.module('codalab.directives')
    .directive('scrollIntoView', ['$timeout', function($timeout) {
        return {
            scope: {
                trigger: '@scrollIntoView'
            },
            restrict: 'A',
            link: function($scope, element, attrs) {
                attrs.$observe('scrollIntoView', function(value, oldvalue) {
                    if (value === 'true' && value !== oldvalue) {
                        $timeout(function() {
                            if ($scope.trigger === 'true') {
                                element[0].scrollIntoView();
                                $scope.trigger = false;
                            }
                        });
                    }
                });
            }
        };
    }]);
