#!/usr/bin/env python
"""
Defines the worker process which handles computations.
"""
import azure
import json
import logging
import logging.config
import os
import shutil
import sys
import tempfile
import time
import traceback
import yaml
from os.path import dirname, abspath, join
from subprocess import Popen, PIPE
from zipfile import ZipFile


# Add codalabtools to the module search path
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

from azure.storage import BlobService
from codalabtools import BaseWorker, BaseConfig
from codalabtools.azure_extensions import AzureServiceBusQueue

logger = logging.getLogger('codalabtools')

class WorkerConfig(BaseConfig):
    """
    Defines configuration properties (mostly credentials) for a worker process.
    """
    def __init__(self, filename='.codalabconfig'):
        super(WorkerConfig, self).__init__(filename)
        self._winfo = self.info['compute-worker']

    def getLoggerDictConfig(self):
        """Gets Dict config for logging configuration."""
        if 'logging' in self._winfo:
            return self._winfo['logging']
        else:
            return super(WorkerConfig, self).getLoggerDictConfig()

    def getAzureStorageAccountName(self):
        """Gets the Azure Storage account name."""
        return self._winfo['azure-storage']['account-name']

    def getAzureStorageAccountKey(self):
        """Gets the Azure Storage account key."""
        return self._winfo['azure-storage']['account-key']

    def getAzureServiceBusNamespace(self):
        """Gets the Azure Service Bus namespace."""
        return self._winfo['azure-service-bus']['namespace']

    def getAzureServiceBusKey(self):
        """Gets the Azure Service Bus key."""
        return self._winfo['azure-service-bus']['key']

    def getAzureServiceBusIssuer(self):
        """Gets the Azure Service Bus issuer."""
        return self._winfo['azure-service-bus']['issuer']

    def getAzureServiceBusQueue(self):
        """Gets the name of the Azure Service Bus queue to listen to."""
        return self._winfo['azure-service-bus']['listen-to']

    def getLocalRoot(self):
        """Gets the path for the local directory where files are staged or None if the path is not provided."""
        return self._winfo['local-root'] if 'local-root' in self._winfo else None

def getBundle(root_path, blob_service, container, bundle_id, bundle_rel_path, max_depth=3):
    """
    be controlled with the max_depth parameter.

    root_path: Path of the local directory under which all files are staged for execution.
    blob_service: Azure BlobService to access the storage account holding the bundles.
    container: Name of Blob container holding the bundles in the specified storage account.
    bundle_id: The ID of the bundle which in this implementation is the path of the Blob
        relative to the container. For example if a bundle is stored in a Blob with URL
        'https://codalab.blob.core.windows.net/bundlecontainer/bundles/1/run.txt' then
        the bundle ID is 'bundles/1/run.txt'.
    bundle_rel_path: Path of the local bundle directory relative to the root directory. For
        example, if root_path is 'C:\\tmp123' and bundle_rel_path is 'run\\program', then the
        program bundle will be located at 'C:\\tmp123\\run\\program'.
    max_depth: An optional argument to limit the depth of recursion when resolving bundle
        dependencies.

    Return value: A dictionary where each key denotes the relative path of a bundle which
        was staged. The value associated with a key is a dictionary representing the bundle's
        metadata. The value may be None if a metadata file was not found. For a valid run,
        the set of keys should contain at the minimum: 'run', 'run\\program' and 'run\\input'.
    """

    def getThem(bundle_id, bundle_rel_path, bundles, depth):
        """Recursively gets the bundles."""
        # download the bundle and save it to a temporary location
        try:
            logger.debug("Getting bundle_id=%s from container=%s" % (container, bundle_id))
            blob = blob_service.get_blob(container, bundle_id)
        except azure.WindowsAzureMissingResourceError:
            #file not found lets None this bundle
            bundles[bundle_rel_path] = None
            return bundles

        bundle_ext = os.path.splitext(bundle_id)[1]
        bundle_file = tempfile.NamedTemporaryFile(prefix='tmp', suffix=bundle_ext, dir=root_path, delete=False)

        logger.debug("Reading from bundle_file.name=%s" % bundle_file.name)

        #take our temp file and write whatever is it form the blob
        with open(bundle_file.name, 'wb') as f:
            f.write(blob)
        # stage the bundle directory
        bundle_path = join(root_path, bundle_rel_path)
        metadata_path = join(bundle_path, 'metadata')

        if bundle_ext == '.zip':
            with ZipFile(bundle_file.file, 'r') as z:
                z.extractall(bundle_path)
        else:
            os.mkdir(bundle_path)
            shutil.copyfile(bundle_file.name, metadata_path)
        # read the metadata if it exists
        bundle_info = None
        if os.path.exists(metadata_path):
            with open(metadata_path) as mf:
                bundle_info = yaml.load(mf)
        bundles[bundle_rel_path] = bundle_info
        # get referenced bundles

        if (bundle_info is not None) and (depth < max_depth):
            for (k, v) in bundle_info.items():
                if k not in ("description", "command", "exitCode", "elapsedTime", "stdout", "stderr", "submitted-by", "submitted-at"):
                    if isinstance(v, str):
                        getThem(v, join(bundle_rel_path, k), bundles, depth + 1)

        return bundles

    return getThem(bundle_id, bundle_rel_path, {}, 0)

