# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
from django.db.models import F, Q, Func
from common.db_helper import DB
from io import BytesIO
from dateutil.relativedelta import relativedelta
import pandas
from compiler import ast
import sqls
import json
import datetime
import copy
import traceback
from common.logger import Logger
from apps.commons.apis import get_platform_info


logger = Logger.getLoggerInstance()

report_affilication = {
    "1": "本品",
    "2": "竞品"
}

report_status = {
    "1": "生成完成",
    "2": "生成中",
    "3": "提交中"
}

report_monitor_end_time = {
    "1": "近一个月",
    "2": "近三个月",
    "3": "近半年",
    "4": "半年前"
}

monitor_cycle = {
    "1": "两周以内",
    "2": "一个月以内"
}


def get_report_list(user, report_status, monitor_end_time, monitor_cycle, key_word):
    # 刷选报告
    sql_format = []
    # values = ("monitor_start_date", "monitor_end_date", "create_time", "username", "status")
    db = DB()
    sql = "SELECT * FROM report where `delete`=false and status>=0 ORDER BY status DESC, create_time DESC"
    if report_status != "100" or monitor_end_time != "36500" or monitor_cycle != "36500" or key_word or(not(user.is_admin and user.user_type == 1)):
        sql = "SELECT * FROM report WHERE `delete`=false and status>=0 and {} ORDER BY status DESC, create_time DESC"

    if report_status != "100":
        if int(report_status) >= 2:
            sql_format.append("{}>={}".format("status", report_status))
        else:
            sql_format.append("{}={}".format("status", report_status))
    if monitor_end_time != "36500":
        if monitor_end_time == "-180":
            sql_format.append("datediff(\'{}\', {})>{}".format(datetime.datetime.now(), "monitor_end_date", 180))
        else:
            sql_format.append("datediff(\'{}\', {})<={}".format(datetime.datetime.now(), "monitor_end_date", monitor_end_time))

    if monitor_cycle != "36500":
        if monitor_cycle == "-90":
             sql_format.append("datediff({}, {})>{}".format("monitor_end_date", "monitor_start_date", 90))
        else:
            sql_format.append("datediff({}, {})<={}".format("monitor_end_date", "monitor_start_date", monitor_cycle))

    if key_word:
        name = key_word.lower()
        user_list = SmUser.objects.annotate(name=Func(F("username"), function="LOWER"),
                                            ).filter(Q(name__contains=name)).values_list("id", flat=True)
        report_name = Report.objects.annotate(report_name=Func(F("name"), function="LOWER"),
                                            ).filter(Q(report_name__contains=name)).values_list("id", flat=True)

        str_user_list = ",".join([str(i) for i in user_list])
        str_title_list = ",".join([str(i) for i in report_name])

        if report_name and user_list:
            sql_title = "{} in ({})".format("id", str_title_list)
            sql_name = "{} in ({})".format("user_id", str_user_list)
            sql_format.append("(" + sql_title + " or " + sql_name + ")")
        else:
            if report_name:
                sql_title = "{} in ({})".format("id", str_title_list)
                sql_format.append(sql_title)
            if user_list:
                sql_name = "{} in ({})".format("user_id", str_user_list)
                sql_format.append(sql_name)

    # 判断是管理员内部用户
    if user.is_admin and user.user_type == 1:
        if "{" in sql or "}" in sql:
            sql = sql.format(True)
    elif user.is_admin:
        corporation = user.corporation
        sql_user = "{}={}".format("corporation", corporation)
        sql_format.append(sql_user)

    else:
        user_id = user.id
        sql_user = "{}={}".format("user_id", user_id)
        sql_format.append(sql_user)

    if sql_format:
        sql_format = " and ".join(sql_format)
        sql = sql.format(sql_format)
    res = db.search(sql)

    return formatted_report(res) if res else []


