import os
import argparse

import datetime
from urllib.parse import urlparse

import requests
import time
from requests import RequestException
from requests.auth import HTTPBasicAuth

from tqdm import trange, tqdm


def print_out_failed_request_info(info):
    print("URL: {url}, Status Code: {status}, Content: {content}".format(
        **info))


def get_remote_submission_info(args, submission_id, **instance_info):
    # print("**********************************")
    # print(instance_info)
    # print("**********************************")
    # challenge_site_url = self.submission.definition.get_challenge_domain()
    # score_api_url = "{0}/api/submission/{1}/get_score".format(challenge_site_url, self.remote_id)
    score_api_url = "{0}://{1}/api/submission/{2}/get_score".format(instance_info.get('scheme'), args.get('domain'), submission_id)
    score_api_resp = requests.get(
        score_api_url,
        auth=instance_info.get('auth_cred')
    )
    if score_api_resp.status_code == 200:
        data = score_api_resp.json()
        if data.get('status'):
            print("Data found for submission. Returning scores.")
            return {
                'status': data.get('status'),
                'score': data.get('score', None)
            }
        else:
            # print("Could not retrieve complete data for submission")
            return None
    elif score_api_resp.status_code == 404:
        # print("Could not find submission or competition.")
        return None
    elif score_api_resp.status_code == 403:
        # print("Not authorized to make this request.")
        return None
    # print("There was a problem making the request")
    return None


def upload_competition_file(args):
    print("Initializing competition upload. Please be patient.")
    USE_GCS = False
    USE_AZURE = False
    size = str(os.path.getsize(args.get('bundle_dir')))
    filename = os.path.basename(args.get('bundle_dir'))
    # Custom check on HTTP vs HTTPS
    try:
        ssl_check_resp = requests.get('http://{}'.format(args.get('domain')))
        actual_url = ssl_check_resp.url
        schema = urlparse(actual_url).scheme
        print("Domain using scheme: {}".format(schema))
    except RequestException as error:
        print("Domain not reachable, or not resolving: {}".format(error.message))
        return
    user_auth = HTTPBasicAuth(args.get('username'),
                              args.get('password'))
    sas_create_url = '{0}://{1}/api/competition/create/sas'.format(schema, args.get('domain'))
    # Hit the SAS create API endpoint
    sas_api_resp = requests.post(sas_create_url, auth=user_auth)
    # If our sas_api_resp status code is 20x, try to actually upload the file
    if 200 <= sas_api_resp.status_code <= 299:
        print("Codalab competition SAS API request successful!")
        sas_url = sas_api_resp.json().get('url')
        sas_file_id = sas_api_resp.json().get('id')
        # DETERMINE STORAGE FROM STORAGE URL!!!!
        storage_domain = urlparse(sas_url).netloc
        split_domain = storage_domain.split('.')
        print("Determining storage from SAS url given.")
        if storage_domain == 'storage.googleapis.com':
            USE_GCS = True
        elif split_domain[len(split_domain) - 2:len(split_domain)] == ['windows', 'net']:
            USE_AZURE = True

        print("Determined storage, ready to upload bundle!")
        with open(args.get('bundle_dir'), 'rb') as bundle_file:
            print("Reading bundle file and uploading to storage!")
            storage_request_data = {'url': sas_url, 'data': bundle_file}
            if USE_GCS:
                storage_request_data['headers'] = {
                    "Content-Type": "application/zip",
                    "content-name": filename,
                    "Content-Length": size,
                    # "Content-Encoding": "gzip",
                }
            if USE_AZURE:
                storage_request_data['headers'] = {
                    # "Content-Type": "application/zip",
                    "x-ms-blob-type": 'BlockBlob',
                    # "content-name": filename,
                    "Content-Length": size,
                    # "Content-Encoding": "gzip",
                }
            if USE_GCS:
                print("USE GCS: {}".format(USE_GCS))
            if USE_AZURE:
                print("USE AZURE: {}".format(USE_AZURE))
            print("About to upload competition bundle to the storage url: {}".format(sas_url))
            storage_resp = requests.put(**storage_request_data)
            # If our upload to storage is succesful
            if 200 <= storage_resp.status_code <= 299:
                print("Succesfully uploaded competition to storage!")
                competition_finalize_url = '{0}://{1}/api/competition/create'.format(schema, args.get('domain'))
                codalab_resp = requests.post(
                    url=competition_finalize_url,
                    data={
                        'id': sas_file_id,
                        'name': filename,
                        'size': size,
                        'type': 'application/zip'
                    },
                    auth=user_auth
                )
                # If our competition succesfully unpacks
                if 200 <= codalab_resp.status_code <= 299:
                    print("Succesfully started unpack of competition!")
                    competition_token = codalab_resp.json().get('token')
                    if not competition_token:
                        print("No competition token returned!")
                        return
                    status_check_url = '{0}://{1}/api/competition/create/{2}'.format(schema, args.get('domain'),
                                                                                      competition_token)
                    finalized_competition_id = None
                    # Retry our status check api, until the status is finished for our competition
                    t = trange(180)
                    for i in t:
                        status_check_resp = requests.get(status_check_url, auth=user_auth)
                        t.set_description("Status: {}".format(status_check_resp.json().get('status')))
                        t.refresh()  # to show immediately the update
                        if status_check_resp.status_code == 200:
                            if status_check_resp.json().get('status') == 'finished' or status_check_resp.json().get('status') == 'failed':
                                if status_check_resp.json().get('status') == 'failed':
                                    print("Competition upload failed:")
                                    print(status_check_resp.json().get('error'))
                                    return
                                finalized_competition_id = status_check_resp.json().get('id')
                                break
                        time.sleep(1)
                    # Status check finished, we are finished
                    if not finalized_competition_id:
                        print("Did not get a finalized competition ID")
                        return
                    detail_view_url = '{0}://{1}/competitions/{2}'.format(schema, args.get('domain'),
                                                                          finalized_competition_id)
                    print("Succesfully created competition (Note you may have to login to view the link): {}".format(detail_view_url))
                    if USE_GCS:
                        storage = 'GCS'
                    elif USE_AZURE:
                        storage = 'AZURE'
                    else:
                        storage = {}
                    return {
                        'scheme': schema,
                        'storage': storage,
                        'comp_detail': detail_view_url,
                        'auth_cred': user_auth
                    }
                else:
                    print("Failed to finalize competiion on Codalab!")
                    print_out_failed_request_info({'url': competition_finalize_url, 'status': codalab_resp.status_code, 'content': codalab_resp.content})
            else:
                print("Failed to upload to storage!")
                print_out_failed_request_info({'url': sas_url, 'status': storage_resp.status_code, 'content': storage_resp.content})
    else:
        print("Failed to get back a SAS url to upload to!")
        print_out_failed_request_info({'url': sas_create_url, 'status': sas_api_resp.status_code, 'content': sas_api_resp.content})


