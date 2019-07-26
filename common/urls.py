# coding: utf-8
# __author__: "James"
# from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = patterns('common.user.views',
    url(r"^code/$", "code"),
    url(r"^login/$", "login"),
    url(r"^logout/$", "logout"),
    url(r"^get-user-menus/$", "get_user_menus"),
    url(r"^get-user-menus-apis/$", "get_user_menus_apis"),
    url(r"^asign-user/$", "asign_user"),
)
