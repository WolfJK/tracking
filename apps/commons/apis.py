# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from common.models import DimIndustry, DimBrand, DimBrandCategory, DimSalesPoint, Report, DimCategory, \
    DimPlatform, SmCompetitor
from django.db.models import F, Q, Value, CharField
from django.db.models.functions import Concat
from itertools import groupby
from operator import itemgetter
import apps.apis as apps_apis
import json
from common.db_helper import DB
import copy
import sqls


def get_user_info(user):
    user_dict = {
        "username": user.username,
        "user_id": user.id,
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


def brand_list(category_id):
    '''
    获取 品牌列表【仅顶级品牌】
    :param category_id: 品类 id
    :return:
    '''
    # , Value("_", output_field=models.CharField())
    brands = DimBrandCategory.objects.filter(category_id=category_id, brand__parent__isnull=True)\
        .values("brand", "brand__name", "brand__parent")\
        .annotate(
        id=Concat(F("brand__id"), Value("_", output_field=CharField()), F("brand__name"), output_field=CharField()),
        name=F("brand__name"),
        parent=F("brand__parent")
    ).values("id", "name", "parent")
    all_brand = [list(brands)]

    get_child_brand_list(brands.values_list("id", flat=True), all_brand)

    return group_brand(all_brand)


def get_child_brand_list(brand_ids, all_brand):
    '''
    获取子品牌
    :param brand_ids:
    :param all_brand:
    :return:
    '''
    childs = DimBrand.objects.filter(parent__in=brand_ids).values("id", "name", "parent")
    if len(childs) > 0:
        all_brand.append(list(childs))
        get_child_brand_list(childs.values_list("id", flat=True), all_brand)


def group_brand(all_brand):
    '''
    将 品牌 列表, 组合成级联形式
    :param all_brand:
    :return:
    '''
    for i in range(len(all_brand) - 1, 0, -1):
        brands = all_brand[i]
        brands.sort(key=itemgetter("parent"))

        child_map = {k: list(v) for k, v in groupby(brands, itemgetter("parent"))}

        for brand in all_brand[i-1]:
            if child_map.has_key(brand["id"]):
                brand.update(child=child_map.pop(brand["id"]))

    return all_brand[0]


def category_list(industry_id):
    '''
    获取 品类列表
    :param industry_id: 行业 id
    :return:
    '''
    return list(DimCategory.objects.filter(industry_id=industry_id).values("id", "name"))


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
    return list(Report.objects.filter(user__corporation=user.corporation, delete=False, status=0).values(
        "id", "name", "title", "tag",
        "monitor_start_date", "monitor_end_date", "platform", "industry", "brand_id",
        "category", "product_line", "accounts", "sales_points", "remark", "remark"
    ))


def get_platform_info():
    platforms_list = list(DimPlatform.objects.all().order_by("parent").values())

    platforms = []
    for k, v in groupby(platforms_list, itemgetter("parent")):
        platforms.append(dict(id=k, name=k, children=apps_apis.del_key_in_ld(list(v), ("parent",))))

    return platforms


def get_vc_platform(type):
    '''
    获取 声量舆情监测的品牌列表
    :param type: bbv、dsm
    :return:
    '''
    platforms = DimPlatform.objects.filter(visible=True).values("id", "name")

    q = Q(parent="母垂")
    if type == "dsm":
        q = ~q

    return list(platforms.filter(q))


def competitor_list(param, user):
    '''
    设置, 竞品列表
    :param param:
    :param user:
    :return:
    '''
    params = dict(queue_filter=param.get("queue_filter", ''), user_id=user.id)
    data = DB.search(sqls.competitor_list, params)
    map(lambda x: x.update(
        competitors=json.loads(x["competitors"]),
        brand=json.loads(x["brand"]),
    ), data)

    return data


def competitor_save(param, user):
    '''
    设置, 添加 主要竞品
    :param param:
    :param user:
    :return:
    '''

    param.update(user=user, brand=json.dumps(param["brand"]), competitors=json.dumps(param["competitors"]))
    param_filter = copy.deepcopy(param)
    param_filter.pop("competitors")

    if len(SmCompetitor.objects.filter(**param_filter)) > 0:
        raise Exception("该品牌的 竞品列表已经存在")

    SmCompetitor(**param).save()


def competitor_get(param, user):
    '''
    设置, 获取单个 主要竞品的详细信息
    :param param:
    :param user:
    :return:
    '''
    competitor = SmCompetitor.objects.filter(id=param["id"], user=user)
    if len(competitor) == 0:
        raise Exception("记录不存在")

    competitor = list(competitor.annotate(industry_id=F("category__industry_id"))
                      .values("id", "industry_id", "category_id", "brand", "competitors"))[0]

    competitor["competitors"] = json.loads(competitor["competitors"])
    competitor["brand"] = json.loads(competitor["brand"])

    return competitor


def competitor_del(param, user):
    '''
    设置 删除 指定的 主要竞品
    :param param:
    :param user:
    :return:
    '''
    competitor = SmCompetitor.objects.filter(id=param["id"], user=user)
    if len(competitor) == 0:
        raise Exception("记录不存在 或 无权限删除")

    competitor[0].delete()

