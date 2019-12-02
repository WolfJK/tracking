# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse
import apis
import json


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
    apis.add_monitor_brand(monitor_id, category, brand, day, market_pattern)

    return JsonResponse(data={"result": "success"}, safe=False)


def search_monitor_brand(request):
    '''
    查找监测品牌
    :param request:
    :return:
    '''
    brand_name = request.POST.get("brand_name")
    category_id = request.POST.get("category_id")  # 行业
    result = apis.search_monitor_brand(brand_name, category_id)

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
    category_id = request.POST.get("category_id")
    apis.get_all_monitor_card_data(category_id)
    return JsonResponse(data={"result": "success"}, safe=False)


def whole_net_analysis(request):
    '''
    奶粉咖啡 全网数据分析 环比的数据默认和卡片页跳转的数据是一样的，环比是和用户在页面上选择的时间来确定
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def bbv_analysis(request):
    '''
    奶粉平台 深度bbv数据分析
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def coffee_media_analysis(request):
    '''
    咖啡品平台 深度媒数据分析
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def milk_media_analysis(request):
    '''
    奶粉平台 深度平台数据分析
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def get_market_pattern(request):

    '''
    编辑监测品牌页面的瓶品牌格局获取 新增从表SmCompetitor返回数据 编辑# 从VcMonitorBrand返回主要竞品
    获取市场格局 对于新增加的获取的是原本设置的主要竞品 对于配置修改的获取的是原来存储的
    :param request:
    :return:
    '''

    vc_monitor_id = request.POST.get("monitor_brand_id")
    brand_list = request.POST.get("brand_list")
    if brand_list and vc_monitor_id:
        raise Exception("参数不能同时有效")
    if vc_monitor_id:
        # 从VcMonitorBrand返回主要竞品
        data = apis.get_compete_brand(vc_monitor_id)
    else:
        # 从表SmCompetitor返回数据
        brand_list = json.loads(brand_list)
        data = apis.get_compete_brand(brand_list)
    return JsonResponse(data=data, safe=False)