def _send_update(queue, task_id, status, extra=None):
    """
    Sends a status update about the running task.

    queue: The Queue to send the update to.
    id: The task ID.
    status: The new status for the task. One of 'running', 'finished' or 'failed'.
    """
    task_args = {'status': status}
    if extra:
        task_args['extra'] = extra
    body = json.dumps({'id': task_id,
                       'task_type': 'run_update',
                       'task_args': task_args})
    queue.send_message(body)

def _upload(blob_service, container, blob_id, blob_file, content_type = None):
    """
    Uploads a Blob.

    blob_service: A BlobService object.
    container: Name of the container to uplaod the Blob to.
    blob_id: Name of the Blob relative to the container.
    blob_file: Path of the local file to upload as a BlockBlob.
    """
    with open(blob_file, 'rb') as f:
        blob = f.read()
        blob_service.put_blob(container, blob_id, blob, x_ms_blob_type='BlockBlob', x_ms_blob_content_type=content_type)

def get_run_func(config):
    """
    Returns the function to invoke in order to do a run given the specified configuration.

    config: A pre-configured instance of WorkerConfig.

    Returns: The function to invoke given a Run task: f(task_id, task_args)
    """

    def run(task_id, task_args):
        """
        Performs a Run.

        task_id: The tracking ID for this task.
        task_args: The input arguments for this task:
        """
        run_id = task_args['bundle_id']
        execution_time_limit = task_args['execution_time_limit']
        container = task_args['container_name']
        reply_to_queue_name = task_args['reply_to']
        is_predict_step = task_args["predict"]
        queue = AzureServiceBusQueue(config.getAzureServiceBusNamespace(),
                                     config.getAzureServiceBusKey(),
                                     config.getAzureServiceBusIssuer(),
                                     reply_to_queue_name)
        root_dir = None
        current_dir = os.getcwd()

        try:
            _send_update(queue, task_id, 'running')
            # Create temporary directory for the run
            root_dir = tempfile.mkdtemp(dir=config.getLocalRoot())
            # Fetch and stage the bundles
            blob_service = BlobService(config.getAzureStorageAccountName(),
                                       config.getAzureStorageAccountKey())
            bundles = getBundle(root_dir, blob_service, container, run_id, 'run')
            # Verify we have an input folder: create one if it's not in the bundle.
            input_rel_path = join('run', 'input')
            if input_rel_path not in bundles:
                input_dir = join(root_dir, 'run', 'input')
                if os.path.exists(input_dir) == False:
                    os.mkdir(input_dir)
            # Verify we have a program
            prog_rel_path = join('run', 'program')
            if prog_rel_path not in bundles:
                raise Exception("Program bundle is not available.")
            prog_info = bundles[prog_rel_path]
            if prog_info is None:
                raise Exception("Program metadata is not available.")
            prog_cmd = ""
            if 'command' in prog_info:
                prog_cmd = prog_info['command'].strip()
            if len(prog_cmd) <= 0:
                raise Exception("Program command is not specified.")
            # Create output folder
            output_dir = join(root_dir, 'run', 'output')
            if os.path.exists(output_dir) == False:
                os.mkdir(output_dir)
            # Create temp folder
            temp_dir = join(root_dir, 'run', 'temp')
            if os.path.exists(temp_dir) == False:
                os.mkdir(temp_dir)
            # Report the list of folders and files staged
            #
            # Invoke custom evaluation program
            run_dir = join(root_dir, 'run')
            os.chdir(run_dir)
            os.environ["PATH"] += os.pathsep + run_dir + "/program"
            logger.debug("Execution directory: %s", run_dir)
            # Update command-line with the real paths
            logger.debug("CMD: %s", prog_cmd)
            prog_cmd = prog_cmd.replace("$program", join('.', 'program')) \
                                .replace("$input", join('.', 'input')) \
                                .replace("$output", join('.', 'output')) \
                                .replace("$tmp", join('.', 'temp')) \
                                .replace("/", os.path.sep) \
                                .replace("\\", os.path.sep)
            logger.debug("Invoking program: %s", prog_cmd)

            if is_predict_step:
                stdout_file_name = 'prediction_stdout_file.txt'
                stderr_file_name = 'prediction_stderr_file.txt'
            else:
                stdout_file_name = 'stdout.txt'
                stderr_file_name = 'stderr.txt'

            stdout_file = join(run_dir, stdout_file_name)
            stderr_file = join(run_dir, stderr_file_name)
            startTime = time.time()
            exit_code = None
            timed_out = False

            stdout = open(stdout_file, "a")
            stderr = open(stderr_file, "a")

            evaluator_process = Popen(prog_cmd.split(' '), stdout=PIPE, stderr=PIPE)

            while exit_code is None:
                exit_code = evaluator_process.poll()

                # time in seconds
                if exit_code is None and time.time() - startTime > execution_time_limit:
                    exit_code = -1
                    logger.info("Killed process for running too long!")
                    stderr.write("Execution time limit exceeded!")
                    evaluator_process.kill()
                    timed_out = True
                    break
                else:
                    time.sleep(.1)

            stdout.write(evaluator_process.stdout.read())
            stderr.write(evaluator_process.stderr.read())
            stdout.close()
            stderr.close()

            logger.debug("Exit Code: %d", exit_code)
            endTime = time.time()
            elapsedTime = endTime - startTime
            prog_status = {
                'exitCode': exit_code,
                'elapsedTime': elapsedTime
            }
            with open(join(output_dir, 'metadata'), 'w') as f:
                f.write(yaml.dump(prog_status, default_flow_style=False))

            logger.debug("Saving output files")
            stdout_id = "%s/%s" % (os.path.splitext(run_id)[0], stdout_file_name)
            _upload(blob_service, container, stdout_id, stdout_file)
            stderr_id = "%s/%s" % (os.path.splitext(run_id)[0], stderr_file_name)
            _upload(blob_service, container, stderr_id, stderr_file)

            private_dir = join(output_dir, 'private')
            if os.path.exists(private_dir):
                logger.debug("Packing private results...")
                private_output_file = join(root_dir, 'run', 'private_output.zip')
                shutil.make_archive(os.path.splitext(private_output_file)[0], 'zip', output_dir)
                private_output_id = "%s/private_output.zip" % (os.path.splitext(run_id)[0])
                _upload(blob_service, container, private_output_id, private_output_file)
                shutil.rmtree(private_dir)

            # Pack results and send them to Blob storage
            logger.debug("Packing results...")
            output_file = join(root_dir, 'run', 'output.zip')
            shutil.make_archive(os.path.splitext(output_file)[0], 'zip', output_dir)
            output_id = "%s/output.zip" % (os.path.splitext(run_id)[0])
            _upload(blob_service, container, output_id, output_file)

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
                            html_file_id = "%s/html/%s" % (os.path.splitext(run_id)[0],"detailed_results.html")
                            print "file_to_upload:%s" % file_to_upload
                            _upload(blob_service, container, html_file_id, file_to_upload, "html")
                            html_found = True

            # check if timed out AFTER output files are written! If we exit sooner, no output is written
            if timed_out:
                logger.exception("Run task timed out (task_id=%s).", task_id)
                _send_update(queue, task_id, 'failed')
            elif exit_code != 0:
                logger.exception("Run task exit code non-zero (task_id=%s).", task_id)
                _send_update(queue, task_id, 'failed', extra={'traceback': open(stderr_file).read()})
            else:
                _send_update(queue, task_id, 'finished')
        except Exception:
            logger.exception("Run task failed (task_id=%s).", task_id)
            _send_update(queue, task_id, 'failed', extra={'traceback': traceback.format_exc()})

        # comment out for dev and viewing of raw folder outputs.
        if root_dir is not None:
            # Try cleaning-up temporary directory
            try:
                os.chdir(current_dir)
                shutil.rmtree(root_dir)
            except:
                logger.exception("Unable to clean-up local folder %s (task_id=%s)", root_dir, task_id)
    return run

def main():
    """
    Setup the worker and start it.
    """
    config = WorkerConfig()

    logging.config.dictConfig(config.getLoggerDictConfig())

    # queue to listen to for notifications of tasks to perform
    queue = AzureServiceBusQueue(config.getAzureServiceBusNamespace(),
                                 config.getAzureServiceBusKey(),
                                 config.getAzureServiceBusIssuer(),
                                 config.getAzureServiceBusQueue())
    # map task type to function to accomplish the task
    vtable = {
        'run' : get_run_func(config)
    }
    # create and start the worker
    worker = BaseWorker(queue, vtable, logger)
    logger.info("Starting compute worker.")
    worker.start()

if __name__ == "__main__":

    main()
