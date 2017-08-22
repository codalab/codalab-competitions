#!/usr/bin/env python
"""
Defines the worker process which handles computations.
"""
import urllib

import json
import logging.config
import os
import platform
import uuid

import psutil
import pwd
import grp
import signal
import math
import re
import shutil
import socket
import sys
import tempfile
import time
import traceback

import requests
import yaml

from os.path import dirname, abspath, join, exists
from subprocess import Popen, call
from zipfile import ZipFile

from celery.app import app_or_default

# Add codalabtools to the module search path
from codalab import settings

sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

from codalabtools import BaseConfig
from apps.web.utils import docker_image_clean

logger = logging.getLogger('codalabtools')
# Stop duplicate log entries in Celery
logger.propagate = False


def _find_only_folder_with_metadata(path):
    """Looks through a bundle for a single folder that contains a metadata file and
    returns that folder's name if found"""
    files_in_path = os.listdir(path)
    if len(files_in_path) > 2 and 'metadata' in files_in_path:
        # We see more than a couple files OR metadata in this folder, leave
        return None
    for f in files_in_path:
        # Find first folder
        folder = os.path.join(path, f)
        if os.path.isdir(folder):
            # Check if it contains a metadata file
            if 'metadata' in os.listdir(folder):
                return folder


def docker_get_size():
    return os.popen("docker system df | awk -v x=4 'FNR == 2 {print $x}'").read().strip()


def docker_prune():
    """Runs a prune on docker if our images take up more than what's defined in settings."""
    # May also use docker system df --format "{{.Size}}"
    image_size = docker_get_size()
    image_size_measurement = image_size[-2:]
    image_size = float(image_size[:-2])

    if image_size > settings.DOCKER_MAX_SIZE_GB and image_size_measurement == "GB":
        logger.info("Pruning")
        os.system("docker system prune --force")


def get_bundle(root_dir, relative_dir, url):
    # get file name from /test.zip?signature=!@#a/df
    url_without_params = url.split('?')[0]
    file_name = url_without_params.split('/')[-1]
    file_ext = os.path.splitext(file_name)[1]

    logger.debug("get_bundle :: Getting %s from %s" % (file_name, url))

    # Save the bundle to a temp file
    # file_download_path = os.path.join(root_dir, file_name)
    bundle_file = tempfile.NamedTemporaryFile(prefix='tmp', suffix=file_ext, dir=root_dir, delete=False)
    urllib.urlretrieve(url, bundle_file.name)

    # Extracting files or grabbing extras
    bundle_path = join(root_dir, relative_dir)
    metadata_path = join(bundle_path, 'metadata')

    if file_ext == '.zip':
        logger.info("get_bundle :: Unzipping %s" % bundle_file.name)
        # Unzip file to relative dir, if a zip
        with ZipFile(bundle_file.file, 'r') as z:
            z.extractall(bundle_path)

        # check if we just unzipped something containing a folder and nothing else
        metadata_folder = _find_only_folder_with_metadata(bundle_path)
        if metadata_folder:
            logger.info("get_bundle :: Found a submission with an extra folder, unpacking and moving up a directory")
            # Make a temp dir and copy data there
            temp_folder_name = join(root_dir, "%s%s" % (relative_dir, '_tmp'))
            shutil.copytree(metadata_folder, temp_folder_name)

            # Delete old dir, move copied data back
            shutil.rmtree(bundle_path, ignore_errors=True)
            shutil.move(temp_folder_name, bundle_path)
    else:
        # Otherwise we have some metadata type file, like run.txt containing other bundles to fetch.
        os.mkdir(bundle_path)
        shutil.copyfile(bundle_file.name, metadata_path)

    os.chmod(bundle_path, 0777)

    # Check for metadata containing more bundles to fetch
    metadata = None
    if os.path.exists(metadata_path):
        with open(metadata_path) as mf:
            metadata = yaml.load(mf)

    if isinstance(metadata, dict):
        for (k, v) in metadata.items():
            if k not in ("description", "command", "exitCode", "elapsedTime", "stdout", "stderr", "submitted-by", "submitted-at"):
                if isinstance(v, str):
                    logger.debug("get_bundle :: Fetching recursive bundle %s %s %s" % (bundle_path, k, v))
                    # Here K is the relative directory and V is the url, like
                    # input: http://test.com/goku?sas=123
                    metadata[k] = get_bundle(bundle_path, k, v)
    return metadata


