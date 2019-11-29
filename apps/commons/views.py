# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse
from . import apis
from apps import apis as apps_apis
from common.user import apis as common_apis


# ############################# 活动有效性评估 相关参数列表 #################################


def common_param(request):
    '''
    公共参数
    :param request:
    :return:
    '''

    report_state = [
        dict(code=100, name="全部"),
        # dict(code=-1, name="失败"),
        dict(code=0, name="生成完成"),
        dict(code=1, name="提交中"),
        dict(code=2, name="生成中"),
        # dict(code=1, name="创建"),
        # dict(code=2, name="爬取中"),
        # dict(code=3, name="入库中"),
        # dict(code=4, name="计算中"),
    ],
    monitor_end_date = [
        dict(code=36500, name="全部"),
        dict(code=30, name="近一月"),
        dict(code=90, name="近三月"),
        dict(code=180, name="近半年"),
        dict(code=-180, name="半年以前"),
    ],
    monitor_period = [
        dict(code=36500, name="全部"),
        dict(code=14, name="两周以内"),
        dict(code=30, name="一个月以内"),
        # dict(code=90, name="三个月以内"),
        # dict(code=-90, name="三个月以上"),
    ],
    industry_list = apis.industry_list()
    user = request.user
    menus = common_apis.get_user_menus(request)
    user_info = apis.get_user_info(user)
    platforms = apis.get_platform_info()
    return JsonResponse(data={
        "report_state": report_state[0],
        "monitor_end_date": monitor_end_date[0],
        "monitor_period": monitor_period[0],
        "industry_list": industry_list,
        "menus": menus,
        "user_info": user_info,
        "platforms": platforms
    }, safe=False)


def brand_list(request):
    '''
    品牌列表
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("category_id", "请选择品类", "int")])
    data = apis.brand_list(param["category_id"])

    return JsonResponse(data, safe=False)


def category_list(request):
    '''
    品类列表
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("industry_id", "请选择行业", "int")])
    data = apis.category_list(param["industry_id"])

    return JsonResponse(data, safe=False)


def sales_point_list(request):
    '''
    宣传卖点列表
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("category_id", "请选择品类", "int")])
    data = apis.sales_point_list(param["category_id"])

    return JsonResponse(data, safe=False)


def report_template_list(request):
    '''
    报告模板列表
    :param request:
    :return:
    '''
    data = apis.report_template_list(request.user)

    return JsonResponse(data, safe=False)


def competitor_list(request):
    '''
    设置, 竞品列表
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("queue_filter", "", "str")])
    competitors = apis.competitor_list(param, request.user)

    return JsonResponse(competitors, safe=False)


def competitor_save(request):
    '''
    设置, 添加 主要竞品
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [
        ("category_id", "请选择品类", "int"),
        ("brand_id", "请选择品牌", "list"),
        ("competitors", "请选择竞品", "list"),
    ])
    apis.competitor_save(param, request.user)

    return HttpResponse("ok")


def competitor_get(request):
    '''
    设置, 获取单个 主要竞品的详细信息
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("id", "请输入主要竞品的 id", "int")])
    competitor = apis.competitor_get(param, request.user)

    return JsonResponse(competitor, safe=False)


def competitor_del(request):
    '''
    设置 删除 指定的 主要竞品
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("id", "请输入主要竞品的 id", "int")])
    apis.competitor_del(param, request.user)

    return HttpResponse("ok")
