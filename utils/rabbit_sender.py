import json

import pika


class MessageSender:
    def __init__(self, host, port):
        print(f"Connecting to RabbitMQ at {host}:{port}")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()

    def send_message(self, queue_name, message):
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
        )

    def close(self):
        self.connection.close()
