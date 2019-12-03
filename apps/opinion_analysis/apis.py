# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
import json
from apps.opinion_analysis import sqls
from common.db_helper import DB
from datetime import datetime


def add_monitor_brand(monitor_id, category, brand, time_slot, competitor):
    """
    全品类是空的字典, 竞品必填
    :return:
    """
    brand = json.loads(brand)
    competitor = json.loads(competitor)
    if not monitor_id:  # 新增
        VcMonitorBrand(category_id=category, brand=json.dumps(brand),
                       competitor=json.dumps(competitor), time_slot=time_slot).save()
    else:  # 更新
        monitor_brand = VcMonitorBrand.objects.get(id=monitor_id)
        monitor_brand.competitor = json.dumps(competitor)
        monitor_brand.time_slot = time_slot
        monitor_brand.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        monitor_brand.save()


def delete_monitor_brand(brand_id):
    VcMonitorBrand.objects.filter(id=brand_id).delete()


def search_monitor_brand(brand_name, category_id):
    if not brand_name:
        result = DB.search(sqls.search_monitor_brand_type, {"category_id": category_id})
    else:
        result = DB.search(sqls.search_monitor_brand, {"brand_name": brand_name, "category_id": category_id})
    return result


def get_compete_brand(vc_monitor):
    if isinstance(vc_monitor, list):
        brand_id = vc_monitor[-1].get("id")
        compete = DB.get(sqls.sm_competitor_compete_brand, {"brand_id": brand_id})
        results = json.loads(compete.get("competitors"))
    else:
        compete = DB.get(sqls.vc_monitor_brand_compete, {"brand_id": vc_monitor})
        results = json.loads(compete.get("competitor"))
    return results


def get_all_monitor_card_data(category_id):
    # 按照品类查询所有的品牌id, 计算声量信息
    vcBrands = DB.search(sqls.get_all_brand_id, {"category_id": category_id})
    category = DimCategory.objects.get(id=category_id)
    industry = DimIndustry.objects.get(id=category.industry_id)
    # 计算sov 获取所有竞品或者全品
    for vcBrand in vcBrands:
        brand_name = vcBrand.get("brand_name")
        time_slot = vcBrand.get("time_slot")
        competitors = json.loads(vcBrand.get("competitor"))

        list_compete = list()
        if competitors:  # 有竞品
            for competitor in competitors:
                list_compete.append(competitor.get("name"))
            bracket = join_sql_bracket(list_compete)
            sql = sqls.monitor_data_compete_voice%(bracket, time_slot)
            voice = DB.get(sql, {"brand_name": brand_name, "category_name": category.name})  # 获取竞品声量
            compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        else:  # 全品
            sql = sqls.all_monitor_voice%(time_slot)
            voice = DB.get(sql, {"category_name": category.name})  # 获取全品类声量
            compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        new_sql = sqls.monitor_data_analysis_voice % (time_slot)
        voice = DB.get(new_sql, {"brand_name": brand_name, "category_name": category.name})  # 获取声量
        self_voice = int(voice.get("voice")) if voice.get("voice") else 0
        data_sql = sqls.all_data_card_voice_assert%(time_slot)
        data_assert = DB.search(data_sql, {"brand_name": brand_name, "category_name": category.name})  # 所有的日期数据
        vcBrand.update(competitor=competitors)
        vcBrand.update(data_assert=data_assert)
        vcBrand.update(count_voice=self_voice)
        vcBrand.update(category_name=category.name)
        vcBrand.update(industry_name=industry.name)
        vcBrand.update(compete_voice=compete_voice)
        try:
            # 计算sov
            sov = round(float(self_voice)/float(compete_voice)*100, 2)
        except Exception:
            # raise Exception("竞品声量或者全品声量不能为0")
            sov = 0
        vcBrand.update(sov=sov)
    return vcBrands


def join_sql_bracket(data):
    str_data = ""
    for index, value in enumerate(data):
        if index == 0:
            str_data += "( "
        str_data += "'" + value + "'"
        if index == len(data) - 1:
            str_data += " )"
            break
        str_data += ","
    return str_data