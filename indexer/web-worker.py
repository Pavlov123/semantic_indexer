#!/usr/bin/env python
import os
import sys
import json
import re
import time
from urlparse import urlparse
from collections import defaultdict

import sparql

from modules import async_logger
from modules.rabbitmq import channel

from modules.settings import settings


class PartialRegistry(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._matches = defaultdict(int)

    def add_tuple(self, subject, verb, object_):
        if isinstance(subject, sparql.IRI):
            self.process_iri(subject.value)

        if isinstance(object_, sparql.IRI):
            self.process_iri(object_.value)

    def process_iri(self, iri):
        if not re.match(r'^http.+', iri):
            return

        domain = urlparse(iri).netloc.split(':')[0]
        if re.match(r'.*dbpedia.org$', domain):
            self._matches[iri] += 1

    def serialize(self):
        return {
            'endpoint': self.endpoint,
            'resources': list(self._matches.items()),
        }

    def save(self):
        if len(self._matches):
            channel.basic_publish(
                exchange='',
                routing_key=settings['db-queue'],
                body=json.dumps(self.serialize()),
            )

try:
    worker_id = 'WEB-WORKER-%d-(%s)' % (os.getpid(), sys.argv[1])
    async_logger.info('%s-STARTED: %s' % (worker_id, time.time()))
    # Create endpoints handling.
    endpoint_connections = {}
    endpoints_queue = settings['web-worker-endpoints-queue']

    queue = settings['web-worker-endpoints-queue']
    for msg in channel.consume(queue):
        if msg is None:
            break
        method, properties, body = msg
        endpoint = body.strip()
        channel.basic_ack(delivery_tag=method.delivery_tag)
        sparql_endpoint = sparql.Service(endpoint, "utf-8", "GET")
        offset = 0
        limit = 1000

        query = 'select * where {?s ?p ?o} offset %d limit %d'
        async_logger.info(
            '%s-ENDPOINT-BEGIN: "%s"' % (worker_id, endpoint)
        )
        try:
            results = sparql_endpoint.query(query % (offset, limit))\
                                     .fetchall()
            while results:
                partial_registry = PartialRegistry(endpoint)
                offset += limit
                for row in results:
                    partial_registry.add_tuple(*row)
                partial_registry.save()
                t1 = time.time()
                results = sparql_endpoint.query(query % (offset, limit)) \
                                         .fetchall()
                async_logger.debug('%s-ENDPOINT-RECORDS-PROCESSED: %s %d' % (
                    worker_id, endpoint, offset
                ))
                async_logger.debug(
                    '%s-ENDPOINT-LATENCY: %s' % (worker_id, time.time() - t1)
                )
        except Exception as e:
            async_logger.error(
                '%s-ENDPOINT-ERROR: endpoint: (%s)  error: %s' %
                (worker_id, endpoint, e)
            )
            continue
        async_logger.info(
            '%s-ENDPOINT-COMPLETE: "%s"' % (worker_id, endpoint)
        )
except Exception as e:
    async_logger.info('%s-ERROR: "%s"' % (worker_id, e))
    raise
finally:
    async_logger.info('%s-CLOSING: %s' % (worker_id, time.time()))
    channel.close()
