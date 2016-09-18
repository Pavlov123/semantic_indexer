import json
import logging
import logging.config

from modules.settings import settings
from modules.rabbitmq import channel

logging.config.dictConfig(settings['logging'])

root_logger = logging.getLogger("root")


queue = settings['log-event-queue']
for msg in channel.consume(queue):
    if msg is None:
        break
    method, properties, body = msg
    try:
        call = json.loads(body)
        root_logger.log(
            call['level'],
            call['msg'],
            *call['args'],
            **call['kwargs']
        )
    except:
        logging.error('Failed to log incoming message: %s ' % body.strip())
    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.close()
