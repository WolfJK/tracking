# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

import traceback
from django.http.response import JsonResponse
from django.http.response import HttpResponse
from enum import Enum
from common.logger import Logger
from common.user import apis as user_apis
from common.exception import NeedCodeException, LockedException
from website.settings import *

logger = Logger.getLoggerInstance()


class HTTP_CODE(Enum):
    OK_200 = 200
    BADREQUEST_400 = 400
    UNAUTHORIZED_401 = 401
    LOCKED_402 = 402
    FORBIDDEN_403 = 403
    NEEDCODE_412 = 412


class MpMiddleware:
    def _build_response_with_code(self, msg, code):
        response = JsonResponse(dict(msg=msg), safe=False)
        response.status_code = code.value
        return response

    def _build_response_with_needcode(self, msg, code, needcode=0):
        response = JsonResponse(dict(msg=msg, needcode=needcode), safe=False)
        response.status_code = code.value
        return response

    def _check_skip_all(self, request):
        if request.path.startswith('/static/'):
            return True

        return False


class GatewayMiddleware(MpMiddleware):
    def process_request(self, request):
        if self._check_skip_all(request):
            return


    def process_exception(self, request, exception):
        logger.error(traceback.format_exc().decode('utf-8'))

        if isinstance(exception, LockedException):
            return self._build_response_with_code(unicode(exception), HTTP_CODE.LOCKED_402)
        elif isinstance(exception, NeedCodeException):
            return self._build_response_with_needcode(unicode(exception), HTTP_CODE.NEEDCODE_412, 1)
        else:
            return self._build_response_with_code(unicode(exception), HTTP_CODE.BADREQUEST_400)

    def process_response(self, request, response):
        if isinstance(response, JsonResponse):
            return response
        elif isinstance(response, HttpResponse):
            if response['Content-type'] == "text/html":
                response = JsonResponse(dict(msg=response.content), safe=False)
                return response
            else:
                return response


class AuthMiddleware(MpMiddleware):
    def process_request(self, request):
        logger.debug("AuthorizationMiddleware.process_request()")

        if self._check_skip_all(request):
            return

        if request.path in SKIP_AUTHORIZATION_URLS:
            return

        if not request.user.is_authenticated():
            return self._build_response_with_code("用户未登录或登录已失效", HTTP_CODE.UNAUTHORIZED_401)

        if not request.user.is_active:
            return self._build_response_with_code('用户已被禁用，请联系管理员', HTTP_CODE.LOCKED_402)

        if request.user.is_admin:
            return

        if not user_apis.auth_api_url(request):
            return self._build_response_with_code("未授权访问", HTTP_CODE.FORBIDDEN_403)

