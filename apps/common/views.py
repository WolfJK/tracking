# coding: utf-8
# __author__: ''
from __future__ import unicode_literals

from django.http.response import JsonResponse
from . import apis
from apps import apis as apps_apis


# ############################# 活动有效性评估 相关参数列表 #################################


def common_param(request):
    '''
    公共参数
    :param request:
    :return:
    '''
    data = dict(
        report_state=[
            dict(code=-1, name="失败"),
            dict(code=0, name="成功"),
            dict(code=1, name="创建"),
            dict(code=2, name="爬取中"),
            dict(code=3, name="入库中"),
            dict(code=4, name="计算中"),
        ],
        monitor_end_date=[
            dict(code=36500, name="全部"),
            dict(code=30, name="近一月"),
            dict(code=90, name="近三月"),
            dict(code=180, name="近半年"),
            dict(code=-180, name="半年以前"),
        ],
        monitor_period=[
            dict(code=36500, name="全部"),
            dict(code=14, name="两周以内"),
            dict(code=30, name="一个月以内"),
            dict(code=90, name="三个月以内"),
            dict(code=-90, name="三个月以上"),
        ],
        industry_list=apis.industry_list()
    )

    return JsonResponse(data)


def brand_list(request):
    '''
    品牌列表
    :param request:
    :return:
    '''
    request_list = [
        ("industry_id", "请选择 行业", "int"),
        ("brand_name", "请输入品牌名称", "str"),
    ]
    param = apps_apis.get_parameter(request.POST, request_list)
    data = apis.brand_list(param["industry_id"], param["brand_name"])

    return JsonResponse(data)


def category_list(request):
    '''
    品类列表
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def sales_point_list(request):
    '''
    宣传卖点列表
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def report_template_list(request):
    '''
    报告模板列表
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)


def throw_account_upload(request):
    '''
    投放账号上传
    :param request:
    :return:
    '''
    data = []

    return JsonResponse(data)






