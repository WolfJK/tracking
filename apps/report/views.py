# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from django.http.response import JsonResponse, HttpResponse
from . import apis
from apps import apis as apps_apis
from django.utils.http import urlquote
import json
from website.settings import whitelist


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
        ("brand_id", "请选择品牌", "list"),
        ("category_id", "请选择品类", "int"),
        ("competitors", "", "list"),
        ("product_line", "", "str"),
        ("name", "请输入报告名称", "str"),
        ("title", "请输入活动主题", "str"),
        ("tag", "", "list"),
        ("monitor_start_date", "请选择活动检测周期", "str"),
        ("monitor_end_date", "请选择活动检测周期", "str"),
        ("platform", "", "list"),
        ("accounts", "", "dict"),
        ("sales_points", "", "list"),
        ("remark", "", "str"),
        ("type", "", "list"),
    ]

    if request.user.is_admin:
        raise Exception("管理员不具有创建报告的权限")

    ip = apps_apis.get_ip(request)
    param = apps_apis.get_parameter(request.POST, params)
    # 这里判断标签  请选择投放渠道
    if not param['accounts'].get("url") and not param['tag']:
        raise Exception("请输入标签")
    if not param['accounts'].get("url") and not param['platform']:
        raise Exception("请选择投放渠道")
    diff_date = (apps_apis.str2date(param["monitor_end_date"]) - apps_apis.str2date(param["monitor_start_date"])).days + 1
    if diff_date < 1 or diff_date > 90:
        raise Exception("请选择正确的检测周期")

    if len(param["sales_points"]) > 3:
        raise Exception("宣传卖点最多选择 3 个")

    report = apis.report_config_create(param, request.user, ip)

    return JsonResponse(dict(code=200, report_id=report.id))


def report_config_edit(request):
    '''
    报告->活动有效性评估->报告配置编辑
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_id", "请选择一个报告", "int")])
    data = apis.get_report_config(param["report_id"], request.user)
    data.__dict__.pop("_state")
    # data = apis.formatted_report([data.__dict__])[0]
    return JsonResponse(data.__dict__, safe=False)


def report_details(request):
    '''
    报告->活动有效性评估->报告详情
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_id", "请选择一个报告", "int")])
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
        ("content", "请输入报告解读内容", "str"),
    ]
    param = apps_apis.get_parameter(request.POST, params)

    if request.user.is_admin:
        raise Exception("管理员不具有编辑解读权限")

    data = apis.report_unscramble_save(param, request.user)

    return JsonResponse(dict(code=200, data=data))


def update_report(request):
    '''
    更新报告状态
    :param request:
    :return:
    '''
    ip = apps_apis.get_ip(request)
    if not (ip.startswith("172.16.1.") or ip in apps_apis.domains_2_ips(whitelist)):
        return JsonResponse(dict(code=403))

    param = apps_apis.get_parameter(request.POST, [
        ("report_id", "请选择报告", "int"),
        ("status", "请输入报告状态", "int"),
        ("data", "", "dict")
    ])
    data = apis.update_report(param["report_id"], param["status"], param["data"], ip)
    return JsonResponse(data, safe=True)


def get_report(request):
    '''
    获取特定状态的报告列表
    :param request:
    :return:
    '''

    ip = apps_apis.get_ip(request)
    if not (ip.startswith("172.16.1.") or ip in apps_apis.domains_2_ips(whitelist)):
        return JsonResponse(dict(code=403))

    param = apps_apis.get_parameter(request.POST, [("status", "请输入报告状态", "int")])
    data = apis.get_reports(param["status"])

    return JsonResponse(data, safe=True)


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
    """
    1： bgc 2：kol  3： url
    数据格式变更 {
                "bgc": [{"1001": []}, {"1002": []}],
                "kol": [{"1001": []}, {"1002": []}],
                "url": [{}, {}]   都是独立存在的
                }
    :param request:
    :return:
    """
    file_bgc = request.FILES.get("bgc")  # 获取上传内容
    file_kol = request.FILES.get("kol")
    file_url = request.FILES.get("url")

    if file_url and (file_kol or file_bgc):
        raise Exception("url链接和kol,bgl不能同时上传")
    # data = apis.read_excle(file_obj)
    if file_url:
        data = apis.read_url_excle(file_url)
    else:
        data = apis.read_bgc_kol_excle(file_kol, file_bgc)

    return JsonResponse(data, safe=False)


def download_account(request):
    """
    版本新增连接下载 1：表示关键词 bgc下载 2： 表示关键词kol下载  3： 表示url连接下载
    :param request:
    :return:
    """
    parametes = request.POST.get("channel")
    flag = request.POST.get("type")
    if flag in ["1", "2"]:
        if not parametes:
            raise Exception("请先传入渠道参数列表")
        try:
            parametes = json.loads(parametes)
        except Exception:
            raise Exception("参数格式错误,list形式的字符串")

    # 下载模板
    download_file, file_name = apis.download_file(parametes, flag)
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
    try:
        download_file, file_name = apis.make_new_form(report_id)
    except Exception:
        download_file, file_name = apis.make_form(report_id)
    response = HttpResponse(download_file)
    # 返回中文名文件
    response["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response["Content-Disposition"] = "attachment; filename={0}".format(urlquote(file_name))

    return response


def activity_contrast(request):
    '''
    活动对比
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [("report_ids", "请选择报告", "list")])

    if len(param["report_ids"]) > 5 or len(param["report_ids"]) < 2:
        raise Exception("报告个数必须大于 2 小于 5")

    data = apis.activity_contrast(param, request.user)

    return JsonResponse(data, safe=False)


def get_competitor(request):
    '''
    根据 品类品牌 获取 品牌竞品列表
    :param request:
    :return:
    '''
    param = apps_apis.get_parameter(request.POST, [
        ("category_id", "请输入 品类 id", "int"),
        ("brand", "请输入品牌信息", "list"),
    ])

    competitor = apis.get_competitor(param, request.user)

    return JsonResponse(competitor, safe=False)