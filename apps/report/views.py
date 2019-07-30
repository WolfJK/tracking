# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse
from . import apis
from apps import apis as apps_apis


# ############################# 活动有效性评估 #################################
def report_config_list(request):
    '''
    报告->活动有效性评估->报告配置列表
    :param request:
    :return:
    '''
    report_status = request.POST.get("report_status")
    monitor_end_time = request.POST.get("monitor_end_time")
    monitor_cycle = request.POST.get("monitor_cycle")
    key_word = request.POST.get("key_word")

    data = apis.get_report_list(request.user, report_status, monitor_end_time, monitor_cycle, key_word)

    return JsonResponse(data, safe=False)


def report_config_delete(request):
    '''
    报告->活动有效性评估->报告配置删除
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def report_config_create(request):
    '''
    报告->活动有效性评估->报告配置新建
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def report_config_edit(request):
    '''
    报告->活动有效性评估->报告配置编辑
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def report_details(request):
    '''
    报告->活动有效性评估->报告详情
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_id", "请选择报告", "int")])
    data = apis.report_details(param["report_id"])
    return JsonResponse(data, safe=True)


def report_unscramble_save(request):
    '''
    报告->活动有效性评估->报告解读保存
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def report_common_info(request):
    # 有效行评估 --> 公共信息
    result = apis.get_common_info()
    return JsonResponse({
        "report_affilication": result[0],
        "report_status": result[1],
        "report_monitor_end_time": result[2],
        "monitor_cycle": result[3],

    }, safe=False)


