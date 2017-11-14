<reports>
    <table class="ui selectable striped table">
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
            </tr>
        </thead>
        <tbody>
            <tr each={submission in submissions}>
                <td>{submission["id"]}</td>
                <td>{submission["Submitter name"]}</td>
                <td>{submission["Zip name"]}</td>
                <td>{submission["Size of zip"]}</td>
                <td>{submission["Compute worker used"]}</td>
                <td>{submission["Queue used"]}</td>
                <td>{submission["Score"]}</td>
                <td>{submission["Total time taken"]}</td>
            </tr>
        </tbody>
    </table>
    <script>
        var self = this


        $.get("report.csv").done(function(data){
            var csv = Papa.parse(data, {dynamicTyping: true, header: true})

            // Remove empty elements
            csv.data = csv.data.filter(function(item){
                return item.id != undefined && item.id != ""
            })

            self.update({submissions: csv.data})
        })

    </script>
    <style>
        reports {
            width: 100%;
        }
    </style>
</reports>