# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = (
    url(r"^hello/", include("apps.hello.urls")),
    url(r"^report/", include("apps.report.urls")),
    url(r"^common/", include("apps.common.urls")),
)