def upload_submission(args, **instance_info):
    if not instance_info.get('storage'):
        print("Need to determine storage again!")
    else:
        storage = instance_info.get('storage')
    scheme = instance_info.get('scheme')
    competition_url = instance_info.get('comp_detail')
    user_auth = instance_info.get('auth_cred')

    size = str(os.path.getsize(args.get('bundle_dir')))
    filename = os.path.basename(args.get('bundle_dir'))

    print("Preparing to make submission.")

    # Get our URL's formatted and such
    # submission = Submission.objects.get(pk=submission_pk)
    parsed_uri = urlparse(competition_url)
    # print(parsed_uri)
    scheme = parsed_uri.scheme
    domain = parsed_uri.netloc
    path = parsed_uri.path
    challenge_pk = path.split('/')[-1]
    site_url = "{0}://{1}".format(scheme, domain)
    submission_sas_url = '{0}/api/competition/{1}/submission/sas'.format(site_url, challenge_pk)
    # Post our request to the submission SAS API endpoint
    print("Getting submission SAS info")
    codalab_sas_resp = requests.post(
        url=submission_sas_url, auth=user_auth, data={'name': filename}
    )
    if not 200 <= codalab_sas_resp.status_code <= 299:
        print("Unable to get submission SAS url from Codalab!")
        print_out_failed_request_info({'url': submission_sas_url, 'status': codalab_sas_resp.status_code, 'content': codalab_sas_resp.content})
        return
    print("Succesfully got codalab SAS response")
    # competition/15595/submission/44798/4aba772a-a6c1-4e6f-a82b-fb9d23193cb6.zip
    submission_data = codalab_sas_resp.json()['id']
    sas_url = codalab_sas_resp.json()['url']
    with open(args.get('submission_dir'), 'rb') as bundle_file:
        print("Reading bundle file and uploading to storage!")
        storage_request_data = {'url': sas_url, 'data': bundle_file}
        if storage == 'GCS':
            storage_request_data['headers'] = {
                "Content-Type": "application/zip",
                "content-name": filename,
                "Content-Length": size,
                # "Content-Encoding": "gzip",
            }
        if storage == 'AZURE':
            storage_request_data['headers'] = {
                # "Content-Type": "application/zip",
                "x-ms-blob-type": 'BlockBlob',
                # "content-name": filename,
                "Content-Length": size,
                # "Content-Encoding": "gzip",
            }
        print("About to upload competition bundle to the storage url: {}".format(sas_url))
        storage_resp = requests.put(**storage_request_data)
    if not 200 <= storage_resp.status_code <= 299:
        print("Failed to upload to storage!")
        print_out_failed_request_info(
            {'url': sas_url, 'status': storage_resp.status_code, 'content': storage_resp.content})
        return
    print("Succesfully uploaded to storage!")
    # https://competitions.codalab.org/api/competition/20616/phases/
    phases_request_url = "{0}/api/competition/{1}/phases/".format(site_url, challenge_pk)
    print("Getting phase info for competition")
    phases_request = requests.get(url=phases_request_url, auth=user_auth)
    phases_dict = phases_request.json()[0]['phases']
    t = trange(len(phases_dict))
    failed_phases = []
    phase_results = []
    for i in t:
        phase_id = phases_dict[i]['id']
        t.set_description("Phase ID: {}".format(phases_dict[i]['id']))
        sub_descr = "Test_Submission_{0}".format(args.get('username'))
        finalize_url = "{0}/api/competition/{1}/submission?description={2}&phase_id={3}".format(site_url, challenge_pk,
                                                                                                sub_descr, phase_id)
        custom_filename = "{username}_{date}.zip".format(username=args.get('username'), date=datetime.datetime.now().date())
        phase_final_resp = requests.post(finalize_url, data={
            'id': submission_data,
            # 'name': 'master.zip',
            'name': custom_filename,
            'type': 'application/zip',
            # 'size': ?
        }, auth=user_auth)
        # If we succeed in posting to the phase, create a new tracker and store the submission info
        if phase_final_resp.status_code == 201:
            result = phase_final_resp.json()
            phase_results.append(result)
        else:
            failed_phases.append(phase_id)
    print("Phases that failed: {}".format(failed_phases))
    print("Results: {}".format(phase_results))
    # print(instance_info)
    if args.get('wait_for_submission'):
        for i in tqdm(range(30 * 60)):
            data = get_remote_submission_info(args, phase_results[0]['id'], **instance_info)
            if data:
                # if data.get('score'):
                print(data)
                break
            time.sleep(1)
        print("One submission finished succesfully!")
    return {'successful_submissions': len(phase_results), 'failed_submissions': len(failed_phases), 'success_rate': (float(len(phase_results)) / float((len(failed_phases) + len(phase_results)))) * 100 if (len(phase_results) + len(failed_phases) != 0) else 0}

