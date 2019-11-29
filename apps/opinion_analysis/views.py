# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse


# ############################# 活动舆情分析 #################################

def add_monitor_brand(request):
    '''
    新增监测品牌
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def search_monitor_brand(request):
    '''
    查找监测品牌
    :param request:
    :return:
    '''
    return JsonResponse(data={"result": "success"}, safe=False)


def delete_monitor_brand(request):
    '''
    删除监测品牌
    :param request:
    :return:
    '''
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