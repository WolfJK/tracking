# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

import hashlib
from django.contrib import auth
from DjangoCaptcha import Captcha
import common.user.sessions as sessions
from common.db_helper import DB
from common.logger import Logger
from common.models import *
from common.exception import LockedException, NeedCodeException
from website.settings import *
import re

logger = Logger.getLoggerInstance()


def get_user_menus(request):
    logger.debug("auth_apis.get_user_menus()")

    permission_menu_api_list = get_user_menus_apis(request)
    permission_menu_list = []
    for item in permission_menu_api_list:
        m = dict(code=item.get('menu_code'), name=item.get('menu_name'))
        if not m in permission_menu_list:
            permission_menu_list.append(m)

    return permission_menu_list

def auth_api_url(request):
    logger.debug("auth_apis.auth_api_url()")
    permission_menu_api_list = get_user_menus_apis(request)

    permission_api_list = []
    for item in permission_menu_api_list:
        permission_api_list.append(item.get('api_url'))

    return request.path in permission_api_list


def get_user_menus_apis(request):
    logger.debug("auth_apis.get_user_menu_apis()")
    sql = """
            SELECT m.code menu_code, m.name menu_name, a.url api_url
              FROM sm_user u, sm_role r, sm_role_menus rm, sm_menu m, sm_menu_apis ma, sm_api a
             WHERE 1=1
               AND r.id=u.role_id AND rm.smrole_id=r.id AND m.id=rm.smmenu_id AND ma.smmenu_id=m.id AND a.id=ma.smapi_id
               AND u.id={user_id}
            """
    dargs = dict(user_id=request.user.id)
    permission_menu_api_list = DB.search(sql, dargs, use_catched=False)
    return permission_menu_api_list


def login(request):
    logger.debug("auth_apis.login()")

    username = request.POST.get('username')
    password = request.POST.get('password')
    # code = request.POST.get('code')

    if not username: raise Exception('请输入用户名')
    if not password: raise Exception('请输入密码')

    # user_attempts, expire = sessions.get_user_attempts(username)
    # if user_attempts >= FAIL_AUTH_ATTEMPTS_MAX:
    #     raise NeedCodeException('登录失败次数达到{}次, 用户将被锁定{}秒'.format(FAIL_AUTH_ATTEMPTS_MAX, expire))

    # if user_attempts >= FAIL_AUTH_ATTEMPTS_CODE:
    #     if not code:
    #         raise NeedCodeException('请输入验证码')
    #     if not Captcha(request).check(code):
    #         raise NeedCodeException('验证码错误')

    user = auth.authenticate(username=username, password=password)
    if not user:
        # user_attempts = user_attempts + 1
        # sessions.update_user_attempts(username, user_attempts)
        msg = '用户名或密码错误'
        print msg
        # if user_attempts >= FAIL_AUTH_ATTEMPTS_CODE:
        #     raise NeedCodeException(msg)

        raise Exception(msg)

    # if not request.user.is_active():
    #     raise LockedException('用户已被禁用，请联系管理员')

    auth.login(request, user)
    print "login"
    return request.session.session_key


def logout(request):
    logger.debug("auth_apis.logout()")

    # clean old session items
    # sessions.clean_old_session_items(request)

    try:
        # do logout
        auth.logout(request)
    except Exception as e:
        logger.error("auth_apis.logout().error=%s" % (unicode(e)))


# 密码校验移动
def hash_to_password(password):
    #  密码转换hashlib
    salt = "MarcPoint::TRACKING"
    return hashlib.sha256('{}{}'.format(password, salt).encode("utf-8")).hexdigest()


def asign_user(username, password, role_id):
    user = SmUser(username=username, password=password, role_id=role_id)
    encryption_password = hash_to_password(password)
    user.password = encryption_password
    user.save()


def set_owner_password(user, new_password, old_password):
    # 设置密码
    if user.password != hash_to_password(old_password):
        print "旧密码验证错误"
        raise Exception("旧密码验证错误!")

    re_str = "([0-9]+[a-zA-Z]+|[a-zA-Z]+[0-9]+)[0-9a-zA-Z]*"  # 密码包含数字和字母

    pattern = re.compile(re_str)
    new_password = new_password.strip(" ")
    if len(new_password) < 6:
        print "密码长度在6个字符以上"
        raise Exception("密码长度在6个字符以上")
    if not pattern.match(new_password):
        print "密码必须包含中英文和数字"
        raise Exception("密码必须包含中英文和数字")

    user.password = hash_to_password(new_password)
    user.save()