def delete_competition(args, **instance_info):
    scheme = instance_info.get('scheme')
    competition_url = instance_info.get('comp_detail')
    user_auth = instance_info.get('auth_cred')
    challenge_pk = urlparse(competition_url).path.split('/')[-1]
    print("Deleting competition with ID/PK of {}".format(challenge_pk))
    delete_url = "{0}://{1}/api/competition/{2}".format(scheme, args.get('domain'), challenge_pk)
    print(delete_url)
    delete_request = requests.delete(delete_url, auth=user_auth)
    if delete_request.status_code == 200:
        print("Succesfully cleaned up test competition!")
    else:
        print("Failed to clean up test competition!")


def setup_parser():
    parser = argparse.ArgumentParser()

    # Bundle Argument
    parser.add_argument('--bundle', '-b', help="The competition bundle to use", type=str, dest='bundle_dir',
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             'test_files/competition_bundle.zip')
                        )
    # Submission Argument
    parser.add_argument('--submission', '-s', help="The submission file to use", type=str, dest='submission_dir',
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_files/submission.zip')
                        )
    # Username & Password Arguments
    parser.add_argument('--username', '-u', help="The username to auth with", type=str, dest='username',
                        default='admin')
    parser.add_argument('--password', '-p', help="The password to auth with", type=str, dest='password',
                        default='admin')
    # Domain argument (optional otherwise defaults to localhost)
    parser.add_argument('--domain', '-d',
                        help="The domain that the instance you are testing lives on. Do not include HTTP scheme.",
                        type=str,
                        dest='domain', default='localhost')
    parser.add_argument('--wait', '-w',
                        help="Test and wait for a submission to actually finish! Will automatically time out after 30 mins",
                        type=bool,
                        dest='wait_for_submission', default=False)
    return parser


def main():
    parser = setup_parser()
    args = vars(parser.parse_args())
    time.sleep(1)
    print("**************************************")
    print("Running with args: {}".format(args))
    print("**************************************")
    instance_info = upload_competition_file(args)
    if not instance_info:
        print("Competition upload must've failed! Breaking")
        return
    print("Instance info returned: {}".format(instance_info))
    submission_counts = upload_submission(args, **instance_info)
    if not submission_counts:
        print("There was an error making submissions!")
        return
    delete_competition(args, **instance_info)
    print(
    "Success Rate: {success_rate}; Failed Submissions: {failed_submissions}; Successful Submissions: {successful_submissions}".format(
        **submission_counts))


if __name__ == '__main__':
    main()  # Or whatever function produces output
