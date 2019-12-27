# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
import json
from apps.opinion_analysis import sqls
from common.db_helper import DB
from datetime import datetime
from apps import apis as apps_apis
from django.db.models import Q, F, Sum, Value, IntegerField
import copy
from dateutil.relativedelta import relativedelta
from itertools import groupby
from operator import itemgetter


def add_monitor_brand(request, monitor_id, category, brand, time_slot, competitor):
    """
    全品类是空的字典, 竞品必填
    :return:
    """
    brand = json.loads(brand)
    competitor = json.loads(competitor)
    if len(competitor) > 10:
        raise Exception("竞品的数量不能超过10个")
    if not monitor_id:  # 新增
        VcMonitorBrand(category_id=category, brand=json.dumps(brand), user_id=request.user.id,
                       competitor=json.dumps(competitor), time_slot=time_slot).save()
    else:  # 更新
        monitor_brand = VcMonitorBrand.objects.get(id=monitor_id)
        monitor_brand.competitor = json.dumps(competitor)
        monitor_brand.time_slot = time_slot
        monitor_brand.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        monitor_brand.save()


def delete_monitor_brand(brand_id):
    VcMonitorBrand.objects.filter(id=brand_id).delete()


def search_monitor_brand(user, brand_name, category_id):
    # result = DB.search(sqls.search_monitor_brand_type, {"category_id": category_id})
    result = list(VcMonitorBrand.objects.filter(category_id=category_id, user__corporation=user.corporation).order_by('-create_time').values())
    for brand in result:
        brand_list = json.loads(brand.get("brand"))
        brand_id, brand_name_dian = dispose_brand_name(brand_list)
        brand.update(brand_name=brand_name_dian)
        brand.update(brand_id=brand_id)
    data = list()
    if brand_name:
        for brand in result:
            if brand_name in brand.get('brand_name'):
                result.append(brand)

    return data if brand_name else result


def get_vcbrand_for_name(brand_id):
    try:
        result = DB.get(sqls.search_one_brand, {"brand_id": brand_id})
    except Exception:
        raise Exception("监测id不存在")
    brand_list = json.loads(result.get("brand"))
    brand_id, brand_name_dian = dispose_brand_name(brand_list)
    result.update(brand_name=brand_name_dian)
    result.update(brand_id=brand_id)
    return result


def dispose_brand_name(brand_list):
    """处理品牌格式
    ["478_Wyeth/惠氏", "471_Wyeth/惠氏.illuma/启赋", "474_Wyeth/惠氏.illuma/启赋.启赋蓝钻"]
    """
    try:
        brand_id = brand_list[-1].split('_')[0]
        brand_name = brand_list[-1].split('_')[1]
    except Exception:
        raise Exception("品牌信息异常")

    return brand_id, brand_name


def dispose_competers(competers):
    """处理竞争产品的格式
    ["412_Abbott/雅培-423_Abbott/雅培.雅培喜康力", "412_Abbott/雅培-422_Abbott/雅培.雅培双贝吸", "412_Abbott/雅培-424_Abbott/雅培.雅培小安素"]
    """
    competer_data = list()
    for competer in competers:
        split_data = competer.split("-")[-1]
        brand_name = split_data.split("_")[-1]
        competer_data.append(brand_name)

    return competer_data


def get_all_monitor_card_data(request, brand_name, category_id):
    # 按照品类查询所有的品牌id, 计算声量信息
    try:
        vcBrands = search_monitor_brand(request.user, brand_name, category_id)
    except Exception:
        vcBrands = DB.search(sqls.get_all_brand_id, {"category_id": category_id})
    category = DimCategory.objects.get(id=category_id)
    industry = DimIndustry.objects.get(id=category.industry_id)

    # 计算sov 获取所有竞品或者全品
    for vcBrand in vcBrands:
        time_slot = vcBrand.get("time_slot")
        # 时间周期计算
        date1 = datetime.now().strftime("%Y-%m-%d")
        date2 = (datetime.now() - relativedelta(days=time_slot)).strftime("%Y-%m-%d")
        date_range = [date2, date1]
        vcBrand.update(date_range=date_range)
        range_time = " and date between '{}' and '{}' ".format(date_range[0], date_range[1])

        self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range)
        brand_name = vcBrand.get("brand_name")
        data_sql = sqls.all_data_card_voice_assert %(range_time)
        data_assert = DB.search(data_sql, {"brand_name": brand_name, "category_name": category.name})  # 所有当前品牌的日期数据
        sov = get_all_sov(self_voice, compete_voice)
        append_vc_brand(vcBrand, competitors, data_assert, self_voice, category, industry, compete_voice, sov)
    return vcBrands


def append_vc_brand(vcBrand, competitors, data_assert, self_voice, category, industry, compete_voice, sov):
    vcBrand.update(competitor=competitors)
    vcBrand.update(data_assert=data_assert)
    vcBrand.update(self_voice=self_voice)
    vcBrand.update(category_name=category.name)
    vcBrand.update(industry_name=industry.name)
    vcBrand.update(compete_voice=compete_voice)
    vcBrand.update(sov=sov)


