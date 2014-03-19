"""
This module defines Windows Azure extensions for CodaLab.
"""

from azure import (
    WindowsAzureData)

from azure.servicebus import (
    ServiceBusService,
    Message)

from codalabtools import (
    Queue,
    QueueMessage)

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

    def receive_message(self):
        msg = self.service.receive_queue_message(self.name, peek_lock=False, timeout=self.polling_timeout)
        return None if msg.body is None else AzureServiceBusQueueMessage(self, msg)

    def send_message(self, body):
        self.service.send_queue_message(self.name, Message(body))


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

def set_storage_service_cors_properties(blob_service, cors_rules):
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
        request.headers = [(k,v) for (k,v) in request.headers if k not in ('x-ms-version', 'Authorization')]
        request.headers.append(('x-ms-version', '2013-08-15'))
        request.headers.append(('Authorization', _sign_storage_blob_request(request, account_name, account_key)))
        response = next_filter(request)
        return response

    blob_service = BlobService(account_name, account_key).with_filter(request_filter)
    blob_service.set_blob_service_properties(blob_svc_props)
