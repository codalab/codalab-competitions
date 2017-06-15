#!/usr/bin/env python
"""
Defines the worker process which handles computations.
"""
import urllib

import json
import logging.config
import os
import platform
import psutil
import pwd
import grp
import signal
import math
import shutil
import socket
import sys
import tempfile
import time
import traceback

import requests
import yaml

from os.path import dirname, abspath, join
from subprocess import Popen, call
from zipfile import ZipFile

from celery.app import app_or_default

# Add codalabtools to the module search path
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

from codalabtools import BaseConfig


logger = logging.getLogger('codalabtools')


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


# class WorkerConfig(BaseConfig):
#     """
#     Defines configuration properties (mostly credentials) for a worker process.
#     """
#     def __init__(self, filename='.codalabconfig'):
#         super(WorkerConfig, self).__init__(filename)
#         self._winfo = self.info['compute-worker']
#
#     def getLoggerDictConfig(self):
#         """Gets Dict config for logging configuration."""
#         if 'logging' in self._winfo:
#             return self._winfo['logging']
#         else:
#             return super(WorkerConfig, self).getLoggerDictConfig()
#
#     def getLocalRoot(self):
#         """Gets the path for the local directory where files are staged or None if the path is not provided."""
#         return self._winfo['local-root'] if 'local-root' in self._winfo else None


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


