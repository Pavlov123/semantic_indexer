import pika

from .settings import settings

connection = pika.BlockingConnection(pika.URLParameters(
    'amqp://%s:%s@127.0.0.1:5672/%s' % (
        settings['rabbitmq']['user'],
        settings['rabbitmq']['pass'],
        settings['rabbitmq']['vhost']
    )
))

channel = connection.channel()

channel.queue_declare(queue=settings['web-worker-endpoints-queue'])
channel.queue_declare(queue=settings['log-event-queue'])
channel.queue_declare(queue=settings['db-queue'])
channel.basic_qos(prefetch_count=1)


def create_exchange_queue(exchange):
    result = channel.queue_declare(exclusive=True)
    queue = result.method.queue
    channel.queue_bind(
        exchange=exchange, queue=queue
    )
    return queue
