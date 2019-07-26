# coding: utf-8
# __author__ = u"James"
from __future__ import unicode_literals
from common.models import SmUser
from apis import hash_to_password

class AuthenticationBackend(object):
    def authenticate(self, username, password):
        try:
            user = SmUser.objects.get(username=username)
            hashpassword = hash_to_password(password)  # 密码校验修只是作用与auth校验
            if user.password != hashpassword:
               return None
        except SmUser.DoesNotExist:
            return None

        return user

    def get_user(self, user_id):
        try:
            user = SmUser.objects.get(pk=user_id)
            return user
        except SmUser.DoesNotExist:
            return None