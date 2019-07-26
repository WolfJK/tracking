# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

from os.path import join

#域名
ALLOWED_HOSTS = []
DEBUG = False
USE_CATCHED=False

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "kcc",
        "USER": "kcc",
        "PASSWORD": "20190318@MaRcPoInT1202",
        "HOST": "172.19.70.126",
        "PORT": "3306",
    }
}

## REDIS Settings
REDIS_IP = "172.19.70.126"
REDIS_PORT = 6379
# SESSION Settings
SESSION_REDIS = {
    'host': REDIS_IP,
    'port': REDIS_PORT,
    'db': 0,
    'prefix': 'SESSION',
    'socket_timeout': 1,
    'retry_on_timeout': False
}

## LOGGER Settings
LOG_DIR = "/var/log/tracking_v1"
LOGGER_PATH = join(LOG_DIR, "tracking_v1.log")
ERROR_LOGGER_PATH = join(LOG_DIR, "tracking_v1_error.log")
LOGGER_SYSTEM_NAME = "TRACKING_V1"
LOGGER_TAG = "TRACKING_APP"