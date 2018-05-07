<reports>
    <p show={ last_update }>Last update: { last_update }</p>

    <button class="ui button positive" onclick={ update_report }>Force update</button>

    <table ref="table" class="ui selectable striped table">
        <thead>
            <tr>
                <th>id</th>
                <th>Submitter name</th>
                <th>Zip name</th>
                <th>Size of zip</th>
                <th>Compute worker used</th>
                <th>Queue used</th>
                <th>Score</th>
                <th>Total time taken</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <tr each={ submission in submissions } class="{ error: submission['Status'] == 'failed' }">
                <td>{ submission["id"] }</td>
                <td>{ submission["Submitter name"] }</td>
                <td>{ submission["Zip name"] }</td>
                <td>{ submission["Size of zip"] }</td>
                <td>{ submission["Compute worker used"] }</td>
                <td>{ submission["Queue used"] }</td>
                <td>{ submission["Score"] }</td>
                <td>{ submission["Total time taken"] }</td>
                <td>{ submission["Status"] }</td>
            </tr>
        </tbody>
    </table>
    <script>
        var self = this

        // --------------------------------------------------------------------
        // Tag init
        self.on('mount', function() {
            self.update_report()

            // Every 60 seconds update the report
            self.update_loop_forever()

            self.table_sorter = Tablesort(self.refs.table)
        })

        // --------------------------------------------------------------------
        // Updates
        self.update_report = function() {
            $.get("report.csv").done(function (data) {
                self.last_update = new Date()
                var csv = Papa.parse(data, {dynamicTyping: true, header: true})

                // Remove empty elements
                csv.data = csv.data.filter(function (item) {
                    return item.id != undefined && item.id != ""
                })

                csv.data.forEach(function(item) {
                    item['Status'] = item['Status'].replace(/(\r\n|\n|\r)/gm,"")
                })

                self.update({submissions: csv.data})
                self.budget_table_sorter.refresh();
            })
        }

        self.update_loop_forever = function() {
            window.setTimeout(function() {
                self.update_report()
                self.update_loop_forever()
            }, 60000)
        }
    </script>
    <style>
        reports {
            width: 100%;
        }
    </style>
</reports>