def get_card_voice_sov(vcBrand, category, date_range, type="net"):
    """
    仅按照时间日期获取相应的本品声量，竞品声量或者全品声量
    :param vcBrand:
    :param category:
    :param date_range:
    :return:
    """
    brand_name = vcBrand.get("brand_name")

    date1 = datetime.strptime(date_range[0], "%Y-%m-%d")
    date2 = datetime.strptime(date_range[1], "%Y-%m-%d")
    range_time = " and date between '{}' and '{}' ".format(date_range[0], date_range[1])
    time_slot = abs((date2-date1).days)

    date_previous1 = (date1 - relativedelta(days=1)).strftime("%Y-%m-%d")
    date_previous2 = (date1 - relativedelta(days=time_slot+1)).strftime("%Y-%m-%d")
    range_time_previous = " and date between '{}' and '{}' ".format(date_previous2, date_previous1)

    competitors = json.loads(vcBrand.get("competitor"))
    try:
        list_compete = dispose_competers(competitors)
    except Exception:
        list_compete = list()
        for competitor in competitors:
            list_compete.append(competitor.get("name"))
    bracket_platform = join_sql_bracket([type, ])
    if competitors:  # 有竞品
        list_compete.append(brand_name)  # 所有的竞品加上本品的总数
        bracket = join_sql_bracket(list_compete)
        if type == "net":
            sql = sqls.monitor_data_compete_voice % (bracket, range_time)  # 获取当前
            sql_previous = sqls.monitor_data_compete_voice% (bracket, range_time_previous)  # 获取上个阶段
        elif type == "all":
            # 只是针对深度bbv的全部
            sql = sqls.monitor_data_bbv_all_compete_voice % (bracket, range_time)  # 获取当前
            sql_previous = sqls.monitor_data_bbv_all_compete_voice % (bracket, range_time_previous)  # 获取上个阶段
        elif type in ["微博", "微信"]:  # 微博微信的平台声量是从sass取出来
            sql = sqls.milk_dw_all_compete_voice % (bracket, bracket_platform, range_time)  # 获取当前
            sql_previous = sqls.milk_dw_all_compete_voice % (bracket, bracket_platform, range_time_previous)  # 获取上个阶段
        else:
            # 各个平台的, 包括深度社煤和深度bbv的所有子集
            sql = sqls.monitor_data_classify_compete_voice % (bracket, bracket_platform,  range_time)  # 获取当前
            sql_previous = sqls.monitor_data_classify_compete_voice % (bracket, bracket_platform, range_time_previous)  # 获取上个阶段
        voice = DB.get(sql, {"category_name": category.name})  # 获取竞品声量
        voice_previous = DB.get(sql_previous, {"category_name": category.name})  # 获取竞品声量
        compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        compete_voice_previous = int(voice_previous.get("voice_all")) if voice_previous.get("voice_all") else 0
    else:  # 全品
        if type == 'net':
            sql = sqls.all_monitor_voice % (range_time)
            sql_previous = sqls.all_monitor_voice % (range_time_previous)
        elif type == 'all':
            sql = sqls.bbv_all_sum_voice % (range_time)
            sql_previous = sqls.bbv_all_sum_voice % (range_time_previous)
        elif type in ["微博", "微信"]:
            sql = sqls.milk_platform_classify_voice % (bracket_platform, range_time)  # 获取当前
            sql_previous = sqls.milk_platform_classify_voice % (bracket_platform, range_time_previous)  # 获取上个阶段
        else:
            sql = sqls.bbv_platform_classify_voice % (bracket_platform, range_time)
            sql_previous = sqls.bbv_platform_classify_voice % (bracket_platform, range_time_previous)
        voice = DB.get(sql, {"category_name": category.name})  # 获取全品类声量
        voice_previous = DB.get(sql_previous, {"category_name": category.name})  # 获取全品类声量
        compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        compete_voice_previous = int(voice_previous.get("voice_all")) if voice_previous.get("voice_all") else 0
    if type == 'net':
        new_sql = sqls.monitor_data_analysis_voice % (range_time)
        new_sql_previous = sqls.monitor_data_analysis_voice % (range_time_previous)
    elif type == "all":
        new_sql = sqls.self_brand_bbv_all % (range_time)
        new_sql_previous = sqls.self_brand_bbv_all % (range_time_previous)
    elif type in ["微博", "微信"]:

        new_sql = sqls.self_brand_milk_classify % (bracket_platform, range_time)
        new_sql_previous = sqls.self_brand_milk_classify % (bracket_platform, range_time_previous)
    else:

        new_sql = sqls.self_brand_bbv_classify % (bracket_platform, range_time)
        new_sql_previous = sqls.self_brand_bbv_classify % (bracket_platform, range_time_previous)

    voice = DB.get(new_sql, {"brand_name": brand_name, "category_name": category.name})  # 本品的的声量
    voice_previous = DB.get(new_sql_previous, {"brand_name": brand_name, "category_name": category.name})  # 本品的的声量
    self_voice = int(voice.get("voice")) if voice.get("voice") else 0
    self_voice_previous = int(voice_previous.get("voice")) if voice_previous.get("voice") else 0

    return self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous


