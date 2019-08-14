# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from common.models import DimIndustry, DimBrand, DimBrandCategory, DimSalesPoint, Report, DimCategory, DimPlatform
from itertools import groupby
from operator import itemgetter
import apps.apis as apps_apis


def get_user_info(user):
    user_dict = {
        "username": user.username,
        "corporation": user.corporation,
        "industry": user.industry_id,
        "industry_name": DimIndustry.objects.get(id=user.industry_id).name,
        "category": user.category_id,
        "category_name": DimCategory.objects.get(id=user.category_id).name,
        "brand": user.brand_id,
        "brand_name": DimBrand.objects.get(id=user.brand_id).name,
        "is_admin": user.is_admin,
        "user_type": user.user_type,
        "user_type_name": user.get_user_type_display(),
        "role": user.role.name
    }
    return user_dict


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


def get_platform_info():
    platforms_list = list(DimPlatform.objects.all().order_by("parent").values())

    platforms = []
    for k, v in groupby(platforms_list, itemgetter("parent")):
        platforms.append(dict(id=k, name=k, children=apps_apis.del_key_in_ld(list(v), ("parent",))))

    return platforms

