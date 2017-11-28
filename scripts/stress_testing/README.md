Stress testing
==============



## make_submission.py

Creates a submission and saves the `id` to `submission_ids.txt`

```
usage: make_submission.py [-h] [-c COMPETITION]
                          submission_zip participant_email

positional arguments:
  submission_zip        Submission zip file to use for stressing
  participant_email     Participant, identified by email address

optional arguments:
  -h, --help            show this help message and exit
  -c COMPETITION, --competition COMPETITION
                        Competition ID, defaults to 1

```

## approve_emails.py

Takes a list of emails, separated by newlines, default filename `approve_emails.txt`. Marks any email
matching the pattern as approved, any email not matching is denied.

Example `approve_emails.txt`

```
admin@admin.com
*@codalab.org
*@*.edu
```


## view_report.py

Starts a simple webserver that processes `submission_ids.txt` and serves up a processed view of it.


## cancel_tasks.py

Cancels all currently running tasks. No more will be distributed, but existing tasks may take a while to completely
stop.
