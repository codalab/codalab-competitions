"""
This module defines Windows Azure extensions for CodaLab.
"""

from azure.servicebus import (ServiceBusService,
                              Message)

from codalabtools import (Queue,
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

