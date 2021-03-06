# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.conf.urls import url, patterns
import views

urlpatterns = patterns("apps.report.views",
    url(r"^report-config-list/$", views.report_config_list),
    url(r"^report-config-delete/$", views.report_config_delete),
    url(r"^report-config-create/$", views.report_config_create),
    url(r"^report-config-edit/$", views.report_config_edit),
    url(r"^report-details/$", views.report_details),
    url(r"^report-unscramble-save/$", views.report_unscramble_save),
    url(r"^activity-contrast/$", views.activity_contrast),
    url(r"^activity-contrast-history/$", views.activity_contrast_history),
    url(r"^get-competitor/$", views.get_competitor),

    url(r"^report-common-info/$", views.report_common_info),
    url(r"^report-config-cancel/$", views.report_config_cancel),
    url(r"^upload/$", views.upload_account),
    url(r"^download/$", views.download_account),
    url(r"^download-panel/$", views.download_panel),

    url(r"^update-report/$", views.update_report),
    url(r"^get-report/$", views.get_report),

)
