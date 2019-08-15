# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

from os.path import join

ALLOWED_HOSTS = ["*"]
DEBUG = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "tracking",
        "USER": "tracking",
        "PASSWORD": "Mp@2019_tracking",
        "HOST": "172.16.1.112",
        "PORT": "3306",
    }
}


## REDIS Settings
REDIS_IP = "172.16.1.112"
REDIS_PORT = 6379

## LOGGER Settings
LOG_DIR = "../../log"
LOGGER_PATH = join(LOG_DIR, "tracking-1.0.log")
ERROR_LOGGER_PATH = join(LOG_DIR, "tracking-1.0_error.log")
LOGGER_SYSTEM_NAME = "Tracking-1.0"
LOGGER_TAG = "Tracking_V1"

# SESSION Settings
SESSION_REDIS = {
    'host': REDIS_IP,
    'port': REDIS_PORT,
    'db': 0,
    'prefix': 'SESSION',
    'socket_timeout': 1,
    'retry_on_timeout': False
    }

# local special
#SESSION_EXPIRE_USER = 15 * 60
USE_CATCHED=False
FAIL_AUTH_MAX_ATTEMPTS = 10
FAIL_AUTH_NEEDCODE_ATTEMPTS = 3

whitelist = ["172.16.1.130", "ddns.marcpoint.com"]

