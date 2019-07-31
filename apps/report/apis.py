# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
from datetime import datetime
from django.db.models import F, Q, Func
from common.db_helper import DB
from io import BytesIO
from dateutil.relativedelta import relativedelta
import pandas
from compiler import ast
import sqls
import json


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


def test():
    pass


def get_report_list(user, report_status, monitor_end_time, monitor_cycle, key_word):
    # 刷选报告
    sql_format = []
    # values = ("monitor_start_date", "monitor_end_date", "create_time", "username", "status")
    db = DB()
    sql = "SELECT * FROM report ORDER BY create_time DESC"
    if report_status or monitor_end_time != "36500" or monitor_cycle != "36500" or key_word or(not(user.is_admin and user.user_type == 1)):
        sql = "SELECT * FROM report WHERE {} ORDER BY create_time DESC"

    if report_status:
        sql_format.append("{}={}".format("status", report_status))
    if monitor_end_time != "36500":
        if monitor_end_time == "30":
            sql_format.append("datediff(\'{}\', {})<{}".format(datetime.now(), "monitor_end_date", 30))
        elif monitor_end_time == "90":
            sql_format.append("datediff(\'{}\', {})<{}".format(datetime.now(), "monitor_end_date", 90))
        elif monitor_end_time == "180":
            sql_format.append("datediff(\'{}\', {})<{}".format(datetime.now(), "monitor_end_date", 180))
        elif monitor_end_time == "-180":
            sql_format.append("datediff(\'{}\', {})>{}".format(datetime.now(), "monitor_end_date", 180))
        else:
            raise Exception("monitor_end_time参数错误")

    if monitor_cycle != "36500":
        if monitor_cycle == "14":
            sql_format.append("datediff({}, {})<{}".format("monitor_end_date", "monitor_start_date", 14))
        elif monitor_cycle == "30":
            sql_format.append("datediff({}, {})<{}".format("monitor_end_date", "monitor_start_date", 30))
        elif monitor_cycle == "90":
            sql_format.append("datediff({}, {})<{}".format("monitor_end_date", "monitor_start_date", 90))
        elif monitor_cycle == "-90":
            sql_format.append("datediff({}, {})>{}".format("monitor_end_date", "monitor_start_date", 90))
        else:
            raise Exception("monitor_cycle 参数错误")

    if key_word:
        name = key_word.lower()
        user_list = SmUser.objects.annotate(name=Func(F("username"), function="LOWER"),
                                            ).filter(Q(name__contains=name)).values_list("id", flat=True)
        str_user_list = "".join([str(i) for i in user_list])

        sql_title = "{} like \'%{}%\'".format("name", key_word)
        if user_list:
            sql_name = "{} in ({})".format("user_id", str_user_list)
            sql_format.append("(" + sql_title + " or " + sql_name + ")")
        else:
            sql_format.append(sql_title)

    # 判断是管理员内部用户
    if user.is_admin and user.user_type == 1:
        pass
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
    if res:
        data = formatted_report(res)
    else:
        data = []
    return data


def formatted_report(reports):
    # 格式化表格
    data_format1 = "%Y-%m-%d"
    data_format2 = "%Y-%m-%d %H:%M:%S"

    for report in reports:
        # 一周内的报告加上NEW
        if report.get("create_time") >= datetime.now() - relativedelta(weeks=1):
            report.update(is_new=True)
        else:
            report.update(is_new=False)
        monitor_start_date = report.get("monitor_start_date").strftime(data_format1)
        monitor_end_date = report.get("monitor_end_date").strftime(data_format1)
        create_time = report.get("create_time").strftime(data_format2)
        report.update(monitor_start_date=monitor_start_date)
        report.update(create_time=create_time)
        report.update(monitor_end_date=monitor_end_date)
        status_values = Report.objects.get(id=report.get("id")).get_status_display()
        report.update(status_values=status_values)
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
    user = SmUser.objects.filter(id=2)
    report = Report.objects.filter(id=report_id, user_id=user.id)
    if len(report) < 1:
        raise Exception("权限不足")

    report = report[0]
    data = json.loads(report.data)
    if not data.get("unscramble"):
        data["unscramble"] = get_unscramble(data, report.sales_point.name)

    return data


