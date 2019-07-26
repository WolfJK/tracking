# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

from django.http.response import *
from DjangoCaptcha import Captcha
import random
from common.logger import Logger
import apis

logger = Logger.getLoggerInstance()


def login(request):
    logger.info("[AUTH]login()")
    session_id = apis.login(request)
    return JsonResponse({"sessionid": session_id})

def logout(request):
    logger.debug("[AUTH]logout()")
    apis.logout(request)
    return JsonResponse({"item": "success"})

def get_user_menus(request):
    menus = apis.Authorization.get_user_menus(request)
    return JsonResponse({"menus": menus})

def get_user_menus_apis(request):
    menus = apis.Authorization.get_user_menus_apis(request)
    return JsonResponse({"menu_apis": menus})

def asign_user(request):
    logger.info("[AUTH]asign_user()")
    username = request.POST.get('username')
    if not username: raise Exception('username cannot be empty.')
    password = request.POST.get('password')
    if not password: raise Exception('password cannot be empty.')
    role_id = request.POST.get('role_id')
    if not role_id: raise Exception('role_id cannot be empty.')

    apis.asign_user(username, password, role_id)

    return JsonResponse({"item": "success"})

def code(request):
    def gene_text():
        source = 'ABCDEFGHKMNPRSTUVWXYZabcdefghkmnpqrstuvwxyz23456789'
        return ''.join(random.sample(list(source), 4))

    ca = Captcha(request)
    ca.words = [gene_text()]
    ca.type = "word"

    return ca.display()