# def getBundle(root_path, blob_service, container, bundle_id, bundle_rel_path, max_depth=3):
#     """
#     be controlled with the max_depth parameter.
#
#     root_path: Path of the local directory under which all files are staged for execution.
#     blob_service: Azure BlobService to access the storage account holding the bundles.
#     container: Name of Blob container holding the bundles in the specified storage account.
#     bundle_id: The ID of the bundle which in this implementation is the path of the Blob
#         relative to the container. For example if a bundle is stored in a Blob with URL
#         'https://codalab.blob.core.windows.net/bundlecontainer/bundles/1/run.txt' then
#         the bundle ID is 'bundles/1/run.txt'.
#     bundle_rel_path: Path of the local bundle directory relative to the root directory. For
#         example, if root_path is 'C:\\tmp123' and bundle_rel_path is 'run\\program', then the
#         program bundle will be located at 'C:\\tmp123\\run\\program'.
#     max_depth: An optional argument to limit the depth of recursion when resolving bundle
#         dependencies.
#
#     Return value: A dictionary where each key denotes the relative path of a bundle which
#         was staged. The value associated with a key is a dictionary representing the bundle's
#         metadata. The value may be None if a metadata file was not found. For a valid run,
#         the set of keys should contain at the minimum: 'run', 'run\\program' and 'run\\input'.
#     """
#
#     def getThem(bundle_id, bundle_rel_path, bundles, depth):
#         """Recursively gets the bundles."""
#         logger.info("Trying to get %s", bundle_rel_path)
#
#         retries_left = 2
#         while retries_left > 0:
#             try:
#                 logger.debug("Getting bundle_id=%s from container=%s" % (bundle_id, container))
#                 blob = blob_service.get_blob(container, bundle_id)
#                 break
#             except azure.WindowsAzureMissingResourceError:
#                 retries_left = 0
#             except:
#                 logger.exception("Failed to fetch bundle_id=%s blob", bundle_id)
#                 retries_left -= 1
#
#         if retries_left == 0:
#             # file not found lets None this bundle
#             bundles[bundle_rel_path] = None
#             return bundles
#
#         bundle_ext = os.path.splitext(bundle_id)[1]
#         bundle_file = tempfile.NamedTemporaryFile(prefix='tmp', suffix=bundle_ext, dir=root_path, delete=False)
#
#         logger.debug("Reading from bundle_file.name=%s" % bundle_file.name)
#
#         # take our temp file and write whatever is it form the blob
#         with open(bundle_file.name, 'wb') as f:
#             f.write(blob)
#         # stage the bundle directory
#         bundle_path = join(root_path, bundle_rel_path)
#         metadata_path = join(bundle_path, 'metadata')
#
#         if bundle_ext == '.zip':
#             with ZipFile(bundle_file.file, 'r') as z:
#                 z.extractall(bundle_path)
#
#             # check if we just unzipped something containing a folder and nothing else
#             metadata_folder = _find_only_folder_with_metadata(bundle_path)
#             if metadata_folder:
#                 # Make a temp dir and copy data there
#                 temp_folder_name = join(root_path, "%s%s" % (bundle_rel_path, '_tmp'))
#                 shutil.copytree(metadata_folder, temp_folder_name)
#
#                 # Delete old dir, move copied data back
#                 shutil.rmtree(bundle_path, ignore_errors=True)
#                 shutil.move(temp_folder_name, bundle_path)
#         else:
#             os.mkdir(bundle_path)
#             shutil.copyfile(bundle_file.name, metadata_path)
#         # read the metadata if it exists
#         bundle_info = None
#         if os.path.exists(metadata_path):
#             with open(metadata_path) as mf:
#                 bundle_info = yaml.load(mf)
#
#         os.chmod(bundle_path, 0777)
#
#         bundles[bundle_rel_path] = bundle_info
#         # get referenced bundles
#
#         if (bundle_info is not None) and isinstance(bundle_info, dict) and (depth < max_depth):
#             for (k, v) in bundle_info.items():
#                 if k not in ("description", "command", "exitCode", "elapsedTime", "stdout", "stderr", "submitted-by", "submitted-at"):
#                     if isinstance(v, str):
#                         getThem(v, join(bundle_rel_path, k), bundles, depth + 1)
#
#         return bundles
#
#     return getThem(bundle_id, bundle_rel_path, {}, 0)


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
        docker_image = task_args.get('docker_image', '')
        bundle_url = task_args['bundle_url']
        stdout_url = task_args['stdout_url']
        stderr_url = task_args['stderr_url']
        output_url = task_args['output_url']
        detailed_results_url = task_args['detailed_results_url']
        private_output_url = task_args['private_output_url']

        execution_time_limit = task_args['execution_time_limit']
        # container = task_args['container_name']
        is_predict_step = task_args.get("predict", False)
        secret = task_args['secret']
        root_dir = None
        current_dir = os.getcwd()
        temp_dir = os.environ.get('SUBMISSION_TEMP_DIR', '/tmp/codalab')
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
            # Create temporary directory for the run
            root_dir = tempfile.mkdtemp(dir=temp_dir)
            os.chmod(root_dir, 0777)
            # Fetch and stage the bundles
            logger.info("Fetching bundles...")
            start = time.time()

            bundles = get_bundle(root_dir, 'run', bundle_url)

            logger.info("Metadata: %s" % bundles)

            end = time.time() - start
            logger.info("Fetched bundles in %s", end)
            # Verify we have an input folder: create one if it's not in the bundle.
            input_rel_path = 'input'
            if input_rel_path not in bundles:
                input_dir = join(root_dir, 'run', 'input')
                if os.path.exists(input_dir) == False:
                    os.mkdir(input_dir)
                    os.chmod(input_dir, 0777)
            # Verify we have a program
            prog_rel_path = 'program'
            if prog_rel_path not in bundles:
                raise Exception("Program bundle is not available.")

            prog_info = bundles[prog_rel_path]
            if prog_info is None:
                raise Exception("Program metadata is not available.")

            prog_cmd_list = []
            if 'command' in prog_info:
                if isinstance(prog_info['command'], type([])):
                    prog_cmd_list = [_.strip() for _ in prog_info['command']]
                else:
                    prog_cmd_list = [prog_info['command'].strip()]
            if len(prog_cmd_list) <= 0:
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
            run_dir = join(root_dir, 'run')
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

            for prog_cmd_counter, prog_cmd in enumerate(prog_cmd_list):
                # Update command-line with the real paths
                logger.info("CMD: %s", prog_cmd)
                prog_cmd = prog_cmd.replace("$program", join(run_dir, 'program')) \
                                    .replace("$input", join(run_dir, 'input')) \
                                    .replace("$output", join(run_dir, 'output')) \
                                    .replace("$tmp", join(run_dir, 'temp')) \
                                    .replace("/", os.path.sep) \
                                    .replace("\\", os.path.sep)
                prog_cmd = prog_cmd.split(' ')
                docker_cmd = [
                    'docker',
                    'run',
                    # Set the right volume
                    '-v', '{0}:{0}'.format(run_dir),
                    # Set the right image
                    docker_image  # if docker_image else 'continuumio/anaconda:4.3.0',
                ]
                prog_cmd = docker_cmd + prog_cmd
                logger.info("Invoking program: %s", " ".join(prog_cmd))

                startTime = time.time()
                timed_out = False

                # Old style of execution
                #
                # prog_cmd = prog_cmd.replace("python", join(run_dir, "/home/azureuser/anaconda/bin/python"))
                # # Run as separate user
                # evaluator_process = Popen(
                #     prog_cmd.split(' '),
                #     preexec_fn=demote(),  # this pre-execution function drops into a lower user
                #     stdout=stdout,
                #     stderr=stderr,
                #     env=os.environ
                # )

                evaluator_process = Popen(
                    prog_cmd,
                    stdout=stdout,
                    stderr=stderr,
                    env=os.environ
                )

                logger.info("Started process, pid=%s" % evaluator_process.pid)

                time_difference = time.time() - startTime
                signal.signal(signal.SIGALRM, alarm_handler)
                signal.alarm(int(math.fabs(math.ceil(execution_time_limit - time_difference))))

                exit_code = None

                logger.info("Checking process, exit_code = %s" % exit_code)

                try:
                    while exit_code == None:
                        time.sleep(1)
                        exit_code = evaluator_process.poll()
                except (ValueError, OSError):
                    pass  # tried to communicate with dead process
                except ExecutionTimeLimitExceeded:
                    exit_code = -1
                    logger.info("Killed process for running too long!")
                    stderr.write("Execution time limit exceeded!")
                    evaluator_process.kill()
                    timed_out = True

                signal.alarm(0)

                logger.info("Exit Code: %d", exit_code)

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

            stdout.close()
            stderr.close()

            logger.info("Saving output files")

            put_blob(stdout_url, stdout_file)
            put_blob(stderr_url, stderr_file)

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
