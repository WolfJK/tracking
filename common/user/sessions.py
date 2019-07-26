# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

from common.redis_helper import REDIS
from common.logger import Logger
from website.settings import *

logger = Logger.getLoggerInstance()

def get_resid_session_key(user_key, key):
    SESSION_PREFIX = SESSION_REDIS.get("prefix")
    return '{}:{}:{}'.format(SESSION_PREFIX, key, user_key)

def get_user_attempts(username):
    key = get_resid_session_key(username, FAIL_AUTH_ATTEMPTS_KEY)
    return int(REDIS.get(key, 0)), int(REDIS.ttl(key))

def update_user_attempts(username, attempts):
    key = get_resid_session_key(username, FAIL_AUTH_ATTEMPTS_KEY)
    return REDIS.set(key, attempts, FAIL_AUTH_ATTEMPTS_EXPIRE)