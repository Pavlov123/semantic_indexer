import json
import logging

from modules.settings import settings

from modules.rabbitmq import channel


def log(level, msg, *args, **kwargs):
    channel.basic_publish(
        exchange='',
        routing_key=settings['log-event-queue'],
        body=json.dumps({
            'level': level,
            'msg': msg,
            'args': args,
            'kwargs': kwargs,
        }),
    )


def debug(msg, *args, **kwargs):
    log(logging.DEBUG, msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    log(logging.INFO, msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    log(logging.WARNING, msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    log(logging.ERROR, msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    log(logging.CRITICAL, msg, *args, **kwargs)
