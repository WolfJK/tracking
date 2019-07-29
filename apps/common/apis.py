# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from itertools import chain
from operator import itemgetter
from common.db_helper import DB
from django.db.models import Q
from common.models import DimIndustry, DimBrand


def industry_list():
    '''
    获取 行业列表
    :return:
    '''
    return list(DimIndustry.objects.values("id", "name"))


def brand_list(industry_id, brand_name):
    '''
    获取 品牌列表
    :param industry_id: 行业 id
    :param brand_name:  模糊搜索 品牌
    :return:
    '''
    return list(DimBrand.objects.filter(industry_id=industry_id, name__contains=brand_name).values("id", "name"))

