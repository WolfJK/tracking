# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse
import apis
import json
from apps import apis as apps_apis


# ############################# 活动舆情分析 #################################

def add_monitor_brand(request):
    '''
    新增监测品牌
    :param request:
    :return:
    '''

    monitor_id = request.POST.get("monitor_id")
    category = request.POST.get("category")
    brand = request.POST.get("brand")
    day = request.POST.get("day")
    market_pattern = request.POST.get("market")
    apis.add_monitor_brand(request, monitor_id, category, brand, day, market_pattern)

    return JsonResponse(data={"result": "success"}, safe=False)


def search_monitor_brand(request):
    '''
    查找监测品牌
    :param request:
    :return:
    '''
    brand_name = request.POST.get("brand_name")
    category_id = request.POST.get("category_id")  # 行业
    result = apis.search_monitor_brand(request.user, brand_name, category_id)

    return JsonResponse(data=result, safe=False)


def delete_monitor_brand(request):
    '''
    删除监测品牌
    :param request:
    :return:
    '''
    brand_id = request.POST.get("brand_id")
    apis.delete_monitor_brand(brand_id)
    return JsonResponse(data={"result": "success"}, safe=False)


def data_monitor_analysis(request):
    '''
    监测品牌卡片页数据展示
    :param request:
    :return:
    '''

    # 返回所有的监测的数据
    brand_name = request.POST.get("brand_name")
    category_id = request.POST.get("category_id")
    data = apis.get_all_monitor_card_data(request, brand_name, category_id)
    return JsonResponse(data=data, safe=False)


def get_vc_monitor_brand(request):
    # 根据id获取某一个监测品牌的详细信息
    monitor_id = request.POST.get("monitor_id")
    data = apis.get_vc_monitor(monitor_id)
    return JsonResponse(data=data, safe=False)


def whole_net_analysis(request):
    '''
    奶粉咖啡 全网数据分析 环比的数据默认和卡片页跳转的数据是一样的，环比是和用户在页面上选择的时间来确定
    :param request:
    :return:
    '''
    brand_id = request.POST.get("brand_id")
    date_range = request.POST.get("date_range")  # list格式
    data = apis.whole_net_analysis(brand_id, date_range)
    return JsonResponse(data=data, safe=False)


def bbv_analysis(request):
    '''
    奶粉平台 深度bbv数据分析
    :param request:
    :return:
    '''
    brand_id = request.POST.get("brand_id")
    date_range = request.POST.get("date_range")  # list格式
    platform = request.POST.get("platform")  # 默认全部
    data = apis.get_bbv_analysis(brand_id, date_range, platform)
    return JsonResponse(data=data, safe=False)


def coffee_media_analysis(request):
    '''
    咖啡品平台 深度媒数据分析
    :param request:
    :return:
    '''

    brand_id = request.POST.get("brand_id")
    date_range = request.POST.get("date_range")  # list格式
    platform = request.POST.get("platform")  # 默认全部
    data = apis.get_dsm_milk_analysis(brand_id, date_range, platform)

    return JsonResponse(data=data, safe=False)


def milk_media_analysis(request):
    '''
    奶粉平台 深度平台数据分析
    :param request:
    :return:
    '''
    brand_id = request.POST.get("brand_id")
    date_range = request.POST.get("date_range")  # list格式
    platform = request.POST.get("platform")  # 默认全部
    data = apis.get_dsm_milk_analysis(brand_id, date_range, platform)

    return JsonResponse(data=data, safe=False)


# ############################# 活动定位: activity orientation #################################

ao_params = [
        ("category", "请选择品类", "str"),
        ("brand", "请选择品牌", "list", apps_apis.brand_to_brand),
        ("type", "请选择类型", "str"),
        ("platform", "请选择平台", "str"),
        ("start_date", "请选择开始时间", "str"),
        ("end_date", "请选择结束时间", "str"),
]

activity_tag = [("activity_tag", "", "str")]


def ao_activity_tag_list(request):
    '''
    活动定位 -> 标签列表
    :param request:
    :return:
    '''

    params = apps_apis.get_parameter(request.POST, ao_params)
    data = apis.ao_activity_tag_list(params)

    return JsonResponse(data=data, safe=False)


def ao_volume_trend(request):
    '''
    活动定位 -> 品牌声量趋势
    :param request:
    :return:
    '''
    params = apps_apis.get_parameter(request.POST, ao_params + activity_tag)
    data = apis.ao_volume_trend(params)

    return JsonResponse(data=data, safe=False)


def ao_keywords_cloud(request):
    '''
    活动定位 -> 获取关键词云
    :param request:
    :return:
    '''
    params = apps_apis.get_parameter(request.POST, ao_params + activity_tag)
    data = apis.ao_keywords_cloud(params)

    return JsonResponse(data=data, safe=False)


def ao_activity_content(request):
    '''
    活动定位 -> 热帖一览
    :param request:
    :return:
    '''
    params = apps_apis.get_parameter(request.POST, ao_params + activity_tag)
    data = apis.ao_activity_content(params)

    return JsonResponse(data=data, safe=False)