def whole_net_analysis(brand_id, date_range):
    """
    :param brand_id:
    :param date_range:
    :return:
    """
    date_range = json.loads(date_range)
    try:
        vcBrand = get_vcbrand_for_name(brand_id)
    except Exception:
        vcBrand = DB.get(sqls.get_brand_by_id, {"brand_id": brand_id})
    category = DimCategory.objects.get(id=vcBrand.get("category_id"))
    industry = DimIndustry.objects.get(id=category.industry_id)
    self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range)
    data_assert, data_voice_histogram, vioce_platform, area_voice, net_keywords, data_radar_classify = get_net_day_month_week_analysis(vcBrand, category, date_range)
    sov = get_all_sov(self_voice, compete_voice)
    append_vc_brand(vcBrand, competitors, data_assert, self_voice, category, industry, compete_voice, sov)
    vcBrand.update(data_voice_histogram=data_voice_histogram)
    vcBrand.update(vioce_platform=vioce_platform)
    vcBrand.update(area_voice=area_voice)
    vcBrand.update(net_keywords=net_keywords)
    vcBrand.update(data_radar_classify=data_radar_classify)
    # 环比
    link_relative(vcBrand, self_voice, sov, self_voice_previous, compete_voice_previous)
    return vcBrand


def get_classify_sov(data_assert, dict_sov_classify):
    """
    获取日周月的sov面积图
    :param vcBrand:
    :param data_assert:
    :return:
    """
    for key, value in data_assert.items():
        for key_type, value_type in value.items():
            for key_sov, value_sov in dict_sov_classify.items():
                if key_type == key_sov:
                    for sov_data in value_sov:
                        for assert_data in value_type:
                            if key_type == "day":
                                key_sov = key_type = "date"
                            if sov_data.get(key_sov) == assert_data.get(key_type):
                                count_assert = assert_data.get('count')
                                count_sov = sov_data.get('count')
                                sov = get_all_sov(count_assert, count_sov)
                                assert_data.update(sov=sov)


def get_round_sov(data_voice_histogram, data_voice_round):
    """
    获取环形图的sov
    :return:
    """
    voice_count = data_voice_round.get("count")
    for histogram in data_voice_histogram:
        histogram_count = histogram.get("count")
        sov = get_all_sov(histogram_count, voice_count)
        histogram.update(sov=sov)
    return data_voice_histogram


def assemble_data(assert_data, type, dict_data):
    for day in assert_data:
        brand_name = day.get("brand")
        if brand_name not in dict_data:
            dict_data.update({brand_name: {"day": [], "month": [], "week": []}})
            dict_data.get(brand_name).get(type).append(day)
        else:
            dict_data.get(brand_name).get(type).append(day)
    return dict_data


