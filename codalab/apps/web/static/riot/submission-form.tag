<submission-form>
    <form ref="form" type="multipart/form-data">
        <input type="file" accept=".zip" onchange="{ begin_upload }" ref="file" style="display: none;">

        <div class="form-group">
            <textarea class="form-control" ref="description" name="description" placeholder="Optionally add more information about this submission"></textarea>
        </div>

        <div class="checkbox">
            <label>
                <input type="checkbox" checked="checked" ref="toc_checkbox"> I accept the <a href="https://github.com/codalab/codalab-competitions/wiki/Privacy">Terms and conditions</a>
            </label>
        </div>

        <div class="form-group" show="{ !upload_progress }">
            <button id="fileUploadButton" type="button" class="button btn btn-primary" onclick="{ select_file }">
                Submit
            </button>
        </div>
    </form>
    <div class="progress" show="{ upload_progress > 0 }" ref="progress">
        <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="{ upload_progress }" aria-valuemin="0" aria-valuemax="100" style="width: { upload_progress }%">
            <span class="sr-only">{ upload_progress }%</span>
        </div>
    </div>

    <script>
        var self = this

        /*---------------------------------------------------------------------
         Progress bar
        ---------------------------------------------------------------------*/
        /*self.show_progress_bar = function () {
            // The transition delays are for timing the animations, so they're one after the other
            self.refs.form.style.transitionDelay = '0s'
            self.refs.form.style.maxHeight = 0
            self.refs.form.style.overflow = 'hidden'

            self.refs.progress.style.transitionDelay = '1s'
            self.refs.progress.style.height = '24px'
        }

        self.hide_progress_bar = function () {
            // The transition delays are for timing the animations, so they're one after the other
            self.refs.progress.style.transitionDelay = '0s'
            self.refs.progress.style.height = 0

            self.refs.form.style.transitionDelay = '.1s'
            self.refs.form.style.maxHeight = '1000px'
            setTimeout(function () {
                // Do this after transition has been totally completed
                self.refs.form.style.overflow = 'visible'
            }, 1000)
        }*/
        self.progress_update_handler = function (progress) {
            if (self.upload_progress === undefined) {
                // First iteration of this upload, nice transitions
                //self.show_progress_bar()
            }

            self.upload_progress = progress * 100;
            //$(self.refs.progress).progress({percent: self.upload_progress})
            self.update();
        }

        /*---------------------------------------------------------------------
         File upload/form processing
        ---------------------------------------------------------------------*/
        self.select_file = function () {
            if(self.refs.toc_checkbox.checked) {
                self.refs.file.click()
            } else {
                alert("To make a submission you must accept the terms and conditions!")
            }
        }

        self.begin_upload = function () {
            // Gets a signed url to upload to
            $.post('/api/competition/' + self.opts.competition_id + '/submission/sas')
                .success(function (data) {
                    self.do_upload(data.url)


                    self.sas_url = data.url
                    self.file_id = data.id
                    self.update()
                })
                .error(function (data) {
                    alert("Failed to upload submission:" + data)
                })
        }

        self.do_upload = function (url) {
            // Do the actual file uploading
            var file = self.refs.file.files[0]
            var form_data = new FormData()
            form_data.append("file", file)

            // Sends the file to storage
            $.ajax({
                url: url,
                type: "PUT",
                processData: false,
                data: form_data,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob')
                    xhr.setRequestHeader('Content-Name', file.name)
                    xhr.setRequestHeader('Content-Type', 'application/zip')
                },
                xhr: function (xhr) {
                    var request = new window.XMLHttpRequest();
                    // Upload progress
                    request.upload.addEventListener("progress", function (event) {
                        if (event.lengthComputable) {
                            var percent_complete = event.loaded / event.total
                            self.progress_update_handler(percent_complete)
                        }
                    }, false)
                    return request
                }
            })
                .success(function (data) {
                    console.log("SUCCESS!")
                    console.log(data)
                    self.finalize_submission(file)
                })
                .error(function (data) {
                    console.log("ERROR")
                    console.log(data)
                    //self.hide_progress_bar()
                })
        }

        self.finalize_submission = function (file) {

            // Tells the server about finished upload and any extra submission details
            //      https://competitions/api/competition/69/submission?description=&phase_id=97

            // Data:
            //      id: competition/69/submission/57/b8c6e639-d26a-42b7-aa97-95e8902f1a32.zip
            //      name: competition%2F16%2Fsubmission%2F2%2F75ff9100-c17b-472a-909f-d30dc06bfccc.zip
            //      type: application/zip
            //      size: 91
            var url = "/api/competition/" + self.opts.competition_id + "/submission?description=" + self.refs.description.value + "&phase_id=" + self.opts.phase_id

            // Reset the form so we can get another input file changed event
            self.refs.form.reset()

            $.post(url, {
                id: file.name,
                name: file.name,
                type: "application/zip",
                size: file.size
            })
                .success(function (data) {
                    console.log("finalize SUCCESS!")
                    console.log(data)
                })
                .error(function (data) {
                    console.log("finalalize ERROR")
                    console.log(data)
                })
                .always(function() {
                    self.upload_progress = 0
                    self.update()
                    //self.hide_progress_bar()
                })
        }
    </script>
</submission-form>
