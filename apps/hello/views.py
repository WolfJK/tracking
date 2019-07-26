# coding: utf-8

from __future__ import unicode_literals

from django.http.response import *
from common.logger import Logger
from common.exception import *

logger = Logger.getLoggerInstance()

def hello_world(request):
    logger.info("hello")
    return HttpResponse("hello")

def exception(request):
    logger.error("exception")
    raise Exception("hello.exception")


def needcode_exception(request):
    logger.error("needcode_exception")
    raise NeedCodeException("Need code.")

def auth_hello(request):
    logger.info("auth_hello")
    return HttpResponse("auth_hello")

def auth_hello_2(request):
    logger.info("auth_hello_2")
    return HttpResponse("auth_hello_2")