def formatted_report(reports):
    # 格式化表格
    data_format1 = "%Y-%m-%d"
    data_format2 = "%Y-%m-%d %H:%M:%S"

    for report in reports:
        # 一周内的报告加上NEW
        if report.get("create_time") >= datetime.datetime.now() - relativedelta(weeks=1):
            report.update(is_new=True)
        else:
            report.update(is_new=False)
        monitor_start_date = report.get("monitor_start_date").strftime(data_format1)
        monitor_end_date = report.get("monitor_end_date").strftime(data_format1)
        create_time = report.get("create_time").strftime(data_format2)
        update_time = report.get("update_time").strftime(data_format2) if report.get("update_time") else None
        report.update(monitor_start_date=monitor_start_date)
        report.update(create_time=create_time)
        report.update(update_time=update_time)
        report.update(monitor_end_date=monitor_end_date)
        status_values = Report.objects.get(id=report.get("id")).get_status_display()
        report.update(status_values=status_values)
        user = SmUser.objects.get(id=report.get("user_id"))
        report.update(username=user.username)
        report.update(platform=json.loads(report.get("platform")))
        brand_name = DimBrand.objects.get(id=report.get("brand_id")).name
        report.update(brand_name=brand_name)
        report.update(industry_name=DimIndustry.objects.get(id=report.get("industry_id")).name)
        report.update(category_name=DimCategory.objects.get(id=report.get("category_id")).name)
        report.update(sales_point_name=DimSalesPoint.objects.get(id=report.get("sales_point_id")).name)
        if user.brand.name == brand_name:
            report.update(is_owner="本品")
        else:
            report.update(is_owner="竞品")
    return reports


def get_common_info():

    return report_affilication, report_status, report_monitor_end_time, monitor_cycle


def report_details(report_id, user):
    """
    生成报告详情
    聚合结果为0时，是不出现在数据里的，需要后端补全, 也可能出现长度为0的列表
    :param report_id:
    :param user: 当前用户
    :return:
    """
    report = get_report(report_id, user, status=(0, ))

    data = data_transform(json.loads(report.data))
    if not data.get("unscramble"):
        data["unscramble"] = get_unscramble(data, report.sales_point.name)

    data["report_config"] = dict(
        start_date=report.monitor_start_date,
        end_date=report.monitor_end_date,
        name=report.name,
        sales_point=report.sales_point.name,
        period=(report.monitor_end_date - report.monitor_start_date).days,
        status_value=report.get_status_display(),
        status=report.status
    )

    return data


def data_transform(data):
    """
    将 etl 格式的数据 转换为 web 格式
    :param data: etl 数据
    :return:
    """
    # 投放渠道分布 转换
    platform = data["spread_overview"]["platform"]
    platform_web = []
    if platform["weibo"] != 0:
        platform_web.append(dict(
            name="微博",
            value=platform["weibo"],
            children=[dict(name="微博", value=platform["weibo"])]
        ))

    if len(platform["motherbaby"]) > 0:
        platform_web.append(dict(
            name="母垂",
            value=sum([x["value"] for x in platform["motherbaby"]]),
            children=platform["motherbaby"]
        ))

    data["spread_overview"]["platform_web"] = platform_web

    # 投放账号分布
    account_max_df = pandas.DataFrame(data["spread_overview"]["account"], columns=["account", "platform", "post_count", "user_type"])
    account_web = account_max_df.drop_duplicates(subset=["account", "platform", "user_type"]).groupby(["user_type"], as_index=False)["account"].count()
    post_web = account_max_df.groupby(["user_type"], as_index=False).agg({"post_count": pandas.Series.sum})

    account_web = pandas.merge(account_web, post_web, how="left", on="user_type")
    data["spread_overview"]["account_web"] = account_web.to_dict(orient="records")

    #  子活动UGC构成
    activity_ugc_in = data["spread_effectiveness"]["activity_ugc_in_activity_composition"]
    refer = filter(lambda x: x["type"] == "提及品牌", copy.deepcopy(activity_ugc_in))
    unrefer = filter(lambda x: x["type"] == "未提及品牌", copy.deepcopy(activity_ugc_in))
    unrefer_map = {x["name"]: x["value"] for x in unrefer}
    map(lambda x: x.update(dict(unvalue=unrefer_map.get(x["name"], 0))), refer)
    data["spread_effectiveness"]["activity_ugc_in"] = refer

    # 活动传播效率合并
    merge_spread_efficiency(data, "platform")
    merge_spread_efficiency(data, "account")
    merge_spread_efficiency(data, "activity")

    # 传播效果
    brand_ugc = copy.deepcopy(data["spread_effectiveness"]["brand_ugc_trend"])
    annual_average = data["spread_effectiveness"]["annual_average_trend"]
    dict_map = {x["date"]: x["value"] for x in annual_average}
    map(lambda x: x.update(dict(value_year=dict_map.get(x["date"], 0))), brand_ugc)
    data["spread_effectiveness"]["brand_ugc_web"] = brand_ugc

    # 品牌关注度
    map(lambda x: x.update(dict(value_year=data["brand_concern"]["annual"])), data["brand_concern"]["trend"])
    map(lambda x: x.update(dict(value_year=data["tags_concern"]["annual"])), data["tags_concern"]["trend"])

    return data


