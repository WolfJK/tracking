# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")


application = get_wsgi_application()


