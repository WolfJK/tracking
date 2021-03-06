# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.conf.urls import url, patterns
import views

urlpatterns = patterns("apps.commons.views",
    url(r"^common-param/$", views.common_param),
    url(r"^brand-list/$", views.brand_list),
    url(r"^category-list/$", views.category_list),
    url(r"^sales-point-list/$", views.sales_point_list),
    url(r"^report-template-list/$", views.report_template_list),
    url(r"^competitor-list/$", views.competitor_list),
    url(r"^competitor-save/$", views.competitor_save),
    url(r"^competitor-get/$", views.competitor_get),
    url(r"^competitor-del/$", views.competitor_del),
)