def merge_spread_efficiency(data, spread_type):
    '''
    对传播效率进行合并
    :param data:
    :param spread_type:
    :return:
    '''
    cumulative = copy.deepcopy(data["spread_efficiency"]["{}_cumulative".format(spread_type)])
    average = data["spread_efficiency"]["{}_average".format(spread_type)]

    list_to_map = {x["name"]: x for x in average}
    map(lambda x: x.update(dict(
        avg_breadth=list_to_map.get(x["name"], {}).get("breadth", 0),
        avg_interaction=list_to_map.get(x["name"], {}).get("interaction", 0),
        avg_value=list_to_map.get(x["name"], {}).get("value", 0),
    )), cumulative)

    data["spread_efficiency"]["{}_web".format(spread_type)] = cumulative


def get_unscramble(data, sales_point):
    '''
    根据数据 获取解读结果
    :param data:
    :param sales_point:
    :return:
    '''

    activity_max, platform_max, account_max, account_post_max, cb_platform_max, \
    hd_platform_max, cb_account_max, hd_account_max, cb_activity_max, hd_activity_max, \
    source_max, activity_ugc_max = [{}] * 12

    if data["spread_overview"]["activity"]:
        activity_max = max(data["spread_overview"]["activity"], key=lambda x: x["value"])

    if data["spread_overview"]["platform_web"]:
        platform_max = max(ast.flatten([x["children"] for x in data["spread_overview"]["platform_web"]]), key=lambda x: x["value"])

    platform_post_sum = sum([v["value"] for v in ast.flatten([x["children"] for x in data["spread_overview"]["platform_web"]])], 0.00001)

    if data["spread_overview"]["account_web"]:
        account_max = max(data["spread_overview"]["account_web"], key=lambda x: x["account"])
        account_post_max = max(data["spread_overview"]["account_web"], key=lambda x: x["post_count"])

    spread_efficiency = data["spread_efficiency"]["platform_cumulative"]

    if spread_efficiency:
        cb_platform_max = max(spread_efficiency, key=lambda x: x["breadth"])
        hd_platform_max = max(spread_efficiency, key=lambda x: x["interaction"])

    account_cumulative = data["spread_efficiency"]["account_cumulative"]
    if account_cumulative:
        cb_account_max = max(account_cumulative, key=lambda x: x["breadth"])
        hd_account_max = max(account_cumulative, key=lambda x: x["interaction"])

    activity_cumulative = data["spread_efficiency"]["activity_cumulative"]
    if activity_cumulative:
        cb_activity_max = max(activity_cumulative, key=lambda x: x["breadth"])
        hd_activity_max = max(activity_cumulative, key=lambda x: x["interaction"])

    platform_cumulative = data["spread_efficiency"]["platform_cumulative"]
    if platform_cumulative:
        source_max = max(platform_cumulative, key=lambda x: x["value"])

    user_type_composition = data["spread_efficiency"]["user_type_composition"]
    account_comment_max = max(user_type_composition, key=lambda x: x["value"])

    if data["spread_effectiveness"]["activity_ugc_in"]:
        activity_ugc_max = max(data["spread_effectiveness"]["activity_ugc_in"], key=lambda x: x["value"])

    param = dict(
        post_count=data["spread_overview"]["post_count"],
        account_all=data["spread_overview"]["account_count"],
        activity_count=len(data["spread_overview"]["activity"]),
        activity_max=activity_max.get("name"),
        activity_post_count=activity_max.get("value"),
        platform_max=platform_max.get("name"),
        platform_post_count=platform_max.get("value"),
        platform_max_ratio=round(platform_max.get("value", 0) * 100.0 / platform_post_sum, 2),
        account_max=account_max.get("user_type"),
        account_count=account_max.get("account"),
        account_post_max=account_post_max.get("user_type"),
        account_post_count=account_post_max.get("post_count"),

        platform_count=len(spread_efficiency),
        cb_platform_max=cb_platform_max.get("name"),
        cb_platform_count=cb_platform_max.get("breadth"),
        hd_platform_max=hd_platform_max.get("name"),
        hd_platform_count=hd_platform_max.get("interaction"),

        cb_account_max=cb_account_max.get("name"),
        cb_account_count=cb_account_max.get("breadth"),
        hd_account_max=hd_account_max.get("name"),
        hd_account_count=hd_account_max.get("interaction"),

        cb_activity_max=cb_activity_max.get("name"),
        cb_activity_count=cb_activity_max.get("breadth"),
        hd_activity_max=hd_activity_max.get("name"),
        hd_activity_count=hd_activity_max.get("interaction"),

        source_max=source_max.get("name"),
        source_ratio=round(source_max.get("value", 0) * 100.0 / sum([x["value"] for x in platform_cumulative], 0.00001), 2),

        account_comment_max=source_max.get("name"),
        account_comment_ratio=round(account_comment_max.get("value", 0) * 100.0 / sum([x["value"] for x in user_type_composition], 0.00001), 2),

        ugc_count=data["spread_effectiveness"]["ugc_count"],
        activitys_ugc_count=data["spread_effectiveness"]["ugc_in_activity_count"],
        brands_ugc_count=data["spread_effectiveness"]["ugc_mentioned_brand_count"],
        activitys_brand_ugc_count=data["spread_effectiveness"]["ugc_intersect_count"],
        activitys_brand_ugc_ratio=round(data["spread_effectiveness"]["ugc_intersect_count"] * 100.0 / (data["spread_effectiveness"]["ugc_in_activity_count"] + 0.00001), 2),
        activity_ugc_max=activity_ugc_max.get("name"),
        activity_ugc_count=activity_ugc_max.get("value"),

        brand_ugc_pre_count=data["spread_effectiveness"]["predict"],
        brand_ugc_diff_count=abs(data["spread_effectiveness"]["predict"] - data["spread_effectiveness"]["ugc_in_activity_count"]),
        brand_ugc_diff_ratio=abs(round(data["spread_effectiveness"]["ugc_in_activity_count"] * 100.0 / (data["spread_effectiveness"]["predict"] + 0.00001), 2) - 1),

        brand_attention=data["brand_concern"]["activity"],
        brand_attention_year=data["brand_concern"]["annual"],
        brand_attention_ratio=abs(round(data["brand_concern"]["activity"] - data["brand_concern"]["annual"] * 100, 2)),

        sales_point_cognitive=data["tags_concern"]["activity"],
        sales_point_cognitive_year=data["tags_concern"]["annual"],
        sales_point=sales_point,
        sales_point_cognitive_ratio=abs(round(data["tags_concern"]["activity"] - data["tags_concern"]["annual"] * 100, 2)),

    )

    unscramble_rule = copy.deepcopy(sqls.unscramble_rule)
    for k in unscramble_rule.keys():
        unscramble = unscramble_rule[k]["unscramble"]
        unscramble = [rule[1].format(**param) for rule in unscramble if eval(rule[0].format(**param))]
        unscramble_rule[k]["unscramble"] = "".join(unscramble)

    return unscramble_rule


