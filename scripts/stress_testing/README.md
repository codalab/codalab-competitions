Stress testing
==============



## make_submission.py

Creates a submission and saves the `id` to `submission_ids.txt`

Example usage:

```
./make_submission.py test.zip admin@admin.com -c 5
```


Help:

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

Example usage:

```
# Only runs once, not a daemon
./approve_emails.py
```

Help:

```
usage: approve_emails.py [-h] [--valid_email_list VALID_EMAIL_LIST]
                         [-c COMPETITION]

optional arguments:
  -h, --help            show this help message and exit
  --valid_email_list VALID_EMAIL_LIST
                        File containing a list of newline separated
                        emails/patterns to approve
  -c COMPETITION, --competition COMPETITION
                        Competition ID, defaults to 1
```

Example `approve_emails.txt` file:

```
admin@admin.com
*@codalab.org
*@*.edu
```


## view_report.py

Starts a simple webserver that processes `submission_ids.txt` and serves up a processed view of it.

Easy way to run in background on linux and ignoring output:

```
nohup python view_report.py > /dev/null 2>&1 &
```


## cancel_tasks.py

Cancels all currently running tasks. No more will be distributed, but existing tasks may take a while to completely
stop.
