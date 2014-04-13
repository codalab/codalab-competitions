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
                    if (_this.options.allowedFileTypes && ($.inArray(file.type, _this.options.allowedFileTypes)) === -1) {
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
