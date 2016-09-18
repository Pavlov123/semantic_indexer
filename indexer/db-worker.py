import json

from modules.settings import settings
from modules.rabbitmq import channel

from modules.database import Resource, Endpoint, Backlink


queue = settings['db-queue']
for msg in channel.consume(queue):
    if msg is None:
        break
    method, properties, body = msg

    posted_message = json.loads(body)
    endpoint = Endpoint.get_or_create(url=posted_message['endpoint'])
    for iri, count in posted_message['resources']:
        resource = Resource.get_or_create(uri=iri)
        backlink = Backlink.get_or_create(
            resource=resource[0], endpoint=endpoint[0]
        )
        Backlink.update(count=Backlink.count + count) \
                .where(Backlink.id == backlink[0].id) \
                .execute()
    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.close()