def get_data(bracket, competitors, range_time, category, platform='net'):
    """
        # 全品类的时候声量top5+本品 有竞品的时候本品+竞品
        assert_data = {
            "name1": {"day": [], "month": [], "week": []},
            "name2": {"day": [], "month": [], "week": []},
            "name3": {"day": [], "month": [], "week": []},
        }
        :param brand_id:
        :return:
        """
    dict_data = dict()
    dict_sov_classify = dict()  # 分类的声量之和
    bracket_platform = join_sql_bracket([platform, ])

    if platform == 'net':
        sql_day = sqls.compete_day_month_week_voice % (bracket, range_time, "date", "date", "date")
        sql_month = sqls.compete_day_month_week_voice % (bracket, range_time, "month", "month", "month")
        sql_week = sqls.compete_day_month_week_voice % (bracket, range_time, "week", "week", "week")
    elif platform == 'all':  # bbv全部
        sql_day = sqls.bbv_compete_day_month_week_voice % (bracket, range_time, "date", "date", "date")
        sql_month = sqls.bbv_compete_day_month_week_voice % (bracket, range_time, "month", "month", "month")
        sql_week = sqls.bbv_compete_day_month_week_voice % (bracket, range_time, "week", "week", "week")
    elif platform in ["微博", "微信"]:
        sql_day = sqls.ww_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "date", "date", "date")
        sql_month = sqls.ww_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "month", "month", "month")
        sql_week = sqls.ww_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "week", "week", "week")
    else:  # 其他的各个平台
        sql_day = sqls.bbv_platform_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "date", "date", "date")
        sql_month = sqls.bbv_platform_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "month", "month", "month")
        sql_week = sqls.bbv_platform_compete_day_month_week_voice % (bracket, bracket_platform, range_time, "week", "week", "week")
    if competitors:
        if platform == 'net':
            sov_month = sqls.area_of_tend_sov % (bracket, range_time, "month", "month", "month")
            sov_day = sqls.area_of_tend_sov % (bracket, range_time, "date", "date", "date")
            sov_week = sqls.area_of_tend_sov%(bracket, range_time,  "week", "week", "week")
        elif platform == 'all':
            sov_month = sqls.bbv_area_of_tend_sov % (bracket, range_time, "month", "month", "month")
            sov_day = sqls.bbv_area_of_tend_sov % (bracket, range_time, "date", "date", "date")
            sov_week = sqls.bbv_area_of_tend_sov % (bracket, range_time, "week", "week", "week")
        elif platform in ["微博", "微信"]:
            sov_day = sqls.ww_area_of_tend_sov % (bracket, bracket_platform, range_time, "date", "date", "date")
            sov_month = sqls.ww_area_of_tend_sov % (bracket, bracket_platform, range_time, "month", "month", "month")
            sov_week = sqls.ww_area_of_tend_sov % (bracket, bracket_platform, range_time, "week", "week", "week")
        else:
            sov_month = sqls.bbv_platform_area_of_tend_sov % (bracket, bracket_platform, range_time, "month", "month", "month")
            sov_day = sqls.bbv_platform_area_of_tend_sov % (bracket, bracket_platform, range_time, "date", "date", "date")
            sov_week = sqls.bbv_platform_area_of_tend_sov % (bracket, bracket_platform, range_time, "week", "week", "week")
    else:
        if platform == 'net':
            sov_month = sqls.area_of_all_brand_tend_sov % (range_time, "month", "month", "month")
            sov_day = sqls.area_of_all_brand_tend_sov % (range_time, "date", "date", "date")
            sov_week = sqls.area_of_all_brand_tend_sov % (range_time, "week", "week", "week")
        elif platform == 'all':
            sov_month = sqls.bbv_area_all_brand_of_tend_sov % (range_time, "month", "month", "month")
            sov_day = sqls.bbv_area_all_brand_of_tend_sov % (range_time, "date", "date", "date")
            sov_week = sqls.bbv_area_all_brand_of_tend_sov % (range_time, "week", "week", "week")
        elif platform in ["微博", "微信"]:
            sov_day = sqls.ww_area_all_brand_of_tend_sov % (bracket_platform, range_time, "date", "date", "date")
            sov_month = sqls.ww_area_all_brand_of_tend_sov % (bracket_platform, range_time, "month", "month", "month")
            sov_week = sqls.ww_area_all_brand_of_tend_sov % (bracket_platform, range_time, "week", "week", "week")
        else:
            sov_month = sqls.bbv_platform_area_all_brand_of_tend_sov % (bracket_platform, range_time, "month", "month", "month")
            sov_day = sqls.bbv_platform_area_all_brand_of_tend_sov % (bracket_platform, range_time, "date", "date", "date")
            sov_week = sqls.bbv_platform_area_all_brand_of_tend_sov % (bracket_platform, range_time, "week", "week", "week")

    day_assert = DB.search(sql_day, {"category_name": category.name})
    month_assert = DB.search(sql_month, {"category_name": category.name})
    week_assert = DB.search(sql_week, {"category_name": category.name})

    # 日月周的总数 用于计算sov
    day_sov_assert = DB.search(sov_day, {"category_name": category.name})
    month_sov_assert = DB.search(sov_month, {"category_name": category.name})
    week_sov_assert = DB.search(sov_week, {"category_name": category.name})

    dict_sov_classify.update(day=day_sov_assert)
    dict_sov_classify.update(month=month_sov_assert)
    dict_sov_classify.update(week=week_sov_assert)
    assemble_data(day_assert, "day", dict_data)
    assemble_data(month_assert, "month", dict_data)
    assemble_data(week_assert, "week", dict_data)

    get_classify_sov(dict_data, dict_sov_classify)
    return dict_data, dict_sov_classify


def get_data_voice_histogram(bracket, range_time, category, competitors, platform='net'):
    """
    获取声量柱形图和sov环形图的总数和每个平台的声量
    """
    bracket_platform = join_sql_bracket([platform, ])
    if platform == 'net':
        sql_his = sqls.brand_voice_histogram % (bracket, range_time,)
    elif platform == 'all':
        sql_his = sqls.bbv_brand_voice_histogram % (bracket, range_time,)
    elif platform in ["微博", "微信"]:
        sql_his = sqls.brand_ww_voice_histogram % (bracket, bracket_platform, range_time,)
    else:
        sql_his = sqls.bbv_platform_brand_voice_histogram % (bracket, bracket_platform, range_time,)
    # 有竞争产品的时候(环形图的总数是竞争产品的全部声量 全品类的时候环形图的总数是全部的声量其余的剩下的用其他来表示)
    if competitors:
        if platform == 'net':
            sql_round = sqls.round_sum_sov % (bracket, range_time)  # 声量总和计算sov环形图
        elif platform == 'all':
            sql_round = sqls.bbv_round_sum_sov % (bracket, range_time)  # 柱形图数据和声量总和计算sov环形图合并在一起
        elif platform in ["微博", "微信"]:
            sql_round = sqls.round_ww_sum_sov % (bracket, bracket_platform, range_time)
        else:
            sql_round = sqls.bbv_platform_round_sum_sov % (bracket, bracket_platform, range_time)
    else:
        if platform == 'net':
            sql_round = sqls.round_all_brand_sum_sov % (range_time)  # 声量总和计算sov环形图
        elif platform == 'all':
            sql_round = sqls.bbv_all_brand_round_sum_sov % (range_time)
        elif platform in ["微博", "微信"]:
            sql_round = sqls.ww_round_sum_sov % (bracket_platform, range_time)
        else:
            sql_round = sqls.bbv_platform_all_brand_round_sum_sov % (bracket_platform, range_time)

    data_voice_histogram = DB.search(sql_his, {"category_name": category.name})
    data_voice_round = DB.get(sql_round, {"category_name": category.name})
    get_round_sov(data_voice_histogram, data_voice_round)
    return data_voice_histogram, data_voice_round


