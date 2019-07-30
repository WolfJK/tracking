# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from itertools import chain
from operator import itemgetter
from common.db_helper import DB
from django.db.models import Q
from common.models import DimIndustry, DimBrand, DimBrandCategory, DimSalesPoint, Report


def industry_list():
    '''
    获取 行业列表
    :return:
    '''
    return list(DimIndustry.objects.values("id", "name"))


def brand_list(industry_id):
    '''
    获取 品牌列表
    :param industry_id: 行业 id
    :return:
    '''
    return list(DimBrand.objects.filter(industry_id=industry_id).values("id", "name"))


def category_list(brand_id):
    '''
    获取 品类列表
    :param brand_id: 品牌 id
    :return:
    '''
    return list(DimBrandCategory.objects.filter(brand_id=brand_id).values("category", "category__name"))


def sales_point_list(category_id):
    '''
    传卖点列表
    :param category_id: 品类 id
    :return:
    '''
    return list(DimSalesPoint.objects.filter(category_id=category_id).values("id", "name"))


def report_template_list(user):
    '''
    报告模板列表
    :return:
    '''
    return list(Report.objects.filter(user__corporation=user.corporation).values(
        "id", "name", "title", "tag",
        "monitor_start_date", "monitor_end_date", "platform", "industry", "brand",
        "category", "product_line", "accounts", "sales_point", "remark", "remark"
    ))

