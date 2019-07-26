# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class SmApi(models.Model):
    name = models.CharField(max_length=32, help_text="接口名称")
    url = models.CharField(max_length=64, help_text="接口名称")

    class Meta:
        db_table = "sm_api"

    def __str__(self):
        return self.name


class SmMenu(models.Model):
    name = models.CharField(max_length=32, help_text="菜单名称")
    code = models.CharField(max_length=32, help_text="菜单编号")
    apis = models.ManyToManyField(to='SmApi', blank=True, db_constraint=False)

    class Meta:
        db_table = "sm_menu"

    def __str__(self):
        return self.name


class SmRole(models.Model):
    name = models.CharField(max_length=32, help_text="角色名称")
    menus = models.ManyToManyField(to='SmMenu', blank=True)

    class Meta:
        db_table = "sm_role"

    def __str__(self):
        return self.name

class SmUser(AbstractBaseUser):
    username = models.CharField(help_text="用户名", max_length=32, unique=True)
    is_active = models.BooleanField(help_text="是否可用", default=True)
    is_admin = models.BooleanField(help_text="是否是管理员", default=False)
    role = models.ForeignKey(SmRole, help_text="角色", on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = "sm_user"

    def __str__(self):
        return self.username