def get_platform_voice_from(bracket, range_time, category, platform='net'):
    # 获取平台声量来源 只有bbv全部和全网数据有平台来源
    if platform == 'net':
        sql_platform_sum = sqls.platform_voice_sum % (bracket, range_time)  # 平台的声量sum
        sql_platform_classify = sqls.platfom_classify_count % (bracket, range_time)  # 各个平台的分类声量
    elif platform == 'all':  # 子类下面没有平台的声量数据
        sql_platform_sum = sqls.bbv_platform_voice_sum_all%(bracket, range_time) # 平台的声量sum
        sql_platform_classify = sqls.bbv_platform_voice_all_classify%(bracket, range_time)  # 各个平台的分类声量
    else:
        return list()
    data_voice_platform_sum = DB.search(sql_platform_sum, {"category_name": category.name})
    data_voice_platform_classify = DB.search(sql_platform_classify, {"category_name": category.name})
    vioce_platform = dispose_platform_voice(data_voice_platform_sum, data_voice_platform_classify)

    return vioce_platform


def get_area_voice_from(range_time, category, brand_name, platform='net'):
    # 获取平台的地域声量
    bracket_platform = join_sql_bracket([platform, ])
    if platform == 'net':
        sql_area_classify = sqls.area_voice_classify % (range_time)  # 各个地域的分类声量
    elif platform == 'all':
        sql_area_classify = sqls.bbv_area_voice_classify%(range_time)  # 各个地域的分类声量
    else:
        sql_area_classify = sqls.bbv_platform_area_voice_classify%(bracket_platform, range_time)
    data_voice_area_classify = DB.search(sql_area_classify, {"category_name": category.name, "brand_name": brand_name})

    return data_voice_area_classify


def get_keywords_from(range_time, category, brand_name, platform='net'):
    # 获取关键词
    bracket_platform = join_sql_bracket([platform, ])
    if platform == 'net':
        net_keywords = sqls.net_keywords % (range_time)  # 获取全网关键词
    elif platform == 'all':
        net_keywords = sqls.bbv_all_keywords%(range_time)  # 获取全网关键词
    else:
        net_keywords = sqls.bbv_platform_keywords_classify % (bracket_platform, range_time)  # 获取全网关键词
    keywords = DB.search(net_keywords, {"category_name": category.name, "brand_name": brand_name})

    return keywords


def get_content_from(bracket, range_time, competitors, category, brand_name, platform='net'):
    # 获取内容分布雷达图 竞品为全品类的时候值显示当前品牌， 为主要竞品时是本品+竞品
    str_brand = join_sql_bracket([brand_name, ])
    bracket_platform = join_sql_bracket([platform,])
    if competitors:
        if platform == 'net':  # 全网的数据和bbv全部的数据时一样的
            sql_radar = sqls.content_radar%(bracket, range_time)
            sql_radar_classify = sqls.content_radar_classify%(bracket, range_time)
        elif platform == 'all':
            sql_radar = sqls.content_radar_bbv_all % (bracket, range_time)
            sql_radar_classify = sqls.content_radar_classify_bbv_all % (bracket, range_time)
        else:
            sql_radar = sqls.content_radar_other_platform % (bracket,bracket_platform, range_time)
            sql_radar_classify = sqls.content_radar_classify_other_platform % (bracket,bracket_platform, range_time)
    else:
        if platform == 'net':  # 全网的数据和bbv全部的数据时一样的
            sql_radar = sqls.content_radar%(str_brand, range_time)
            sql_radar_classify = sqls.content_radar_classify%(str_brand, range_time)
        elif platform == 'all':
            sql_radar = sqls.content_radar_bbv_all % (str_brand, range_time)
            sql_radar_classify = sqls.content_radar_classify_bbv_all % (str_brand, range_time)
        else:
            sql_radar = sqls.content_radar_other_platform % (str_brand, bracket_platform,range_time)
            sql_radar_classify = sqls.content_radar_classify_other_platform % (str_brand, bracket_platform, range_time)
    data_radar = DB.search(sql_radar, {"category_name": category.name})
    data_radar_classify = DB.search(sql_radar_classify, {"category_name": category.name})
    dispose_content_radar(data_radar, data_radar_classify)
    return data_radar_classify


def get_net_day_month_week_analysis(vcBrand, category, date_range):

    brand_name = vcBrand.get("brand_name")
    bracket, competitors, range_time = get_bracket_datarange(vcBrand, category, date_range)
    dict_data, dict_sov_classify = get_data(bracket, competitors, range_time, category)

    # 获取声量助柱形图
    data_voice_histogram, data_voice_round = get_data_voice_histogram(bracket, range_time, category, competitors)

    # 获取声量平台来源
    vioce_platform = get_platform_voice_from(bracket, range_time, category)

    # 获取地域声量来源
    data_voice_area_classify = get_area_voice_from(range_time, category, brand_name)

    # 获取全网关键词
    net_keywords = get_keywords_from(range_time, category, brand_name)

    # 获取内容分布
    data_radar_classify = get_content_from(bracket, range_time, competitors, category, brand_name)

    return dict_data, data_voice_histogram, vioce_platform, data_voice_area_classify, net_keywords, data_radar_classify


def dispose_content_radar(data_radar, data_radar_classify):
    for platform_sum in data_radar:
        for platform_classify in data_radar_classify:
            all_count = platform_sum.get("count")
            classify_count = platform_classify.get("count")
            if platform_sum.get('brand') == platform_classify.get("brand"):
                sov = get_all_sov(classify_count, all_count)
                platform_classify.update(sov=sov)
    return data_radar_classify


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


