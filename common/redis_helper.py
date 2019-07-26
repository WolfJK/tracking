# coding: utf8
# __author__ = "Rich"
from __future__ import unicode_literals

from website.settings import *
from common.logger import Logger
import redis
import json

logger = Logger.getLoggerInstance()


class REDIS:
    _redis = None

    @classmethod
    def getRedis(cls):
        if not cls._redis:
            host = SESSION_REDIS.get("host")
            port = SESSION_REDIS.get("port")
            cls._redis = redis.Redis(host=host, port=port)

        return cls._redis

    @classmethod
    def get(cls, key, default=None):
        cls.getRedis()
        # do
        value = cls._redis.get(key)
        try:
            value = json.loads(value)
        except:
            pass

        return value if value else default

    @classmethod
    def set(cls, key, value, expire=None):
        cls.getRedis()

        if isinstance(value, list) or isinstance(value, dict):
            value = json.dumps(value)

        cls._redis.set(key, value, expire)

    @classmethod
    def ttl(cls, key):
        cls.getRedis()
        value = cls._redis.ttl(key)
        return value if value else 0
