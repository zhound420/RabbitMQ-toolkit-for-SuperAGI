from pika import PlainCredentials
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import os
import json
import datetime
import pika
import logging
from abc import ABC
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from rabbitmq_connection import RabbitMQConnection

class RabbitMQTool(BaseTool, BaseModel):
    logger: Any
    name: str  # Added this line
    description: str = "Tool that contains various operations to interact with RabbitMQ"

    rabbitmq_server: str = Field(default_factory=lambda: os.getenv('RABBITMQ_SERVER', '192.168.4.194'))
    rabbitmq_username: str = Field(default_factory=lambda: os.getenv('RABBITMQ_USERNAME', 'guest'))
    rabbitmq_password: str = Field(default_factory=lambda: os.getenv('RABBITMQ_PASSWORD', 'guest'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def build_connection_params(self):
        self.logger.debug("Building connection params.")
        credentials = pika.PlainCredentials(self.rabbitmq_username, self.rabbitmq_password)
        self.logger.debug("Connection params built.")
        return pika.ConnectionParameters(host=self.rabbitmq_server, credentials=credentials)

    def _execute(self, *args, **kwargs):
        tool_input = kwargs.get("tool_input", {})
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                tool_input = {"action": "send_message", "queue_name": self.name, "message": tool_input}
        else:
            if "queue_name" not in tool_input or tool_input["queue_name"] is None:
                tool_input["queue_name"] = self.name

        action = tool_input.get("action")
        if action == "send_message":
            queue_name = tool_input.get("queue_name")
            message = tool_input.get("message")
            return self._execute_send(queue_name, message)
        elif action == "receive_message":
            queue_name = tool_input.get("queue_name")
            return self._execute_receive(queue_name)
        else:
            raise ValueError(f"Unknown operation: '{action}'")

    def _execute_send(self, queue_name, message, persistent=False, priority=0):
        try:
            connection_params = self.build_connection_params()
            connection = RabbitMQConnection(
                connection_params,
                operation_type="send",
                queue_name=queue_name,
                message=message,
                persistent=persistent,
                priority=priority
            )
        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"Error while sending message: {str(e)}")
        return connection.run()

    def _execute_receive(self, queue_name):
        try:
            connection_params = self.build_connection_params()
            connection = RabbitMQConnection(connection_params, "receive", queue_name)
            return connection.run()
        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"Error while receiving message: {str(e)}")
            return None

    def send_message(self, receiver_name, message, msg_type="text", priority=0):
        queue_name = receiver_name
        message = {
            "sender": self.name,
            "receiver": queue_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": msg_type,
            "content": message
        }
        tool_input = {
            "action": "send_message",
            "queue_name": queue_name,
            "message": json.dumps(message)
        }
        return self._execute(tool_input=tool_input)

    def receive_message(self, receiver_name):
        queue_name = receiver_name
        tool_input = {
            "action": "receive_message",
            "queue_name": queue_name
        }
        raw_message = self._execute(tool_input=tool_input)
        message = json.loads(raw_message)
        return message["content"]
