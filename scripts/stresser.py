#!/usr/bin/env python

import argparse
import requests
from textwrap import dedent
from subprocess import check_output

from os.path import exists


def put_blob(url, file_path):
    requests.put(
        url,
        data=open(file_path, 'rb'),
        headers={
            # Only for Azure but AWS ignores this fine
            'x-ms-blob-type': 'BlockBlob',
        }
    )


if __name__ == "__main__":
    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_zip", help="Submission zip file to use for stressing")
    parser.add_argument("participant_email", help="Participant, identified by email address")
    parser.add_argument("-c", "--competition", default=1, help="Competition ID, defaults to 1")
    args = parser.parse_args()

    # Validate arguments
    if not args.submission_zip.endswith(".zip"):
        raise Exception("Received non zip file: {}".format(args.submission_zip))

    if not exists(args.submission_zip):
        raise Exception("Zip file not found: {}".format(args.submission_zip))

    print(args.submission_zip)
    print(args.participant_email)
    print(args.competition)

    # Get SAS URL by running a script inside docker and printing out the URL between asterisks, like:
    # >>> ***http://url-we-want.com/***
    get_sas_url_script = dedent("""
        from django.conf import settings
        from apps.web.tasks import _make_url_sassy
        
        if settings.USE_AWS:
            attr = 's3_file'
        else:
            attr = 'file'
        
        url = _make_url_sassy(getattr(CompetitionSubmission(), attr), permission='w')
        
        # wrap the URL so we can easily parse it from the output
        print('***{}***'.format(url))
    """)

    test = check_output([
        "docker",
        "exec",
        "-it",
        "django",
        "bash",
        "-c",
        'echo "{}" | python manage.py shell_plus'.format(get_sas_url_script)
    ])

    submission_url = test.split('***')[1]

    # Put submission to that URL
    put_blob(submission_url, args.submission_zip)


    # Tie it together and submit
    submission_script = """
        from django.conf import settings
        from apps.web.models import Competition, CompetitionSubmission, CompetitionParticipant
        
        if settings.USE_AWS:
                file_kwarg = {{'s3_file': {submission_url}}}
            else:
                file_kwarg = {{'file': {submission_url}}}
                
        competition = Competition.objects.get(pk={competition_id})
        phase = None
        for phase in competition.phases.all():
            if phase.is_active:
                phase = phase
                break
        
        new_submission = CompetitionSubmission(
            participant=CompetitionParticipant.objects.get(email={email}, competition=competition),
            phase=phase,
            **file_kwarg
        )
        new_submission.save(ignore_submission_limits=True)
    
        evaluate_submission.apply_async((new_submission.pk, phase.is_scoring_only))
    """.format(
        submission_url=submission_url,
        email=args.participant_email,
        competition_id=args.competition
    )


    # # Get arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument("submissions", nargs="*", help="Submission zip files to use for stressing")
    # args = parser.parse_args()
    #
    # # Get valid submission zips
    # submissions = []
    #
    # for arg in args.submissions:
    #     if not arg.endswith(".zip"):
    #         print("WARNING: Received non zip file: {}".format(arg))
    #     else:
    #         submissions.append(arg)
    #
    # submission_count = len(submissions)
    # if submission_count == 0:
    #     raise Exception("ERROR: Did not receive any submission zips, arguments were: {}".format(sys.argv))
    #
    # #
    # print("Running stress test with {} submissions".format(len(submissions)))

