# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = patterns(
    'apps.hello.views',
    url(r"^hello-world/$", "hello_world"),
    url(r"^exception/$", "exception"),
    url(r"^needcode-exception/$", "needcode_exception"),
    url(r"^auth-hello/$", "auth_hello"),
    url(r"^auth-hello-2/$", "auth_hello_2"),

)