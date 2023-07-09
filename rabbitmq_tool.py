from typing import Any
from superagi.tools.base_tool import BaseTool
import pika
import os
import logging
import datetime
import json
from rabbitmq_connection import RabbitMQConnection
from pydantic import BaseModel

class RabbitMQTool(BaseModel):
    name = "RabbitMQ Tool"
    description = "A tool for interacting with RabbitMQ"
    rabbitmq_server: str
    rabbitmq_username: str
    rabbitmq_password: str
    connection_params: Any
    logger: Any
    base_tool: BaseTool

    def __init__(self):
        self.base_tool = BaseTool()  # Initialize the BaseTool instance
        self.rabbitmq_server = os.getenv('RABBITMQ_SERVER', 'localhost')
        self.rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.connection_params = pika.ConnectionParameters(
            host=self.rabbitmq_server,
            credentials=pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_password)
        )
        self.logger = logging.getLogger(__name__)

    def _execute(self, action, parameters):
        self.base_tool._execute(action, parameters)  # Delegate to the BaseTool instance

    def execute(self, action, queue_name, message=None, persistent=False, priority=0, callback=None, consumer_tag=None, delivery_tag=None):
        connection = RabbitMQConnection(self.connection_params, action, queue_name, message, persistent, priority, callback, consumer_tag, delivery_tag)
        return connection.run()

    def send_natural_language_message(self, receiver, content, msg_type="text", priority=0):
        message = {
            "sender": self.name,
            "receiver": receiver,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": msg_type,
            "content": content
        }
        self.execute("send", receiver, json.dumps(message), priority=priority)

    def receive_natural_language_message(self, queue_name):
        raw_message = self.execute("receive", queue_name)
        message = json.loads(raw_message)
        return message["content"]