def get_unscramble(data, sales_point):
    '''
    根据数据 获取解读结果
    :param data:
    :param sales_point:
    :return:
    '''
    activity_max = max(data["spread_overview"]["activity"], key=lambda x: x["value"])
    platform_max = max(ast.flatten([x["children"] for x in data["spread_overview"]["platform1"]]), key=lambda x: x["value"])
    platform_post_sum = sum([v["value"] for v in ast.flatten([x["children"] for x in data["spread_overview"]["platform1"]])])
    account_max_df = pandas.DataFrame(data["spread_overview"]["account"])
    account_max = account_max_df.drop_duplicates(subset=["account", "platform"]).groupby(["user_type"], as_index=False).agg({"account": pandas.Series.nunique}).sort_values("account", ascending=False).iloc[0]
    post_max = account_max_df.groupby(["user_type"], as_index=False).agg({"post_count": pandas.Series.sum}).sort_values("post_count", ascending=False).iloc[0]

    spread_efficiency = data["spread_efficiency"]["platform_cumulative"]
    cb_platform_max = max(spread_efficiency, key=lambda x: x["breadth"])
    hd_platform_max = max(spread_efficiency, key=lambda x: x["interaction"])

    account_cumulative = data["spread_efficiency"]["account_cumulative"]
    cb_account_max = max(account_cumulative, key=lambda x: x["breadth"])
    hd_account_max = max(account_cumulative, key=lambda x: x["interaction"])

    activity_cumulative = data["spread_efficiency"]["activity_cumulative"]
    cb_activity_max = max(activity_cumulative, key=lambda x: x["breadth"])
    hd_activity_max = max(activity_cumulative, key=lambda x: x["interaction"])

    platform_cumulative = data["spread_efficiency"]["platform_cumulative"]
    source_max = max(platform_cumulative, key=lambda x: x["value"])

    user_type_composition = data["spread_efficiency"]["user_type_composition"]
    account_comment_max = max(user_type_composition, key=lambda x: x["value"])

    activity_ugc_max = max(data["spread_effectiveness"]["activity_ugc_in_activity_composition"], key=lambda x: x["value"])

    param = dict(
        post_count=data["spread_overview"]["post_count"],
        account_all=data["spread_overview"]["account_count"],
        activity_count=len(data["spread_overview"]["activity"]),
        activity_max=activity_max["name"],
        activity_post_count=activity_max["value"],
        platform_max=platform_max["name"],
        platform_post_count=platform_max["value"],
        platform_max_ratio=round(platform_max["value"] * 100.0 / platform_post_sum, 2),
        account_max=account_max.user_type,
        account_count=account_max.account,
        post_max=post_max.user_type,
        account_post_max=post_max.post_count,

        platform_count=len(spread_efficiency),
        cb_platform_max=cb_platform_max["name"],
        cb_platform_count=cb_platform_max["breadth"],
        hd_platform_max=hd_platform_max["name"],
        hd_platform_count=hd_platform_max["interaction"],

        cb_account_max=cb_account_max["name"],
        cb_account_count=cb_account_max["breadth"],
        hd_account_max=hd_account_max["name"],
        hd_account_count=hd_account_max["interaction"],

        cb_activity_max=cb_activity_max["name"],
        cb_activity_count=cb_activity_max["breadth"],
        hd_activity_max=hd_activity_max["name"],
        hd_activity_count=hd_activity_max["interaction"],

        source_max=source_max["name"],
        source_ratio=round(source_max["value"] * 100.0 / sum([x["value"] for x in platform_cumulative]), 2),

        account_comment_max=source_max["name"],
        account_comment_ratio=round(account_comment_max["value"] * 100.0 / sum([x["value"] for x in user_type_composition]), 2),

        ugc_count=data["spread_effectiveness"]["ugc_count"],
        activitys_ugc_count=data["spread_effectiveness"]["ugc_in_activity_count"],
        brands_ugc_count=data["spread_effectiveness"]["ugc_mentioned_brand_count"],
        activitys_brand_ugc_count=data["spread_effectiveness"]["ugc_intersect_count"],
        activitys_brand_ugc_ratio=round(data["spread_effectiveness"]["ugc_intersect_count"] * 100.0 / data["spread_effectiveness"]["ugc_in_activity_count"], 2),
        activity_ugc_max=activity_ugc_max["name"],
        activity_ugc_count=activity_ugc_max["value"],

        brand_ugc_pre_count=data["spread_effectiveness"]["predict"],
        brand_ugc_diff_count=abs(data["spread_effectiveness"]["predict"] - data["spread_effectiveness"]["ugc_in_activity_count"]),
        brand_ugc_diff_ratio=abs(round(data["spread_effectiveness"]["ugc_in_activity_count"] * 100.0 / data["spread_effectiveness"]["predict"], 2) - 1),

        brand_attention=data["brand_concern"]["activity"],
        brand_attention_year=data["brand_concern"]["annual"],
        brand_attention_ratio=abs(round(data["brand_concern"]["activity"] - data["brand_concern"]["annual"] * 100, 2)),

        sales_point_cognitive=data["tags_concern"]["activity"],
        sales_point_cognitive_year=data["tags_concern"]["annual"],
        sales_point=sales_point,
        sales_point_cognitive_ratio=abs(round(data["tags_concern"]["activity"] - data["tags_concern"]["annual"] * 100, 2)),

    )

    for k in sqls.unscramble_rule.keys():
        unscramble = sqls.unscramble_rule[k]["unscramble"]
        unscramble = [rule[1].format(**param) for rule in unscramble if eval(rule[0].format(**param))]
        sqls.unscramble_rule[k]["unscramble"] = "".join(unscramble)

    return sqls.unscramble_rule