def report_unscramble_save(param, user):
    """
    编辑报告解读
    :param param:
    :param user:
    :return:
    """
    report = get_report(param["report_id"], user, status=(0, ))
    data = json.loads(report.data)

    data["unscramble"] = json.loads(param["content"])
    for k, v in data["unscramble"].iteritems():
        if v.pop("is_change", 0):
            v.update(user=user.username, date=datetime.datetime.now().strftime('%Y-%m-%d'))

    report.data = json.dumps(data)
    report.save()


def get_report(report_id, user, status):
    """
    校验是否有权操作报告
    :param report_id:
    :param user:
    :param status: 报告的状态
    :return:
    """
    reports = Report.objects.filter(id=report_id, user_id=user.id)
    if len(reports) < 1:
        raise Exception("权限不足")

    report = reports[0]
    if status and not report.status in status:
        raise Exception("报告还未就绪")

    return report


def report_config_create(param, user, ip):
    """
    生成报告
    :param param: 报告参数
    :param user: 当前用户
    :param ip: 用户 ip
    :return:
    """
    # 拼接帐号格式
    platforms = get_platform_info()
    platform = param["platform"]
    for k in platforms:
        k.update(children=[])
        for _ in platform:
            plat = DimPlatform.objects.get(id=_)
            if plat.parent == k.get("name"):
                k.get("children").append(dict(id=_, name=plat.name))
    param.update(
        user=user,
        tag=json.dumps(param["tag"]),
        accounts=json.dumps(param["accounts"]),
        platform=json.dumps(platforms),
    )

    # 如果输入了 report_id, 则为 编辑 报告配置
    report_id = param.pop("report_id")
    if report_id:
        report = get_report(report_id, user, status=(1, ))
        param.update(id=report_id, update_time=datetime.datetime.now(), create_time=report.create_time)

    param["sales_point"] = DimSalesPoint.objects.get(id=param["sales_point"])
    report = Report(**param)
    report.save()

    ReportStatus(report=report, status=1, ip=ip).save()
    return report

