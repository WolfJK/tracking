# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.conf.urls import url, patterns
import views

urlpatterns = patterns("apps.report.views",
    url(r"^report-config-param/$", views.report_config_param),
    url(r"^report-config-list/$", views.report_config_list),
    url(r"^report-config-delete/$", views.report_config_delete),
    url(r"^report-config-create/$", views.report_config_create),
    url(r"^report-details/$", views.report_details),
    url(r"^report-unscramble-save/$", views.report_unscramble_save),
)
