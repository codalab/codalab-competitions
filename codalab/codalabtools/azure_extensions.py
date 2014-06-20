"""
This module defines Windows Azure extensions for CodaLab.
"""
import logging
from time import sleep

from azure import (
    WindowsAzureData,
    WindowsAzureError
)

from azure.storage import (
    _sign_storage_blob_request,
    BlobService,
    StorageServiceProperties)

from azure.servicebus import (
    ServiceBusService,
    Message)

from codalabtools import (
    Queue,
    QueueMessage)

logger = logging.getLogger('codalabtools')

class AzureServiceBusQueueMessage(QueueMessage):
    """
    Implements a QueueMessage backed by a Windows Azure Service Bus Queue Message.
    """
    def __init__(self, queue, message):
        self.queue = queue
        self.message = message
    def get_body(self):
        return self.message.body
    def get_queue(self):
        raise self.queue

class AzureServiceBusQueue(Queue):
    """
    Implements a Queue backed by a Windows Azure Service Bus Queue.
    """

    # Timeout in seconds. receive_message is blocking and returns as soon as one of two
    # conditions occurs: a message is received or the timeout period has elapsed.
    polling_timeout = 60

    def __init__(self, namespace, key, issuer, name):
        self.service = ServiceBusService(service_namespace=namespace, account_key=key, issuer=issuer)
        self.name = name
        self.max_retries = 3
        self.wait = lambda count: 1.0*(2**count)

    def _try_request(self, fn, retry_count=0, fail=None):
        '''Helper to retry request for sending and receiving messages.'''
        try:
            return fn()
        except (WindowsAzureError) as e:
            if retry_count < self.max_retries:
                logger.error("Retrying request after error occurred. Attempt %s of %s.",
                             retry_count+1, self.max_retries)
                wait_interval = self.wait(retry_count)
                if wait_interval > 0.0:
                    sleep(wait_interval)
                return self._try_request(fn, retry_count=retry_count+1, fail=fail)
            else:
                if fail is not None:
                    fail()
                raise e

    def receive_message(self):
        op = lambda: self.service.receive_queue_message(self.name,
                                                        peek_lock=False,
                                                        timeout=self.polling_timeout)
        msg = self._try_request(op)
        return None if msg.body is None else AzureServiceBusQueueMessage(self, msg)

    def send_message(self, body):
        op = lambda: self.service.send_queue_message(self.name, Message(body))
        fail = lambda: logger.error("Failed to send message. Message body is:\n%s", body)
        self._try_request(op, fail=fail)


class CorsRule(WindowsAzureData):
    '''CORS Rule for Windows Azure storage service.'''

    def __init__(self):
        self.allowed_origins = u''
        self.allowed_methods = u''
        self.max_age_in_seconds = 0
        self.exposed_headers = u''
        self.allowed_headers = u''

class Cors(WindowsAzureData):
    '''CORS list of rules for Windows Azure storage service.'''

    def __init__(self):
        self.cors_rule = []

def set_storage_service_cors_properties(account_name, account_key, cors_rules):
    """
    Assigns the specified CORS rules to the specified Blob service.

    blob_service: Target BlobService object.
    cors_rules: A Cors instance specifying the rules to apply.
    """
    blob_svc_props = StorageServiceProperties()
    blob_svc_props.metrics = None
    blob_svc_props.logging = None
    setattr(blob_svc_props, 'cors', cors_rules)

    def request_filter(request, next_filter):
        """ Intercepts request to modify headers."""
        request.headers = [(k, v) for (k, v) in request.headers if k not in ('x-ms-version', 'Authorization')]
        request.headers.append(('x-ms-version', '2013-08-15'))
        request.headers.append(('Authorization', _sign_storage_blob_request(request, account_name, account_key)))
        response = next_filter(request)
        return response

    blob_service = BlobService(account_name, account_key).with_filter(request_filter)
    blob_service.set_blob_service_properties(blob_svc_props)
