# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = (
    url(r"^report/", include("apps.report.urls")),
    url(r"^common/", include("apps.commons.urls")),
    url(r"^opinion-analysis/", include("apps.opinion_analysis.urls")),
)

