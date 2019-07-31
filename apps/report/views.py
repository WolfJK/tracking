# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse
from . import apis
from apps import apis as apps_apis
from django.utils.http import urlquote
import json


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
    user = request.user
    report_id = request.POST.get("report_id")
    if not report_id:
        raise Exception("请输入报告id")
    apis.delete_report(user, report_id)

    return HttpResponse("")


def report_config_create(request):
    '''
    报告->活动有效性评估->报告配置新建
    :param request:
    :return:
    '''
    params = [
        ("report_id", "", "int"),
        ("industry_id", "请选择行业", "int"),
        ("brand_id", "请选择品牌", "int"),
        ("category_id", "请选择品类", "int"),
        ("product_line", "", "str"),
        ("name", "请输入报告名称", "str"),
        ("title", "请输入活动主题", "str"),
        ("tag", "请输入活动标签", "str"),
        ("monitor_start_date", "请选择活动检测周期", "str"),
        ("monitor_end_date", "请选择活动检测周期", "str"),
        ("platform", "请选择投放渠道", "str"),
        ("accounts", "", "str"),
        ("sales_point", "请选择投宣传卖点", "int"),
        ("remark", "", "str"),
    ]
    param = apps_apis.get_parameter(request.POST, params)
    apis.report_config_create(param, request.user)

    return HttpResponse()


def report_config_edit(request):
    '''
    报告->活动有效性评估->报告配置编辑
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_id", "请选择一个报告", "int")])
    data = apis.get_report_config(param["report_id"], request.user)

    return JsonResponse(data, safe=False)


def report_details(request):
    '''
    报告->活动有效性评估->报告详情
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_id", "请选择报告", "int")])
    data = apis.report_details(param["report_id"], request.user)
    return JsonResponse(data, safe=True)


def report_unscramble_save(request):
    '''
    报告->活动有效性评估->报告解读保存
    :param request:
    :return:
    '''
    params = [
        ("report_id", "请选择报告", "int"),
        ("plate", "请选择报告模块", "str"),
        ("content", "请输入报告解读内容", "str"),
    ]
    param = apps_apis.get_parameter(request.POST, params)
    if not param["plate"] in ("transmission", "efficiency", "effect_ugc", "effect_brand", "effect_sales_point"):
        raise Exception("报告板块错误")

    apis.report_unscramble_save(param, request.user)

    return JsonResponse(dict(code=200))


def report_common_info(request):
    # 有效行评估 --> 公共信息
    result = apis.get_common_info()
    return JsonResponse({
        "report_affilication": result[0],
        "report_status": result[1],
        "report_monitor_end_time": result[2],
        "monitor_cycle": result[3],

    }, safe=False)


def report_config_cancel(request):
    # 取消报告
    user = request.user
    report_id = request.POST.get("report_id")
    if not report_id:
        raise Exception("缺少report_id")

    apis.cancel_report(user, report_id)
    return HttpResponse("")


def upload_account(request):
    # 上传帐号

    file_obj = request.FILES.get("filename")  # 获取上传内容
    if not file_obj:
        raise Exception("没有找到文件")
    data = apis.read_excle(file_obj)
    return JsonResponse(data, safe=False)


def download_account(request):
    parametes = request.POST.get("channel")
    if not parametes:
        raise Exception("请先传入渠道参数列表")
    try:
        parametes = json.loads(parametes)
    except Exception:
        raise Exception("参数格式错误,list形式的字符串")
    # 下载模板
    download_file, file_name = apis.download_file(parametes)
    response = HttpResponse(download_file)
    # 返回中文名文件
    response["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response["Content-Disposition"] = "attachment; filename={0}".format(urlquote(file_name))

    return response


def download_panel(request):
    # 产看配置的下载名单
    report_id = request.POST.get("report_id")
    if not report_id:
        raise Exception("请先传入报告id")
    # 下载模板
    download_file, file_name = apis.make_form(report_id)
    response = HttpResponse(download_file)
    # 返回中文名文件
    response["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response["Content-Disposition"] = "attachment; filename={0}".format(urlquote(file_name))

    return response