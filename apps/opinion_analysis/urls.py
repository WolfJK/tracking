# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.conf.urls import url, patterns
import views

urlpatterns = patterns("apps.opinion_analysis.views",

   # 舆情分析 卡片页

   url(r"^add-monitor-brand/$", views.add_monitor_brand),
   url(r"^search-monitor-brand/$", views.search_monitor_brand),
   url(r"^delete-monitor-brand/$", views.delete_monitor_brand),
   url(r"^data-monitor-analysis/$", views.data_monitor_analysis),


   # 舆请分析详情页

   url(r"^whole-net-analysis/$", views.whole_net_analysis),
   url(r"^bbv-analysis/$", views.bbv_analysis),
   url(r"^coffee-media-analysis/$", views.coffee_media_analysis),
   url(r"^milk-media-analysis/$", views.milk_media_analysis),


   # 活动定位
   url(r"^ao-activity-tag-list/$", views.ao_activity_tag_list),
   url(r"^ao-volume-trend/$", views.ao_volume_trend),
   url(r"^ao-keywords-cloud/$", views.ao_keywords_cloud),
   url(r"^ao-activity-content/$", views.ao_activity_content),
)