def report_config_create(param, user):
    """
    生成报告
    :param param: 报告参数
    :param user: 当前用户
    :return:
    """
    user = SmUser.objects.get(id=2)
    param.update(user=user)

    if param["report_id"]:
        reports = Report.objects.filter(id=param["report_id"], user_id=user.id)
        if len(reports) < 1:
            raise Exception("权限不足")

        param.update(id=param.pop("report_id"), update_time=datetime.now(), create_time=reports[0].create_time)

    Report(**param).save()


def get_report_config(report_id, user):
    """
    生成报告
    :param report_id: 报告id
    :param user: 当前用户
    :return:
    """
    user = SmUser.objects.get(id=2)

    reports = Report.objects.filter(id=report_id, user_id=user.id).values()
    if len(reports) < 1:
        raise Exception("权限不足")

    return reports[0]


def delete_report(user, report_id):
    # 只有生成成功之后的报告才能删除 公司管理员可以删除公司的所有报告， 普通用户只能删除自己的报告
    error_message = "报告未生成,不允许删除"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if user.is_admin:
        if report.status == 0 and report.user.corporation == user.corporation:
            report.delete()
        else:
            raise Exception(error_message)
    else:
        if report.status == 0 and report.user.id == user.id:
            report.delete()
        else:
            raise Exception(error_message)


def cancel_report(user, report_id):
    # 只有未处理的报告才能取消
    error_message = "报告已经被受理,不允许取消"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if user.is_admin:
        if report.status == 1 and report.user.corporation == user.corporation:
            report.delete()
        else:
            raise Exception(error_message)
    else:
        if report.status == 1 and report.user.id == user.id:
            report.delete()
        else:
            raise Exception(error_message)


def download_file(parametes):
    # 创建Excel内存对象，用StringIO填充
    output = BytesIO()
    writer = pandas.ExcelWriter(output, engine="xlsxwriter")

    dimension_df = pandas.DataFrame.from_records(list(), columns=["BGL/KOL", "所在地", "帐号"])
    for paramete in parametes:
        dimension_df.to_excel(writer, sheet_name=paramete, index=0)
    writer.save()
    output.seek(0)
    return output.getvalue(), "{0}.xlsx".format("template" + str(datetime.now().date()))


def read_excle(file):
    xl = pandas.ExcelFile(file)
    sheets = xl.sheet_names
    data_list =list()
    for num, value in enumerate(sheets):
        df1 = pandas.read_excel(file, encoding="utf-8", sheet_name=sheets[num])
        df1["name"] = value
        dict_dfs = df1.to_dict("records")
        data_list.append(dict_dfs)
    return data_list


def make_form(report_id):
    # 创建Excel内存对象，用StringIO填充
    file_name = "{0}.xlsx".format("accounts" + str(datetime.now().date()))
    try:
        report_obj = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if report_obj.accounts:
        parametes = json.loads(report_obj.accounts)
        output = BytesIO()
        writer = pandas.ExcelWriter(output, engine="xlsxwriter")

        for paramete_list in parametes:
            dimension_df = pandas.DataFrame.from_records(paramete_list, columns=["BGL/KOL", "所在地", "帐号"])
            dimension_df.to_excel(writer, sheet_name=paramete_list[0].get("name"), index=0)
        writer.save()
        output.seek(0)
    return output.getvalue() if report_obj.accounts else "", file_name
