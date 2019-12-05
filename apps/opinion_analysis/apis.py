# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
import json
from apps.opinion_analysis import sqls
from common.db_helper import DB
from datetime import datetime
from django.db.models import Q, F, Sum
import copy
from dateutil.relativedelta import relativedelta


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
        time_slot = vcBrand.get("time_slot")
        # 时间周期计算
        date1 = datetime.now().strftime("%Y-%m-%d")
        date2 = (datetime.now() - relativedelta(days=time_slot)).strftime("%Y-%m-%d")
        date_range = [date2, date1]
        vcBrand.update(date_range=date_range)
        self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range)
        brand_name = vcBrand.get("brand_name")
        data_sql = sqls.all_data_card_voice_assert %(time_slot)
        data_assert = DB.search(data_sql, {"brand_name": brand_name, "category_name": category.name})  # 所有当前品牌的日期数据
        vcBrand.update(competitor=competitors)
        vcBrand.update(data_assert=data_assert)
        vcBrand.update(self_voice=self_voice)
        vcBrand.update(category_name=category.name)
        vcBrand.update(industry_name=industry.name)
        vcBrand.update(compete_voice=compete_voice)
        sov = get_all_sov(self_voice, compete_voice)
        vcBrand.update(sov=sov)

    return vcBrands


def get_card_voice_sov(vcBrand, category,  date_range):
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
    list_compete = list()
    if competitors:  # 有竞品
        for competitor in competitors:
            list_compete.append(competitor.get("name"))
        list_compete.append(brand_name)  # 所有的竞品加上本品的总数
        bracket = join_sql_bracket(list_compete)
        sql = sqls.monitor_data_compete_voice % (bracket, range_time)  # 获取当前
        sql_previous = sqls.monitor_data_compete_voice% (bracket, range_time_previous)  # 获取上个阶段
        voice = DB.get(sql, {"category_name": category.name})  # 获取竞品声量
        voice_previous = DB.get(sql_previous, {"category_name": category.name})  # 获取竞品声量

        compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        compete_voice_previous = int(voice_previous.get("voice_all")) if voice_previous.get("voice_all") else 0
    else:  # 全品
        sql = sqls.all_monitor_voice % (range_time)
        sql_previous = sqls.all_monitor_voice % (range_time_previous)
        voice = DB.get(sql, {"category_name": category.name})  # 获取全品类声量
        voice_previous = DB.get(sql_previous, {"category_name": category.name})  # 获取全品类声量
        compete_voice = int(voice.get("voice_all")) if voice.get("voice_all") else 0
        compete_voice_previous = int(voice_previous.get("voice_all")) if voice_previous.get("voice_all") else 0

    new_sql = sqls.monitor_data_analysis_voice % (range_time)
    new_sql_previous = sqls.monitor_data_analysis_voice % (range_time_previous)

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
    vcBrand = DB.get(sqls.get_brand_by_id, {"brand_id": brand_id})
    category = DimCategory.objects.get(id=vcBrand.get("category_id"))
    industry = DimIndustry.objects.get(id=category.industry_id)
    self_voice, competitors, compete_voice, self_voice_previous, compete_voice_previous = get_card_voice_sov(vcBrand, category, date_range)
    data_assert, data_voice_histogram, vioce_platform, area_voice, net_keywords, data_radar_classify = get_day_month_week_analysis(vcBrand, category, date_range)
    sov = get_all_sov(self_voice, compete_voice)
    vcBrand.update(competitor=competitors)
    vcBrand.update(self_voice=self_voice)
    vcBrand.update(category_name=category.name)
    vcBrand.update(industry_name=industry.name)
    vcBrand.update(compete_voice=compete_voice)
    vcBrand.update(data_assert=data_assert)
    vcBrand.update(sov=sov)
    vcBrand.update(data_voice_histogram=data_voice_histogram)
    vcBrand.update(vioce_platform=vioce_platform)
    vcBrand.update(area_voice=area_voice)
    vcBrand.update(net_keywords=net_keywords)
    vcBrand.update(data_radar_classify=data_radar_classify)
    # todo 环比
    sov_previous = get_all_sov(self_voice_previous, compete_voice_previous)
    try:
        link_relative = round((float(self_voice)-float(self_voice_previous) )/ float(self_voice_previous) * 100, 2)
        link_relative_sov = round((float(sov)-float(sov_previous) )/ float(sov_previous) * 100, 2)
    except Exception:
        link_relative = 0
        link_relative_sov = 0
    vcBrand.update(link_relative={"link_relative": link_relative, "link_relative_sov": link_relative_sov})
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