def get_all_sov(self_voice, compete_voice):
    try:
        sov = round(float(self_voice) / float(compete_voice) * 100, 2)
    except Exception:
        # raise Exception("竞品声量或者全品声量不能为0")
        sov = 0
    return sov


def dispose_platform_voice(data_voice_platform_sum, data_voice_platform_classify):
    """
    处理声量
    :return:
    """
    for platform_sum in data_voice_platform_sum:
        for platform_classify in data_voice_platform_classify:
            if platform_sum.get("brand") == platform_classify.get("brand"):
                sum_data = platform_sum.get("count")
                classify_data = platform_classify.get("count")
                sov = get_all_sov(classify_data, sum_data)
                platform_classify.update(sov=sov)
                platform_classify.update(sum_coun=sum_data)
    return data_voice_platform_classify


def get_bbv_day_month_week_analysis(vcBrand, category, date_range, platform):
    """
    # 全品类的时候声量top5+本品 有竞品的时候本品+竞品
    :param brand_id:
    :return:
    """

    brand_name = vcBrand.get("brand_name")
    bracket, competitors, range_time = get_bracket_datarange(vcBrand, category, date_range)
    dict_data, dict_sov_classify = get_data(bracket, competitors, range_time, category, platform)
    # 获取声量助柱形图
    data_voice_histogram, data_voice_round = get_data_voice_histogram(bracket, range_time, category, competitors, platform)

    # 获取平台声量的条形图
    vioce_platform = get_platform_voice_from(bracket, range_time, category, platform)

    # 获取地域的声量
    data_voice_area_classify = get_area_voice_from(range_time, category, brand_name, platform)

    # 获取全网关键词
    net_keywords = get_keywords_from(range_time, category, brand_name, platform)

    # 获取内容分布
    data_radar_classify = get_content_from(bracket, range_time, competitors, category, brand_name)

    return dict_data, data_voice_histogram, vioce_platform, data_voice_area_classify, net_keywords, data_radar_classify


def get_bbv_analysis(brand_id, date_range, platform):
    # bbv数据分析
    date_range = json.loads(date_range)
    try:
        vcBrand = get_vcbrand_for_name(brand_id)
    except Exception:
        vcBrand = DB.get(sqls.get_brand_by_id, {"brand_id": brand_id})

    category = DimCategory.objects.get(id=vcBrand.get("category_id"))
    industry = DimIndustry.objects.get(id=category.industry_id)
    self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range, type=platform)
    data_assert, data_voice_histogram, vioce_platform, area_voice, net_keywords, data_radar_classify = get_bbv_day_month_week_analysis(vcBrand, category, date_range, platform)
    sov = get_all_sov(self_voice, compete_voice)
    append_vc_brand(vcBrand, competitors, data_assert, self_voice, category, industry, compete_voice, sov)
    vcBrand.update(data_voice_histogram=data_voice_histogram)
    vcBrand.update(vioce_platform=vioce_platform)
    vcBrand.update(area_voice=area_voice)
    vcBrand.update(net_keywords=net_keywords)
    vcBrand.update(data_radar_classify=data_radar_classify)
    # 环比
    link_relative(vcBrand, self_voice, sov, self_voice_previous, compete_voice_previous)
    return vcBrand


def get_bracket_datarange(vcBrand, category, date_range):
    brand_name = vcBrand.get("brand_name")
    range_time = " and a.date between '{}' and '{}' ".format(date_range[0], date_range[1])
    competitors = json.loads(vcBrand.get("competitor"))
    try:
        list_compete = dispose_competers(competitors)
    except Exception:
        list_compete = list()
        for competitor in competitors:
            list_compete.append(competitor.get("name"))
    # list_compete = list()
    if competitors:  # 有竞品
        # for competitor in competitors:
        #     list_compete.append(competitor.get("name"))
        # list_compete.append(brand_name)
        bracket = join_sql_bracket(list_compete)
    else:
        # 获取top5的声量
        sql = sqls.all_top5 % (range_time)
        sql_brand = DB.search(sql, {"bran_name": brand_name, "category_name": category.name})
        for brand in sql_brand:
            list_compete.append(brand.get("brand"))
        list_compete.append(brand_name)
        bracket = join_sql_bracket(list_compete)
    return bracket, competitors, range_time


