<submission-form>
    <form ref="form" type="multipart/form-data">
        <div class="form-group">
            <label for="description">Description</label>
            <textarea class="form-control" ref="description" name="description"></textarea>
        </div>

        <div class="form-group">
            <input type="file" accept=".zip" onchange="{ begin_upload }" ref="file" style="display: none;">
            <button id="fileUploadButton" type="button" class="button btn btn-primary" onclick="{ select_file }">
                Submit
            </button>
        </div>
    </form>
    <!--
    <p>sas_url: { sas_url }</p>
    <p>file_id: { file_id }</p>
    -->
    <script>
        var self = this

        self.on("mount", function() {
        })

        self.select_file = function() {
            self.refs.file.click()
        }

        self.begin_upload = function() {
            // Gets a signed url to upload to
            $.post('/api/competition/' + self.opts.competition_id + '/submission/sas')
                .success(function(data) {
                    self.do_upload(data.url)


                    self.sas_url = data.url
                    self.file_id = data.id
                    self.update()
                })
                .error(function(data){
                    alert("Failed to upload submission:" + data)
                })
        }

        self.do_upload = function(url) {
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
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob')
                    xhr.setRequestHeader('Content-Name', file.name)
                    xhr.setRequestHeader('Content-Type', 'application/zip')
                }
            })
                .success(function(data){
                    console.log("SUCCESS!")
                    console.log(data)
                    self.finalize_submission(file)
                })
                .error(function(data){
                    console.log("ERROR")
                    console.log(data)
                })
        }

        self.finalize_submission = function(file) {
            // Tells the server about finished upload and any extra submission details
            //      https://competitions/api/competition/69/submission?description=&phase_id=97

            // Data:
            //      id: competition/69/submission/57/b8c6e639-d26a-42b7-aa97-95e8902f1a32.zip
            //      name: competition%2F16%2Fsubmission%2F2%2F75ff9100-c17b-472a-909f-d30dc06bfccc.zip
            //      type: application/zip
            //      size: 91
            var url = "/api/competition/" + self.opts.competition_id + "/submission?phase_id=" + self.opts.phase_id
            $.post(url, {
                id: file.name,
                name: file.name,
                type: "application/zip",
                size: file.size
            })
                .success(function(data){
                    console.log("finalize SUCCESS!")
                    console.log(data)
                })
                .error(function(data){
                    console.log("finalalize ERROR")
                    console.log(data)
                })
        }
    </script>
</submission-form>