def get_report_config(report_id, user):
    """
    查看报告配置
    :param report_id: 报告id
    :param user: 当前用户
    :return:
    """
    report = get_report(report_id, user, status=None)
    report.accounts = json.loads(report.accounts)
    report.tag = json.loads(report.tag)
    report.platform = report.platform

    return report


def delete_report(user, report_id):
    # 只有生成成功之后的报告才能删除 公司管理员可以删除公司的所有报告， 普通用户只能删除自己的报告
    error_message = "只有生成之后的报告才能执行删除操作"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if user.is_admin:
        if report.status == 0 and report.user.corporation == user.corporation:
            report.delete = True
            report.save()
        else:
            raise Exception(error_message)
    else:
        if report.status == 0 and report.user.id == user.id:
            report.delete = True
            report.save()
        else:
            raise Exception(error_message)


def cancel_report(user, report_id):
    # 只有未处理的报告才能取消
    error_message = "只有未受理的报告才允许取消"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if user.is_admin:
        if report.status == 1 and report.user.corporation == user.corporation:
            report.delete = True
            report.save()
        else:
            raise Exception(error_message)
    else:
        if report.status == 1 and report.user.id == user.id:
            report.delete = True
            report.save()
        else:
            raise Exception(error_message)


def download_file(parametes):
    # 创建Excel内存对象，用StringIO填充
    output = BytesIO()
    writer = pandas.ExcelWriter(output, engine="xlsxwriter")
    parametes = DimPlatform.objects.filter(id__in=parametes).values_list('name', flat=True)
    dimension_df = pandas.DataFrame.from_records(list(), columns=["BGC/KOL", "所在地", "帐号"])
    for paramete in parametes:
        dimension_df.to_excel(writer, sheet_name=paramete, index=0)
    writer.save()
    output.seek(0)
    return output.getvalue(), "{0}.xlsx".format("template" + str(datetime.datetime.now().date()))


def read_excle(file):
    xl = pandas.ExcelFile(file)
    sheets = xl.sheet_names
    data_list =list()
    for num, value in enumerate(sheets):
        try:
            platform = DimPlatform.objects.get(name=value)
        except Exception:
            raise Exception("表名称不存在")
        df1 = pandas.read_excel(file, encoding="utf-8", sheet_name=sheets[num])
        if df1.empty:
            continue
        df1["platform_name"] = value
        df1["platform_id"] = platform.id
        dict_dfs = df1.to_dict("records")
        data_list.append(dict_dfs)
    return data_list


def make_form(report_id):
    # 创建Excel内存对象，用StringIO填充
    file_name = "{0}.xlsx".format("accounts" + str(datetime.datetime.now().date()))
    try:
        report_obj = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if report_obj.accounts:
        parametes = json.loads(report_obj.accounts)
        output = BytesIO()
        writer = pandas.ExcelWriter(output, engine="xlsxwriter")

        for paramete_list in parametes:
            dimension_df = pandas.DataFrame.from_records(paramete_list, columns=["BGC/KOL", "所在地", "帐号"])
            dimension_df.to_excel(writer, sheet_name=paramete_list[0].get("platform_name"), index=0)
        writer.save()
        output.seek(0)
    return output.getvalue() if report_obj.accounts else "", file_name


def update_report(report_id, status, data, ip):
    '''
    更新 报告状态
    :param report_id:
    :param status:
    :param data:
    :param ip:
    :return:
    '''
    try:
        report = Report.objects.get(id=report_id)
        report.status = status
        if data:
            report.data = json.dumps(data)
        report.save()

        ReportStatus(report=report, status=status, ip=ip).save()
    except:
        logger.error("[update_report request data]  report_id={0}, status={1}".format(report_id, status))
        return dict(code=500)

    return dict(code=200)


def get_reports(status=0):
    '''
    获取特定状态 的报告列表
    :param status:
    :return:
    '''
    try:
        reports = list(Report.objects.filter(status=status, delete=False).values(
            "id", "name", "industry__name", "tag", "monitor_start_date", "monitor_end_date",
            "platform", "accounts", "sales_point__name", "brand__name",
        ))
        map(lambda r: r.update(
            tag=json.loads(r["tag"]),
            accounts=json.loads(r["accounts"]),
            platform=json.loads(r["platform"]),
        ), reports)

    except:
        logger.error("[[get_report request data]]  status={}".format(status))
        return dict(code=500)

    return dict(code=200, data=reports)