def get_dsm_milk_analysis(brand_id, date_range, platform):
    """
    奶粉深度社媒数据分析 其中微博微信的数据的声量数据来源与sass
    """
    date_range = json.loads(date_range)
    try:
        vcBrand = get_vcbrand_for_name(brand_id)
    except Exception:
        vcBrand = DB.get(sqls.get_brand_by_id, {"brand_id": brand_id})
    category = DimCategory.objects.get(id=vcBrand.get("category_id"))
    industry = DimIndustry.objects.get(id=category.industry_id)
    self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range, platform)
    data_assert, data_voice_histogram, data_voice_area_classify, net_keywords, data_radar_classify = get_dsm_milk_day_month_week_analysis(vcBrand, category, date_range, platform)
    #  需要增加官方发帖 用户发帖
    offcial_posts = get_top_20_offical_posts(vcBrand, platform, date_range, category)  # 官方发帖
    user_posts = get_top_20_user_posts(vcBrand, platform, date_range, category)  # 用户发帖

    sov = get_all_sov(self_voice, compete_voice)
    append_vc_brand(vcBrand, competitors, data_assert, self_voice, category, industry, compete_voice, sov)
    vcBrand.update(data_voice_histogram=data_voice_histogram)
    vcBrand.update(area_voice=data_voice_area_classify)
    vcBrand.update(net_keywords=net_keywords)
    vcBrand.update(data_radar_classify=data_radar_classify)
    vcBrand.update(offcial_posts=offcial_posts)
    vcBrand.update(user_posts=user_posts)
    # 环比
    link_relative(vcBrand, self_voice, sov, self_voice_previous, compete_voice_previous)
    # top5 玉珏图
    if category.name == "咖啡":
        top5, top3 = randar_patter_map(vcBrand, platform, date_range, category)
        vcBrand.update(top5=top5)
        vcBrand.update(top3=top3)

    return vcBrand


def link_relative(vcBrand, self_voice, sov, self_voice_previous, compete_voice_previous):
    sov_previous = get_all_sov(self_voice_previous, compete_voice_previous)
    try:
        link_relative = round((float(self_voice) - float(self_voice_previous)) / float(self_voice_previous) * 100, 2)
        link_relative_sov = round((float(sov) - float(sov_previous)) / float(sov_previous) * 100, 2)
    except Exception:
        link_relative = 0
        link_relative_sov = 0
    vcBrand.update(link_relative={"link_relative": link_relative, "link_relative_sov": link_relative_sov})

    return vcBrand


def get_dsm_milk_day_month_week_analysis(vcBrand, category, date_range, platform):

    brand_name = vcBrand.get("brand_name")
    bracket, competitors, range_time = get_bracket_datarange(vcBrand, category, date_range)

    # 获取日周月数据
    dict_data, dict_sov_classify = get_data(bracket, competitors, range_time, category, platform)
    # sov环形 和 品牌声量的条形图
    data_voice_histogram, data_voice_round = get_data_voice_histogram(bracket, range_time, category, competitors, platform)

    # 获取声量平台的条形图  子类是没有声量平台来源的条形图的

    # 获取地域的声量 地域声量微薄微信和小红书还有知乎的来源是一样的
    data_voice_area_classify = get_area_voice_from(range_time, category, brand_name, platform)

    # 获取全网关键词
    net_keywords = get_keywords_from(range_time, category, brand_name, platform)

    # 获取内容分布
    data_radar_classify = get_content_from(bracket, range_time, competitors, category, brand_name)

    return dict_data, data_voice_histogram, data_voice_area_classify, net_keywords, data_radar_classify


def get_top_20_offical_posts(vcBrand, platform, date_range, category):
    """
    获取官方发帖top20 只有是深度社媒的微博和小红书平台
    按照互动量排序 微博：原创微博的转发+评论+点赞
                 微信： 点赞数
                 小红书： 原创帖子的转发+品论+点赞+收藏
                 知乎：评论+点赞
    :return:
    """

    range_time = " a.date between '{}' and '{}' ".format(date_range[0], date_range[1])
    brand_name = vcBrand.get("brand_name")
    if platform in ["微博", "微信", "小红书"]:
        if platform == "微博":
            sql = sqls.dsm_weibo_official_top20 %range_time
        elif platform == "微信":
            sql = sqls.dsm_weixin_official_top20%range_time
        else:
            sql = sqls.dsm_redbook_official_top20%range_time
        offcial_posts = DB.search(sql, {'type_from': 1, "platform": platform, "brand_name": brand_name, "category_name": category.name})
    else:
        offcial_posts = []

    return offcial_posts


def get_top_20_user_posts(vcBrand, platform, date_range, category):
    """
    获取用户发帖top20  只有是深度社媒的微博和小红书平台
    :return:
    """
    range_time = " a.date between '{}' and '{}' ".format(date_range[0], date_range[1])
    brand_name = vcBrand.get("brand_name")
    if platform in ["微博", "微信", "小红书"]:
        if platform == "微博":
            sql = sqls.dsm_weibo_official_top20 % range_time
        elif platform == "微信":
            sql = sqls.dsm_weixin_official_top20 % range_time
        else:
            sql = sqls.dsm_redbook_official_top20 % range_time
        users_posts = DB.search(sql, {'type_from': 2, "platform": platform, "brand_name": brand_name, "category_name": category.name})
    else:
        users_posts = []

    return users_posts


