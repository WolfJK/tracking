# coding: utf-8
# __author__: "James"
# from __future__ import unicode_literals
from django.conf.urls import *

urlpatterns = [
    url(r'^user/', include('common.urls')),
    url(r'^apps/', include('apps.urls')),
]
