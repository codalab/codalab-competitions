"""
This module defines Windows Azure extensions for CodaLab.
"""
import logging
from time import sleep

from azure import WindowsAzureError

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

    def __init__(self, namespace, key, issuer, shared_access_key_name, shared_access_key_value, name):
        self.service = ServiceBusService(service_namespace=namespace, account_key=key,
                                         issuer=issuer, shared_access_key_name=shared_access_key_name,
                                         shared_access_key_value=shared_access_key_value)
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

