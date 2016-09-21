#!/usr/bin/env python
from subprocess import Popen
import time

from modules.rabbitmq import channel
from modules.settings import settings
from modules import async_logger
from random import randint

# Start logging process
session_id = randint(10000000000, 11000000000)  # unique id to identify processes.
print session_id
logging = Popen(['python', 'logger.py', '%d' % session_id])
async_logger.debug(
    'SESSION-%d-STARTED: %s' % (session_id, time.time())
)

web_workers = []
for i in range(0, settings['web-workers']):
    web_workers.append(
        Popen(['python', 'web-worker.py', '%d-%d' % (session_id, i)])
    )

db_workers = []
for i in range(0, settings['db-workers']):
    db_workers.append(
        Popen(['python', 'db-worker.py', '%d-%d' % (session_id, i)])
    )

with open(settings['data-paths']['sparql-endpoints'], 'r') as sparql_source:
    for endpoint in sparql_source:
        channel.basic_publish(
            exchange='',
            routing_key=settings['web-worker-endpoints-queue'],
            body=endpoint,
        )
channel.close()
