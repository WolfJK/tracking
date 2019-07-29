# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.conf.urls import url, patterns
import views

urlpatterns = patterns("apps.common.views",
    url(r"^report-config-param/$", views.report_config_param),
    url(r"^industry-list/$", views.industry_list),
    url(r"^brand-list/$", views.brand_list),
    url(r"^category-list/$", views.category_list),
    url(r"^sales_point-list/$", views.sales_point_list),
    url(r"^throw-account-upload/$", views.throw_account_upload),
)