def randar_patter_map(vcBrand, platform, date_range, category):
    """
     雷达组合图 获取条形加玉珏图 页面展示咖啡的微博加小红书
    品牌 购买行为 感官 取出top5 没有玉珏图
    使用场景 产品属性 取出top3 加上玉珏图
    top5和top3分别计算返回
    :return:
    """
    dict_data = dict()
    dict_scene_property = {}
    if platform in ["微博", '小红书']:
        range_time = " and date between '{}' and '{}' ".format(date_range[0], date_range[1])
        # range_time = " and date between '{}' and '{}' ".format('2018-01-01', '2019-12-30')
        brand_name = vcBrand.get("brand_name")
        sql_second_top5 = sqls.randar_patter_map%(range_time)
        data_second_top5 = DB.search(sql_second_top5, {"brand_name": brand_name, "category_name": category.name, "platform": platform})
        # data_second_top5 = DB.search(sql_second_top5, {"brand_name": brand_name, "category_name": '奶粉', "platform": platform})
        level2 = []
        data_second_top5.sort(key=itemgetter('level1'))
        for level1, items in groupby(data_second_top5, key=itemgetter('level1')):
            if level1 in ['使用场景', '产品属性']:
                list_level2 = [i.get('level2') for i in items][:3]
                level2.extend(list_level2)
            else:  # 取出top3
                dict_data.update({level1: [i.get('level2') for i in items]})
        if level2:  # # 获取使用场景 产品属性的3级认知的全部的言论数计算玉珏图
            level2_bracket = join_sql_bracket(level2)
            sql = sqls.region_three_for_randar%(level2_bracket, range_time)
            data_three_region = DB.search(sql, {"brand_name": brand_name, "category_name": category.name, "platform": platform})
            # data_three_region = DB.search(sql, {"brand_name": brand_name, "category_name": "奶粉", "platform": platform})
            data_three_region.sort(key=itemgetter('level1'))
            for level1, items in groupby(data_three_region, key=itemgetter('level1')):
                for i in items:
                    if level1 not in dict_scene_property:
                        dict_scene_property.update({level1: {i.get('level2'): [[i.get('level3'), i.get('count')]]}})
                    else:
                        two_region = dict_scene_property.get(level1)
                        level2 = i.get('level2')
                        if level2 not in two_region:
                            two_region.update({level2: [[i.get('level3'), i.get('count')]]})
                        else:
                            two_region.get(level2).append([i.get('level3'), i.get('count')])

    return dict_data, dict_scene_property



# ############################# 活动定位: activity orientation #################################


def bbv_all_and_date(params):
    '''
    活动定位 -> 功能函数:
        1、处理 bbv 全部, 即:删除 params中的 platform
        2、将 params 中的 start_date 和 end_date 封装成 model 查询方式
    :param params:
    :return: 返回 platform
    '''
    params.update(date__range=[params.pop("start_date"), params.pop("end_date")])

    if params["type"] == "bbv" and params["platform"] == "全部":
        return params.pop("platform")

    return params["platform"]


def ao_activity_tag_list(params):
    '''
    活动定位 -> 标签列表
    :param params:
    :return:
    '''
    bbv_all_and_date(params)
    activity_tags = list(VcMpActivityTags.objects.filter(**params)
                         .values("activity_tag").annotate(count=Sum("count"))
                         .order_by("-count").values("activity_tag")[:20])

    return activity_tags


def ao_volume_trend(params):
    '''
    活动定位 -> 品牌声量趋势
    :param params:
    :return:
    '''
    platform = bbv_all_and_date(params)

    # 获取 活动日期 或者 系统推荐活动日期
    if params["activity_tag"] == "":
        activity_date = ao_recommend_activate_period(copy.deepcopy(params))
    else:
        activity_date = ao_activity_date(params)

    params.pop("activity_tag")
    if platform in ["微信", "微博"]:
        params.pop("type")
        volume_obj = VcSaasPlatformVolume.objects.filter(**params)
    else:
        volume_obj = VcMpPlatformAreaVolume.objects.filter(**params)

    volume_trend = list(volume_obj.values("date").annotate(count=Sum("count")).order_by("date"))
    date_list = list(DimDate.objects.filter(date__range=params["date__range"]).values("date").distinct().order_by("date"))

    volume_trend = apps_apis.combine_list_map(date_list, volume_trend, "date", dict(count=0))
    data = apps_apis.combine_list_map(volume_trend, activity_date, "date", dict(is_activity=0))

    return data


def ao_activity_date(params):
    '''
    活动定位 -> 获取活动所在的 日期列表
    :param params:
    :return:
    '''
    activity_tags = list(VcMpActivityTags.objects.filter(**params).values("date")
                         .annotate(is_activity=Value(1, output_field=IntegerField())).values("date", "is_activity"))

    return activity_tags


def ao_recommend_activate_period(params):
    '''
    活动定位 -> 系统推荐活动期
    :param params:
    :return:
    '''
    params.pop("type")
    params.pop("activity_tag")
    data = list(VcMpRecommendActivatePeriod.objects.filter(**params).values("date")
                .annotate(is_activity=Value(1, output_field=IntegerField())).values("date", "is_activity"))

    return data


def ao_keywords_cloud(params):
    '''
    活动定位 -> 获取关键词云
    :param params:
    :return:
    '''
    bbv_all_and_date(params)
    data = list(VcMpKeywordsCloud.objects.filter(**params)
                .values("keywords").annotate(count=Sum("count")).values("keywords", "count"))

    return data


def ao_activity_content(params):
    '''
    活动定位 -> 热帖一览
    :param params:
    :return:
    '''
    bbv_all_and_date(params)
    activity_content = VcMpActivityContent.objects.filter(**params).annotate(
        interaction=F("reading") + F("reviews") + F("retweets") + F("praise_points") + F("favorite"))\
        .order_by("account", "-interaction").values(
        "account", "title", "url", "reading", "reviews", "retweets", "praise_points", "favorite", "user_type"
    )[:30]

    return list(activity_content)