def get_day_month_week_analysis(vcBrand, category, date_range):
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

    def assemble_data(assert_data, type):
        for day in assert_data:
            brand_name = day.get("brand")
            if brand_name not in dict_data:
                dict_data.update({brand_name: {"day": [], "month": [], "week": []}})
                dict_data.get(brand_name).get(type).append(day)
            else:
                dict_data.get(brand_name).get(type).append(day)

    def get_data():
        sql_day = sqls.compete_day_month_week_voice%(bracket, range_time,  "date", "date", "date")
        sov_day = sqls.area_of_tend_sov%(bracket, range_time,  "date", "date", "date")
        sql_month = sqls.compete_day_month_week_voice%(bracket, range_time,  "month", "month", "month")
        sov_month = sqls.area_of_tend_sov%(bracket, range_time,  "month", "month", "month")
        sql_week = sqls.compete_day_month_week_voice%(bracket, range_time,  "week", "week", "week")
        sov_week = sqls.area_of_tend_sov%(bracket, range_time,  "week", "week", "week")

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
        assemble_data(day_assert, "day")
        assemble_data(month_assert, "month")
        assemble_data(week_assert, "week")

    brand_name = vcBrand.get("brand_name")

    range_time = " and a.date between '{}' and '{}' ".format(date_range[0], date_range[1])

    competitors = json.loads(vcBrand.get("competitor"))
    list_compete = list()
    if competitors:  # 有竞品
        for competitor in competitors:
            list_compete.append(competitor.get("name"))
        list_compete.append(brand_name)
        bracket = join_sql_bracket(list_compete)

    else:
        # 获取top5的声量
        sql = sqls.all_top5%(range_time)
        sql_brand = DB.search(sql, {"bran_name": brand_name, "category_name": category.name})

        for brand in sql_brand:
            list_compete.append(brand.get("brand"))
        list_compete.append(brand_name)
        bracket = join_sql_bracket(list_compete)
    get_data()

    # 获取声量助柱形图
    sql_his = sqls.brand_voice_histogram%(bracket, range_time,)
    sql_round = sqls.round_sum_sov%(bracket, range_time)  # 声量总和计算sov环形图
    sql_platform_sum = sqls.platform_voice_sum%(bracket, range_time) # 平台的声量sum
    sql_platform_classify = sqls.platfom_classify_count%(bracket, range_time)  # 各个平台的分类声量
    # sql_area_sum = sqls.area_voice_sum%(bracket, range_time)  # 各个地域的分类声量之和
    sql_area_classify = sqls.area_voice_classify%(bracket, range_time)  # 各个地域的分类声量
    net_keywords = sqls.net_keywords%(bracket, range_time)  # 获取全网关键词

    data_voice_histogram = DB.search(sql_his, {"category_name": category.name})

    data_voice_round = DB.get(sql_round, {"category_name": category.name})

    data_voice_platform_sum = DB.search(sql_platform_sum, {"category_name": category.name})
    data_voice_platform_classify = DB.search(sql_platform_classify, {"category_name": category.name})
    # 获取声量平台来源
    vioce_platform = dispose_platform_voice(data_voice_platform_sum, data_voice_platform_classify)

    # 获取地域声量来源
    # data_voice_area_sum = DB.search(sql_area_sum, {"category_name": category.name})
    data_voice_area_classify = DB.search(sql_area_classify, {"category_name": category.name})

    # 增加 sov趋势 sov环形
    get_classify_sov(dict_data, dict_sov_classify)
    get_round_sov(data_voice_histogram, data_voice_round)

    # 获取全网关键词
    net_keywords = DB.search(net_keywords, {"category_name": category.name})
    # 获取内容分布
    if competitors:
        sql_radar = sqls.content_radar%(bracket, range_time)
        sql_radar_classify = sqls.content_radar_classify%(bracket, range_time)

    else:
        str_brand = join_sql_bracket([brand_name, ])
        sql_radar = sqls.content_radar%(str_brand, range_time)
        sql_radar_classify = sqls.content_radar_classify%(str_brand, range_time)
    data_radar = DB.search(sql_radar, {"category_name": category.name})
    data_radar_classify = DB.search(sql_radar_classify, {"category_name": category.name})
    dispose_content_radar(data_radar, data_radar_classify)
    return dict_data, data_voice_histogram, vioce_platform, data_voice_area_classify, net_keywords, data_radar_classify


def dispose_content_radar(data_radar, data_radar_classify):
    for platform_sum in data_radar:
        for platform_classify in data_radar_classify:
            all_count = platform_sum.get("count")
            classify_count = platform_classify.get("count")
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

    if params["activity_tag"] == "":
        params.pop("activity_tag")
        activity_date = ao_recommend_activate_period(copy.deepcopy(params))
    else:
        # 获取 活动日期
        activity_date = ao_activity_date(params)

    if platform in ["微信", "微博"]:
        volume_obj = VcSaasPlatformVolume.objects.filter(**params)
    else:
        volume_obj = VcMpPlatformAreaVolume.objects.filter(**params)

    data = list(volume_obj.values("date").annotate(count=Sum("count")).order_by("-date"))

    return list(data=data, activity_date=activity_date)


def ao_activity_date(params):
    '''
    活动定位 -> 获取活动所在的 日期列表
    :param params:
    :return:
    '''
    activity_tags = list(VcMpActivityTags.objects.filter(**params).values("date").distinct().order_by("-date"))

    return activity_tags


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
        "account", "title", "url", "reading", "reviews", "retweets", "praise_points", "favorite"
    )[:30]

    return list(activity_content)


def ao_recommend_activate_period(params):
    '''
    活动定位 -> 系统推荐活动期
    :param params:
    :return:
    '''
    params.pop("type")
    data = list(VcMpRecommendActivatePeriod.objects.filter(**params).values("date").distinct().order_by("date"))

    return data

