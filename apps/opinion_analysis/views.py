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
    监测品牌数据展示
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def whole_net_analysis(request):
    '''
    奶粉咖啡 全网数据分析
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
    获取市场格局 对于新增加的获取的是原本设置的主要竞品 对于配置修改的获取的是原来存储的
    :param request:
    :return:
    '''

    vc_monitor_id = request.POST.get("monitor_brand_id")

    if vc_monitor_id:
        # 返回主要竞品
        brand_list = json.loads(vc_monitor_id)
        data = apis.get_compete_brand(brand_list)
    else:
        # 返回全品类
        data = []
    return JsonResponse(data=data, safe=False)