def _send_update(task_id, status, secret, virtual_host='/', extra=None):
    """
    Sends a status update about the running task.

    id: The task ID.
    status: The new status for the task. One of 'running', 'finished' or 'failed'.
    """
    task_args = {'status': status}
    if extra:
        task_args['extra'] = extra
    logger.info("Updating task=%s status to %s", task_id, status)
    from apps.web.tasks import update_submission
    app = app_or_default()
    with app.connection() as new_connection:
        # We need to send on the main virtual host, not whatever host we're currently
        # connected to.
        new_connection.virtual_host = virtual_host
        update_submission.apply_async((task_id, task_args, secret), connection=new_connection)


def put_blob(url, file_path):
    logger.info("Putting blob %s in %s" % (file_path, url))
    requests.put(
        url,
        data=open(file_path, 'rb'),
        headers={
            'x-ms-blob-type': 'BlockBlob',
        }
    )


class ExecutionTimeLimitExceeded(Exception):
    pass


def alarm_handler(signum, frame):
    raise ExecutionTimeLimitExceeded


def demote(user='workeruser'):
    def result():
        os.setgid(grp.getgrnam(user).gr_gid)
        os.setuid(pwd.getpwnam(user).pw_uid)
    return result


def get_run_func():
    """
    Returns the function to invoke in order to do a run given the specified configuration.

    Returns: The function to invoke given a Run task: f(task_id, task_args)
    """

    def run(task_id, task_args):
        """
        Performs a Run.

        task_id: The tracking ID for this task.
        task_args: The input arguments for this task:
        """
        logger.info("Entering run task; task_id=%s, task_args=%s", task_id, task_args)
        # run_id = task_args['bundle_id']
        docker_image = docker_image_clean(task_args['docker_image'])
        bundle_url = task_args['bundle_url']
        ingestion_program_docker_image = docker_image_clean(task_args['ingestion_program_docker_image'])
        stdout_url = task_args['stdout_url']
        stderr_url = task_args['stderr_url']
        ingestion_program_stderr_url = task_args['ingestion_program_stderr_url']
        ingestion_program_output_url = task_args['ingestion_program_output_url']
        output_url = task_args['output_url']
        detailed_results_url = task_args['detailed_results_url']
        private_output_url = task_args['private_output_url']

        execution_time_limit = task_args['execution_time_limit']
        # container = task_args['container_name']
        is_predict_step = task_args.get("predict", False)
        is_scoring_step = not is_predict_step
        secret = task_args['secret']
        current_dir = os.getcwd()
        temp_dir = os.environ.get('SUBMISSION_TEMP_DIR', '/tmp/codalab')

        if is_predict_step:
            logger.info("Task is prediction.")
        else:
            logger.info("Task is scoring.")

        # try:
        #     running_processes = subprocess.check_output(["fuser", temp_dir])
        # except:
        running_processes = '<DISABLED>'
        debug_metadata = {
            "hostname": socket.gethostname(),

            "processes_running_in_temp_dir": running_processes,

            "beginning_virtual_memory_usage": json.dumps(psutil.virtual_memory()._asdict()),
            "beginning_swap_memory_usage": json.dumps(psutil.swap_memory()._asdict()),
            "beginning_cpu_usage": psutil.cpu_percent(interval=None),

            # following are filled in after test ran + process SHOULD have been closed
            "end_virtual_memory_usage": None,
            "end_swap_memory_usage": None,
            "end_cpu_usage": None,
        }

        docker_prune()

        try:
            # Cleanup dir in case any processes didn't clean up properly
            for the_file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, the_file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)

            # Kill running processes in the temp dir
            try:
                call(["fuser", "-k", temp_dir])
            except:
                pass

            _send_update(task_id, 'running', secret, extra={
                'metadata': debug_metadata
            })
            # Create temporary directories for the run
            root_dir = tempfile.mkdtemp(dir=temp_dir)
            os.chmod(root_dir, 0777)

            run_dir = join(root_dir, 'run')
            shared_dir = tempfile.mkdtemp(dir=temp_dir)
            hidden_data_dir = None

            # Fetch and stage the bundles
            logger.info("Fetching bundles...")
            start = time.time()

            bundles = get_bundle(root_dir, 'run', bundle_url)

            # If we were passed hidden data, move it
            if is_predict_step:
                hidden_ref_original_location = join(run_dir, 'hidden_ref')
                if exists(hidden_ref_original_location):
                    logger.info("Found reference data AND an ingestion program, hiding reference data for ingestion program to use.")
                    shutil.move(hidden_ref_original_location, temp_dir)
                    hidden_data_dir = join(temp_dir, 'hidden_ref_%s'.format(str(uuid.uuid1())[0:8]))

            logger.info("Metadata: %s" % bundles)

            end = time.time() - start
            logger.info("Fetched bundles in %s", end)
            # Verify we have an input folder: create one if it's not in the bundle.
            input_rel_path = 'input'
            input_dir = join(root_dir, 'run', 'input')
            if input_rel_path not in bundles:
                if os.path.exists(input_dir) == False:
                    os.mkdir(input_dir)
                    os.chmod(input_dir, 0777)
            # Verify we have a program
            prog_rel_path = 'program'
            if prog_rel_path not in bundles:
                raise Exception("Program bundle is not available.")

            ingestion_prog_info = None
            if 'ingestion_program' in bundles:
                ingestion_prog_info = bundles['ingestion_program']
                if not ingestion_prog_info:
                    raise Exception("Ingestion program is missing metadata. Make sure the folder structure is "
                                    "appropriate (metadata not in a subdirectory).")

            # Look for submission/scoring program metadata, if we're scoring -- otherwise ingestion
            # program will handle the case where a code submission has no metadata.
            prog_info = bundles[prog_rel_path] or {}
            if prog_info is None and is_scoring_step:
                raise Exception("Program metadata is not available.")

            prog_cmd_list = []
            if 'command' in prog_info:
                if isinstance(prog_info['command'], type([])):
                    prog_cmd_list = [_.strip() for _ in prog_info['command']]
                else:
                    prog_cmd_list = [prog_info['command'].strip()]
            if len(prog_cmd_list) <= 0 and is_scoring_step:
                raise Exception("Program command is not specified.")

            # Create output folder
            output_dir = join(root_dir, 'run', 'output')
            if os.path.exists(output_dir) == False:
                os.mkdir(output_dir)
                os.chmod(output_dir, 0777)
            # Create temp folder
            temp_dir = join(root_dir, 'run', 'temp')
            if os.path.exists(temp_dir) == False:
                os.mkdir(temp_dir)
                os.chmod(temp_dir, 0777)
            # Report the list of folders and files staged
            #
            # Invoke custom evaluation program
            os.chdir(run_dir)
            os.environ["PATH"] += os.pathsep + run_dir + "/program"
            logger.info("Execution directory: %s", run_dir)

            if is_predict_step:
                stdout_file_name = 'prediction_stdout_file.txt'
                stderr_file_name = 'prediction_stderr_file.txt'
            else:
                stdout_file_name = 'stdout.txt'
                stderr_file_name = 'stderr.txt'

            stdout_file = join(run_dir, stdout_file_name)
            stderr_file = join(run_dir, stderr_file_name)
            stdout = open(stdout_file, "a+")
            stderr = open(stderr_file, "a+")
            prog_status = []

            ingestion_stdout_file = join(run_dir, 'ingestion_stdout_file.txt')
            ingestion_stderr_file = join(run_dir, 'ingestion_stderr_file.txt')
            ingestion_stdout = open(ingestion_stdout_file, "a+")
            ingestion_stderr = open(ingestion_stderr_file, "a+")

            run_ingestion_program = False

            timed_out = False
            exit_code = None
            ingestion_program_exit_code = None

            # If our program command list is empty and we're not scoring, we probably got a result submission
            if not prog_cmd_list and is_predict_step:
                prog_cmd_list = ['']

            for prog_cmd_counter, prog_cmd in enumerate(prog_cmd_list):
                startTime = time.time()

                # Ingestion programs (optional) determine whether or not a submission is code or results, and then
                # if given, run the code or move the results appropriately

                if is_predict_step:
                    logger.info("Running ingestion program")

                    # Check that we should even be running this submission in a special way, may
                    # just be results..
                    submission_path = join(run_dir, "program")
                    metadata_path = join(submission_path, "metadata")
                    is_code_submission = False
                    if exists(metadata_path):
                        submission_metadata = yaml.load(open(metadata_path).read())
                        is_code_submission = "command" in submission_metadata.keys()

                    if is_code_submission:
                        logger.info("We have a code submission!")

                    # We're in prediction so use an ingestion program to process the submission.
                    # Was an ingestion program provided?
                    if is_code_submission and ingestion_prog_info:
                        logger.info("Running organizer provided ingestion program and submission.")
                        # Run ingestion program, run submission
                        run_ingestion_program = True
                    elif is_code_submission:
                        logger.info("Running code submission like normal, no ingestion program provided.")
                    else:
                        # We didn't find an ingestion program, let's use the following simple one
                        # that just executes the submission and moves results
                        logger.info("No code submission, moving input directory to output.")
                        # This isn't a code submission, it is already ready to score. Remove
                        # old output directory and replace it with this submission's contents.
                        os.rmdir(output_dir)
                        os.rename(input_dir, output_dir)

                evaluator_process = None
                if prog_cmd:
                    # Update command-line with the real paths
                    prog_cmd = prog_cmd.replace("$program", join(run_dir, 'program')) \
                                        .replace("$input", join(run_dir, 'input')) \
                                        .replace("$output", join(run_dir, 'output')) \
                                        .replace("$tmp", join(run_dir, 'temp')) \
                                        .replace("$shared", shared_dir) \
                                        .replace("/", os.path.sep) \
                                        .replace("\\", os.path.sep)
                    prog_cmd = prog_cmd.split(' ')
                    docker_cmd = [
                        'docker',
                        'run',
                        # Remove it after run,
                        '--rm',
                        # Set the right volume
                        '-v', '{0}:{0}'.format(run_dir),
                        '-v', '{0}:{0}'.format(shared_dir),
                        # Note that hidden data dir is excluded here!
                        # Set the right image
                        docker_image,
                    ]
                    prog_cmd = docker_cmd + prog_cmd

                    logger.info("Invoking program: %s", " ".join(prog_cmd))
                    evaluator_process = Popen(
                        prog_cmd,
                        stdout=stdout,
                        stderr=stderr,
                        env=os.environ,
                        # cwd=join(run_dir, 'program')
                    )

                if run_ingestion_program:
                    if 'command' not in ingestion_prog_info:
                        raise Exception("Ingestion program metadata was found, but is missing the 'command' attribute,"
                                        "which is necessary to execute the ingestion program.")
                    ingestion_prog_cmd = ingestion_prog_info['command']

                    # ingestion_run_dir = join(run_dir, 'ingestion')
                    ingestion_prog_cmd = ingestion_prog_cmd.replace("$program", join(run_dir, 'ingestion_program')) \
                        .replace("$input", join(run_dir, 'input')) \
                        .replace("$output", join(run_dir, 'output')) \
                        .replace("$tmp", join(run_dir, 'temp')) \
                        .replace("$shared", shared_dir) \
                        .replace("$hidden", hidden_data_dir) \
                        .replace("/", os.path.sep) \
                        .replace("\\", os.path.sep)
                    ingestion_prog_cmd = ingestion_prog_cmd.split(' ')
                    ingestion_docker_cmd = [
                        'docker',
                        'run',
                        # Remove it after run,
                        '--rm',
                        # Set the right volume
                        '-v', '{0}:{0}'.format(run_dir),
                        '-v', '{0}:{0}'.format(shared_dir),
                        '-v', '{0}:{0}'.format(hidden_data_dir),
                        # Set the right image
                        ingestion_program_docker_image,
                    ]
                    ingestion_prog_cmd = ingestion_docker_cmd + ingestion_prog_cmd

                    logger.info("Invoking ingestion program: %s", " ".join(ingestion_prog_cmd))
                    ingestion_process = Popen(
                        ingestion_prog_cmd,
                        stdout=ingestion_stdout,
                        stderr=ingestion_stderr,
                        # cwd=join(run_dir, 'ingestion_program')
                    )
                else:
                    ingestion_process = None

                if evaluator_process:
                    logger.info("Started process, pid=%s" % evaluator_process.pid)

                if evaluator_process or ingestion_process:
                    # Only if a program is running do these checks, otherwise infinite loop checking nothing!
                    time_difference = time.time() - startTime
                    signal.signal(signal.SIGALRM, alarm_handler)
                    signal.alarm(int(math.fabs(math.ceil(execution_time_limit - time_difference))))

                    logger.info("Checking process, exit_code = %s" % exit_code)

                    try:
                        # While either program is running and hasn't exited, continue polling
                        while (evaluator_process and exit_code == None) or (ingestion_process and ingestion_program_exit_code == None):
                            time.sleep(1)

                            if evaluator_process and exit_code is None:
                                exit_code = evaluator_process.poll()

                            if ingestion_process and ingestion_program_exit_code is None:
                                ingestion_program_exit_code = ingestion_process.poll()
                    except (ValueError, OSError):
                        pass  # tried to communicate with dead process
                    except ExecutionTimeLimitExceeded:
                        logger.info("Killed process for running too long!")
                        stderr.write("Execution time limit exceeded!")

                        if evaluator_process:
                            exit_code = -1
                            evaluator_process.kill()
                        if ingestion_process:
                            ingestion_program_exit_code = -1
                            ingestion_process.kill()

                        timed_out = True

                    signal.alarm(0)

                    if evaluator_process:
                        logger.info("Exit Code regular process: %d", exit_code)
                    if ingestion_process:
                        logger.info("Exit Code ingestion process: %d", ingestion_program_exit_code)
                else:
                    exit_code = 0  # let code down below know everything went OK

                endTime = time.time()
                elapsedTime = endTime - startTime

                if len(prog_cmd_list) == 1:
                    # Overwrite prog_status array with dict
                    prog_status = {
                        'exitCode': exit_code,
                        'elapsedTime': elapsedTime
                    }
                else:
                    # otherwise we're doing multi-track and processing multiple commands so append to the array
                    prog_status.append({
                        'exitCode': exit_code,
                        'elapsedTime': elapsedTime
                    })
                with open(join(output_dir, 'metadata'), 'w') as f:
                    f.write(yaml.dump(prog_status, default_flow_style=False))

                if timed_out or exit_code != 0:
                    # Submission failed somewhere in here, bomb out
                    break

            stdout.close()
            stderr.close()

            logger.info("Saving output files")

            put_blob(stdout_url, stdout_file)
            put_blob(stderr_url, stderr_file)

            if run_ingestion_program:
                ingestion_stdout.close()
                ingestion_stderr.close()
                put_blob(ingestion_program_stderr_url, ingestion_stdout_file)
                put_blob(ingestion_program_output_url, ingestion_stderr_file)

            private_dir = join(output_dir, 'private')
            if os.path.exists(private_dir):
                logger.info("Packing private results...")
                private_output_file = join(root_dir, 'run', 'private_output.zip')
                shutil.make_archive(os.path.splitext(private_output_file)[0], 'zip', output_dir)
                put_blob(private_output_url, private_output_file)
                shutil.rmtree(private_dir, ignore_errors=True)

            # Pack results and send them to Blob storage
            logger.info("Packing results...")
            output_file = join(root_dir, 'run', 'output.zip')
            shutil.make_archive(os.path.splitext(output_file)[0], 'zip', output_dir)
            put_blob(output_url, output_file)

            # Check if the output folder contain an "html file" and copy the html file as detailed_results.html
            # traverse root directory, and list directories as dirs and files as files
            html_found = False
            for root, dirs, files in os.walk(output_dir):
                if not (html_found):
                    path = root.split('/')
                    for file in files:
                        file_to_upload = os.path.join(root,file)
                        file_ext = os.path.splitext(file_to_upload)[1]
                        if file_ext.lower() ==".html":
                            put_blob(detailed_results_url, file_to_upload)
                            html_found = True

            # Save extra metadata
            debug_metadata["end_virtual_memory_usage"] = json.dumps(psutil.virtual_memory()._asdict())
            debug_metadata["end_swap_memory_usage"] = json.dumps(psutil.swap_memory()._asdict())
            debug_metadata["end_cpu_usage"] = psutil.cpu_percent(interval=None)

            # check if timed out AFTER output files are written! If we exit sooner, no output is written
            if timed_out:
                logger.exception("Run task timed out (task_id=%s).", task_id)
                _send_update(task_id, 'failed', secret, extra={
                    'metadata': debug_metadata
                })
            elif exit_code != 0:
                logger.exception("Run task exit code non-zero (task_id=%s).", task_id)
                _send_update(task_id, 'failed', secret, extra={
                    'traceback': open(stderr_file).read(),
                    'metadata': debug_metadata
                })
            else:
                _send_update(task_id, 'finished', secret, extra={
                    'metadata': debug_metadata
                })
        except Exception:
            if debug_metadata['end_virtual_memory_usage'] == None:
                # We didnt' make it far enough to save end metadata... so do it!
                debug_metadata["end_virtual_memory_usage"] = json.dumps(psutil.virtual_memory()._asdict())
                debug_metadata["end_swap_memory_usage"] = json.dumps(psutil.swap_memory()._asdict())
                debug_metadata["end_cpu_usage"] = psutil.cpu_percent(interval=None)

            logger.exception("Run task failed (task_id=%s).", task_id)
            _send_update(task_id, 'failed', secret, extra={
                'traceback': traceback.format_exc(),
                'metadata': debug_metadata
            })

        # comment out for dev and viewing of raw folder outputs.
        if root_dir is not None:
            # Try cleaning-up temporary directory
            try:
                os.chdir(current_dir)
                shutil.rmtree(root_dir, ignore_errors=True)
            except:
                logger.exception("Unable to clean-up local folder %s (task_id=%s)", root_dir, task_id)
    return run
