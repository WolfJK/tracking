# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
from common.db_helper import DB
from io import BytesIO
from dateutil.relativedelta import relativedelta
import pandas
from compiler import ast
import sqls
import json
import datetime
import copy
from common.logger import Logger
from apps.commons.apis import get_platform_info
import apps.apis as apps_apis
from itertools import chain
from django.db.models import F
import pdb


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
    sql_format = ["status>=-1", ]
    db = DB()
    sql = "SELECT report.* FROM report join sm_user on report.user_id=sm_user.id WHERE `delete`=false and {} ORDER BY create_time DESC"
    # sql = "SELECT report.* FROM report where `delete`=false and status>=0 ORDER BY status DESC, create_time DESC"
    # if report_status != "100" or monitor_end_time != "36500" or monitor_cycle != "36500" or key_word or(not(user.is_admin and user.user_type == 1)):
    #     sql = "SELECT report.* FROM report WHERE `delete`=false and  {} ORDER BY status DESC, create_time DESC"
    if report_status != "100":
        if int(report_status) >= 2:
            # sql_format.append("{}>={}".format("status", report_status))
            sql_format.append("status in (-1, 2, 3, 4, 5, 6)")
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
        sql_title = "LOWER(report.name) like '%{}%'".format(key_word.lower())
        sql_name = "LOWER(sm_user.username) like '%{}%'".format(key_word.lower())
        report_title = "LOWER(report.title) like '%{}%'".format(key_word.lower())
        report_brand = "LOWER(report.brand_id) like '%{}%'".format(key_word.lower())
        sql_format.append("(" + sql_title + " OR " + sql_name + " OR " + report_title + " OR " + report_brand + ")")

    # 判断是管理员内部用户
    # if user.is_admin and user.user_type == 1:
    #     pass
    # elif user.is_admin:
    #     # sql = sql_join
    #     corporation = user.corporation
    #     sql_user = "{}='{}'".format("sm_user.corporation", corporation)
    #     sql_format.append(sql_user)
    if not user.is_admin:
        # user_id = user.id
        # sql_user = "{}={}".format("user_id", user_id)
        corporation = user.corporation
        sql_user = "{}='{}'".format("sm_user.corporation", corporation)
        sql_format.append(sql_user)

    if sql_format:
        sql_format = " and ".join(sql_format)
        sql = sql.format(sql_format)
    res = db.search(sql)

    report_create_list = list()  # 状态 >2 或者 等于 -1
    success_list = list()  # 状态0
    commit_list = list()   # 状态1
    for report in res:

        if report.get("status") >= 2:
            report_create_list.append(report)
        elif report.get('status') == -1:
            report_create_list.append(report)
        elif report.get("status") == 1:
            commit_list.append(report)
        else:
            success_list.append(report)
    report_create_list.extend(commit_list)
    report_create_list.extend(success_list)
    return formatted_report(report_create_list) if res else []


def formatted_report(reports):
    # 格式化表格
    data_format1 = "%Y-%m-%d"
    data_format2 = "%Y-%m-%d %H:%M:%S"

    for report in reports:
        report.pop("data")  # 数据太大 去除data
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
        report.update(tag=json.loads(report.get("tag")))
        report.update(accounts=json.loads(report.get("accounts")))
        report.update(competitors=[c.split("-")[-1].split("_")[1] for c in json.loads(report.get("competitors"))])
        brand_list = json.loads(report.get("brand_id"))
        brand_id = brand_list[-1].split("_")[0]
        brand_name = brand_list[-1].split("_")[1]
        report.update(brand_id=brand_id)
        report.update(brand_name=brand_name)
        report.update(industry_name=DimIndustry.objects.get(id=report.get("industry_id")).name)
        report.update(category_name=DimCategory.objects.get(id=report.get("category_id")).name)

        report.update(sales_point_name=json.loads(report["sales_points"]))
        report.update(sales_points=json.loads(report["sales_points"]))
        if user.brand.name == brand_name:
            report.update(is_owner="本品")
        else:
            report.update(is_owner="竞品")
    return reports


def get_common_info():

    return report_affilication, report_status, report_monitor_end_time, monitor_cycle


def report_details(report_id, user, need_unscramble=True):
    """
    生成报告详情
    聚合结果为0时，是不出现在数据里的，需要后端补全, 也可能出现长度为0的列表
    :param report_id:
    :param user: 当前用户
    :param need_unscramble: 是否需要解读
    :return:
    """

    report = get_report(report_id, user, status=(0, ))
    brand = ".".join([b.split("_")[1] for b in json.loads(report.brand_id)])
    sales_points = json.loads(report.sales_points)

    config = dict(sales_points=sales_points, brand=brand, activity=report.title)
    data = data_transform(json.loads(report.data), config)

    if not data.get("unscramble") and need_unscramble:
        data["unscramble"] = get_unscramble(data, sales_points)

    for i in range(len(data["tags_concern"])):
        data["tags_concern"][i]["name"] = sales_points[i].split("_")[1]

    data["report_config"] = dict(
        id=report.id,
        start_date=report.monitor_start_date,
        end_date=report.monitor_end_date,
        name=report.name,
        brand=brand,
        activity=report.title,
        period=(report.monitor_end_date - report.monitor_start_date).days + 1,
        status_value=report.get_status_display(),
        status=report.status,
        reprot_period=get_reprot_period(report.monitor_start_date, report.monitor_end_date)
    )

    return data


def data_transform(data, config):
    """
    将 etl 格式的数据 转换为 web 格式
    :param data: etl 数据
    :param config: 活动的配置
    :return:
    """
    sales_points = config["sales_points"]
    brand = config["brand"]
    activity = config["activity"]

    # 投放渠道分布 转换
    platform = data["spread_overview"]["platform"]
    platform_web = []
    if platform["weibo"] != 0:
        platform_web.append(dict(
            name="微博",
            brand=brand,
            value=platform["weibo"],
            children=[dict(name="微博", value=platform["weibo"], brand=brand, activity=activity)]
        ))

    if len(platform["motherbaby"]) > 0:
        map(lambda x: x.update(brand=brand, activity=activity), platform["motherbaby"])
        platform_web.append(dict(
            name="母垂",
            brand=brand,
            value=sum([x["value"] for x in platform["motherbaby"]]),
            children=platform["motherbaby"]
        ))

    data["spread_overview"]["platform_web"] = platform_web

    # 投放账号分布
    account_max_df = pandas.DataFrame(data["spread_overview"]["account"], columns=["account", "platform", "post_count", "user_type"])
    account_web = account_max_df.drop_duplicates(subset=["account", "platform", "user_type"]).groupby(["user_type"], as_index=False)["account"].count()
    post_web = account_max_df.groupby(["user_type"], as_index=False).agg({"post_count": pandas.Series.sum})

    account_web = pandas.merge(account_web, post_web, how="left", on="user_type")
    account_web["brand"] = brand
    account_web["activity"] = activity
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
    brand_ugc.sort(key=lambda x: x["date"])
    # brand_ugc.append(dict(
    #     date=apps_apis.next_period(brand_ugc[-1]["date"]),
    #     value=data["spread_effectiveness"]["ugc_mentioned_brand_count"],
    #     value_year=data["spread_effectiveness"]["predict"]
    # ))
    data["spread_effectiveness"]["brand_ugc_web"] = brand_ugc

    # 品牌关注度
    map(lambda x: x.update(dict(value_year=data["brand_concern"]["annual"])), data["brand_concern"]["trend"])
    data["brand_concern"]["trend"].sort(key=lambda x: x["date"])
    # data["brand_concern"]["trend"].append(dict(
    #     date=apps_apis.next_period(data["brand_concern"]["trend"][-1]["date"]),
    #     value=data["brand_concern"]["activity"],
    #     value_year=data["brand_concern"]["annual"]
    # ))

    # 单独处理 tags_concern
    tags_concern(data, sales_points)

    # 精度修正
    apps_apis.set_precision(data["spread_effectiveness"]["brand_ugc_web"], keys=("value", "value_year"), precision=1)
    apps_apis.set_precision(data["spread_effectiveness"]["annual_average_trend"], keys=("value",), precision=1)
    apps_apis.set_precision(data["spread_effectiveness"], keys=("predict", "delta_absolute"), precision=0)
    apps_apis.set_precision(data["spread_effectiveness"], keys=("delta", ), precision=1, pct=100.0)

    apps_apis.set_precision(data["brand_concern"]["trend"], keys=("value", "value_year"), precision=1, pct=100.0)
    apps_apis.set_precision(data["brand_concern"], keys=("annual", "activity", "delta"), precision=1, pct=100.0)

    map(lambda x: x.update(brand=brand, activity=activity), data["spread_efficiency"]["activity_composition"])
    map(lambda x: x.update(brand=brand, activity=activity), data["spread_efficiency"]["user_type_composition"])

    apps_apis.ratio(data["spread_efficiency"]["activity_composition"], "value", precision=1)
    apps_apis.ratio(data["spread_efficiency"]["user_type_composition"], "value", precision=1)

    apps_apis.set_precision(data["spread_efficiency"]["platform_web"], keys=("avg_breadth", ), precision=1)
    apps_apis.set_precision(data["spread_efficiency"]["account_web"], keys=("avg_breadth", ), precision=1)
    apps_apis.set_precision(data["spread_efficiency"]["activity_web"], keys=("avg_breadth", ), precision=1)

    data["spread_overview"]["trend"].sort(key=lambda x: x["date"])
    data["spread_effectiveness"]["brand_ugc_web"].sort(key=lambda x: x["date"])
    data["spread_effectiveness"]["annual_average_trend"].sort(key=lambda x: x["date"])

    return data


def tags_concern(data, sales_points):
    '''
    处理 tags_concern 的数据
    :param data:
    :param sales_points:
    :return:
    '''
    if len(sales_points) == 0:
        return

    for i in range(len(data["tags_concern"])):
        tags_concern = data["tags_concern"][i]
        map(lambda x: x.update(dict(value_year=tags_concern["annual"])), tags_concern["trend"])
        tags_concern["trend"].sort(key=lambda x: x["date"])
        # tags_concern["trend"].append(dict(
        #     date=apps_apis.next_period(tags_concern["trend"][-1]["date"]),
        #     value=tags_concern["activity"],
        #     value_year=tags_concern["annual"]
        # ))

        apps_apis.set_precision(tags_concern["trend"], keys=("value", "value_year"), precision=1, pct=100.0)
        apps_apis.set_precision(tags_concern, keys=("annual", "activity", "delta"), precision=1, pct=100.0)
        tags_concern.update(sales_point=sales_points[i].split("_")[1], index=i)


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


def get_unscramble(data, sales_points):
    '''
    根据数据 获取解读结果
    :param data:
    :param sales_points:
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

    activity_composition = data["spread_efficiency"]["activity_composition"]
    if activity_composition:
        source_max = max(activity_composition, key=lambda x: x["value"])

    user_type_composition = data["spread_efficiency"]["user_type_composition"]
    account_comment_max = max(user_type_composition, key=lambda x: x["value"])

    if data["spread_effectiveness"]["activity_ugc_in"]:
        activity_ugc_max = max(data["spread_effectiveness"]["activity_ugc_in"], key=lambda x: x.get("value", 0) + x.get("unvalue", 0))

    param = dict(
        post_count=data["spread_overview"]["post_count"],
        account_all=data["spread_overview"]["account_count"],
        activity_count=len(data["spread_overview"]["activity"]),
        activity_max=activity_max.get("name"),
        activity_post_count=int(round(activity_max.get("value", 0))),
        platform_max=platform_max.get("name"),
        platform_post_count=int(round(platform_max.get("value", 0))),
        platform_max_ratio=round(platform_max.get("value", 0) * 100.0 / platform_post_sum, 1),
        account_max=account_max.get("user_type"),
        account_count=int(round(account_max.get("account", 0))),
        account_post_max=account_post_max.get("user_type"),
        account_post_count=int(round(account_post_max.get("post_count", 0))),

        platform_count=len(spread_efficiency),
        cb_platform_max=cb_platform_max.get("name"),
        cb_platform_count=int(round(cb_platform_max.get("breadth", 0))),
        hd_platform_max=hd_platform_max.get("name"),
        hd_platform_count=int(round(hd_platform_max.get("interaction", 0))),

        cb_account_max=cb_account_max.get("name"),
        cb_account_count=int(round(cb_account_max.get("breadth", 0))),
        hd_account_max=hd_account_max.get("name"),
        hd_account_count=int(round(hd_account_max.get("interaction", 0))),

        cb_activity_max=cb_activity_max.get("name"),
        cb_activity_count=int(round(cb_activity_max.get("breadth", 0))),
        hd_activity_max=hd_activity_max.get("name"),
        hd_activity_count=int(round(hd_activity_max.get("interaction", 0))),

        source_max=source_max.get("name"),
        source_ratio=round(source_max.get("value", 0) * 100.0 / sum([x["value"] for x in activity_composition], 0.00001), 1),

        account_comment_max=account_comment_max.get("name"),
        account_comment_ratio=round(account_comment_max.get("value", 0) * 100.0 / sum([x["value"] for x in user_type_composition], 0.00001), 1),

        ugc_count=int(round(data["spread_effectiveness"]["ugc_count"])),
        activitys_ugc_count=int(round(data["spread_effectiveness"]["ugc_mentioned_brand_count"])),
        brands_ugc_count=int(round(data["spread_effectiveness"]["ugc_mentioned_brand_count"])),
        activitys_brand_ugc_count=int(round(data["spread_effectiveness"]["ugc_intersect_count"])),
        activitys_brand_ugc_ratio=round(data["spread_effectiveness"]["ugc_intersect_count"] * 100.0 / (data["spread_effectiveness"]["ugc_in_activity_count"] + 0.00001), 1),
        activity_ugc_max=activity_ugc_max.get("name"),
        activity_ugc_count=int(round(activity_ugc_max.get("value", 0) + activity_ugc_max.get("unvalue", 0))),

        brand_ugc_pre_count=int(round(data["spread_effectiveness"]["predict"])),
        brand_ugc_diff_count=int(round(abs(data["spread_effectiveness"]["predict"] - data["spread_effectiveness"]["ugc_mentioned_brand_count"]))),
        brand_ugc_diff_ratio=abs(round(data["spread_effectiveness"]["ugc_mentioned_brand_count"] * 100.0 / (data["spread_effectiveness"]["predict"] + 0.00001), 1) - 1),

        brand_attention=data["brand_concern"]["activity"],
        brand_attention_year=data["brand_concern"]["annual"],
        brand_attention_ratio=abs(data["brand_concern"]["delta"]),
    )

    # 处理 sales_points
    sp_unscramble = []
    for i in range(len(data["tags_concern"])):
        sp_param = dict(
            sales_point_cognitive=data["tags_concern"][i]["activity"],
            sales_point_cognitive_year=data["tags_concern"][i]["annual"],
            sales_point_cognitive_ratio=abs(data["tags_concern"][i]["delta"]),
            sales_point=sales_points[i].split("_")[1],
        )

        sp_unscramble.append(unscramble("effect_sales_point", sp_param)["unscramble"])

    unscramble_rule = dict(effect_sales_point=dict(unscramble="\n\n".join(sp_unscramble), user=None, date=None))
    # 处理其他
    for k in sqls.unscramble_rule.keys():
        if k == "effect_sales_point":
            continue
        unscramble_rule.update({k: unscramble(k, param)})

    return unscramble_rule


def unscramble(unscramble_type, param):
    '''
    传入参数, 进行 解读
    :param unscramble_type:
    :param param:
    :return:
    '''
    template = copy.deepcopy(sqls.unscramble_rule[unscramble_type])
    unscramble = [rule[1].format(**param) for rule in template["unscramble"] if eval(rule[0].format(**param))]
    template["unscramble"] = "".join(unscramble)

    return template


def get_reprot_period(begin, end):
    '''
    获取 报告 所跨的周 和 月
    :param begin:
    :param end:
    :return:
    '''
    period = DimDate.objects.filter(date__range=[begin, end])

    return dict(
        week_period=list(period.values("week").distinct().order_by("week")),
        month_period=list(period.values("month").distinct().order_by("month"))
    )


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
        if v.pop("state", 0):
            v.update(user=user.username, date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    report.data = json.dumps(data, ensure_ascii=False)
    report.save()

    return data


def get_report(report_id, user, status):
    """
    校验是否有权操作报告
    :param report_id:
    :param user:
    :param status: 报告的状态
    :return:
    """
    reports = Report.objects.filter(id=report_id, delete=False)
    if not user.is_admin:
        reports = reports.filter(user__corporation=user.corporation)

    if len(reports) < 1:
        raise Exception("权限不足/报告不存在")

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
    return_list = list()
    for k in platforms:
        k.update(children=[])
        for _ in platform:
            plat = DimPlatform.objects.get(code=_)
            if plat.parent == k.get("name"):
                k.get("children").append(dict(id=_, name=plat.name))
        if k.get("children"):
            return_list.append(k)

    param.update(
        user=user,
        tag=json.dumps(param["tag"], ensure_ascii=False),
        platform=json.dumps(return_list, ensure_ascii=False),
        competitors=json.dumps(param["competitors"], ensure_ascii=False),
        brand_id=json.dumps(param["brand_id"], ensure_ascii=False),
        sales_points=json.dumps(param["sales_points"], ensure_ascii=False),
    )
    # 判断帐号类型 # 判断如果选择的是url则清空关键字和投放平台，不启用bgc，kol库
    # 清楚活动关键字和投放平台 url链接的投放平台是通过链接来判定的
    accounts = param["accounts"]
    accounts.update(choose_bgc=param['bgc'])
    accounts.update(choose_kol=param['kol'])
    # if accounts:
    #     if accounts.get('url'):
    #         accounts.update(type=list())
    #     else:
    #         accounts.update(type=param["type"])
    # else:
    #     accounts.update(url=list(), bgc=list(), kol=list(), type=param["type"] )
    param.pop('bgc')
    param.pop('kol')

    param.update(accounts=json.dumps(accounts, ensure_ascii=False))

    report_id = param.pop("report_id")
    reports = Report.objects.filter(name=param["name"], user__corporation=user.corporation, delete=False)

    if len(reports) > 0 and (not report_id or report_id != reports[0].id):
        raise Exception("报告已经存在")

    # 如果输入了 report_id, 则为 编辑 报告配置
    if report_id:
        report = get_report(report_id, user, status=(1, ))
        param.update(id=report_id, update_time=datetime.datetime.now(), create_time=report.create_time)

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
    report = get_report(report_id, user, status=(0, 1, 2, 3, 4, 5, 6))
    return report


def activity_contrast(param, user):
    '''
    活动对比
    :param param:
    :param user:
    :return:
    '''
    # 1、获取报告
    reports = [report_details(report_id, user) for report_id in param["report_ids"]]

    # 2、处理 活动对比历史记录保存, 注意: 需要获取数据库的 history, 不能走缓存的 history
    activity_contrast_history = json.loads(SmUser.objects.get(id=user.id).activity_contrast_history)
    if set(param["report_ids"]) != set(activity_contrast_history):
        user.activity_contrast_history = json.dumps(param["report_ids"], ensure_ascii=False)
        user.save()

    all_platform, datas = [], []
    # 3、数据规整
    for report in reports:
        brand = report["report_config"]["brand"]
        platform_web = report["spread_overview"]["platform_web"]
        platforms = [p for p in chain.from_iterable([platform["children"] for platform in platform_web])]

        all_platform.append([m["name"] for m in platforms])

        composition = {us["type"]: us["value"] for us in report["spread_effectiveness"]["ugc_in_activity_composition"]}
        datas.append(dict(
            id=report["report_config"]["id"],
            brand=brand,
            activity=report["report_config"]["activity"],
            name=report["report_config"]["name"],
            start_date=report["report_config"]["start_date"],
            end_date=report["report_config"]["end_date"],

            platform_overview={m["name"]: m for m in platforms},
            account_overview=report["spread_overview"]["account_web"],

            platform_efficiency=report["spread_efficiency"]["platform_web"],
            account_efficiency=report["spread_efficiency"]["account_web"],
            activity_efficiency=report["spread_efficiency"]["activity_web"],

            activity_composition_efficiency=report["spread_efficiency"]["activity_composition"],
            user_type_efficiency=report["spread_efficiency"]["user_type_composition"],

            # 传播效果对比 -> 活动期间UGC总计
            ugc_count_effectiveness=report["spread_effectiveness"]["ugc_count"],
            # 传播效果对比 -> 活动 UGC【活动 ugc 构成】
            ugc_in_activity_composition={
                "提及品牌": composition.get("提及品牌", 0),
                "未提及品牌": composition.get("未提及品牌", 0)
            },

            # 品牌 UGC -> 活动期品牌 ugc
            ugc_in_activity_count=report["spread_effectiveness"]["ugc_mentioned_brand_count"],
            # 品牌 UGC -> 活动对品牌 ugc 的贡献度
            delta_absolute=report["spread_effectiveness"]["delta_absolute"],

            # 品牌关注度 -> 活动品牌关注[活动期实际品牌关注度]
            activity_brand_concern=report["brand_concern"]["activity"],
            # 品牌关注度 -> 活动对品牌关注贡献度
            delta_brand_concern=report["brand_concern"]["delta"],
        ))

    all_platform = list(set(chain.from_iterable(all_platform)))
    # 4、数据处理
    for data in datas:
        data["platform_overview"] = [data["platform_overview"].get(
            platform,
            dict(name=platform, value=0, brand=data["brand"], activity=data["activity"])
        ) for platform in all_platform]

        data["platform_all_efficiency"] = dict(
            brand=data["brand"],
            activity=data["activity"],
            value=sum([s["value"] for s in data["platform_efficiency"]]),
            avg_value=sum([s["avg_value"] for s in data["platform_efficiency"]]),
            breadth=sum([s["breadth"] for s in data["platform_efficiency"]]),
            avg_breadth=sum([s["avg_breadth"] for s in data["platform_efficiency"]]),
            interaction=sum([s["interaction"] for s in data["platform_efficiency"]]),
            avg_interaction=sum([s["avg_interaction"] for s in data["platform_efficiency"]]),
        )

    # 5、提取 efficiency, 并 进行 flat_map
    def __flat_map(datas, efficiency):
        array = []
        for data in datas:
            array.append([dict(
                brand=data["brand"],
                name=e["name"],
                activity=data["activity"],
                value=e["value"],
                avg_value=e["avg_value"],
                interaction=e["interaction"],
                avg_interaction=e["avg_interaction"],
                breadth=e["breadth"],
                avg_breadth=e["avg_breadth"],
            ) for e in data.pop(efficiency)]
                         )

        return list(chain.from_iterable(array))

    # 6、进行 efficiency 处理
    efficiency = dict(
        platform_all=[data.pop("platform_all_efficiency") for data in datas],
        platform_efficiency=__flat_map(datas, "platform_efficiency"),
        account_efficiency=__flat_map(datas, "account_efficiency"),
        activity_efficiency=__flat_map(datas, "activity_efficiency"),
    )

    # 7、进行 传播实况对比 提取
    spread_the_facts = {
        "platform_overview": [data.pop("platform_overview") for data in datas],
        "account_overview": [data.pop("account_overview") for data in datas],
        "activity_composition_efficiency": [data.pop("activity_composition_efficiency") for data in datas],
        "user_type_efficiency": [data.pop("user_type_efficiency") for data in datas],
    }

    return dict(efficiency=efficiency, data=datas, spread_the_facts=spread_the_facts)


def get_competitor(param, user):
    '''
    根据 品类品牌 获取 品牌竞品列表
    :param param:
    :param user:
    :return:
    '''
    competitor = list(SmCompetitor.objects
                      .filter(category_id=param["category_id"], user__corporation=user.corporation, brand=json.dumps(param["brand"], ensure_ascii=False))
                      .values_list("competitors", flat=True))

    if len(competitor) > 0:
        return json.loads(competitor[0])

    return []


def delete_report(user, report_id):
    # 只有生成成功之后的报告才能删除
    error_message = "只有生成之后的报告才能执行删除操作或你没有权限"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")
    # if user.is_admin:
    #     if report.status == 0 and report.user.corporation == user.corporation:
    #         report.delete = True
    #         report.save()
    #     else:
    #         raise Exception(error_message)
    # else:
    if report.status == 0 and report.user.id == user.id:
        report.delete = True
        report.save()
    else:
        raise Exception(error_message)


def cancel_report(user, report_id):
    # 只有未处理的报告才能取消
    error_message = "只有未受理的报告才允许取消或你没有权限"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")
    #
    # if user.is_admin:
    #     if report.status == 1 and report.user.corporation == user.corporation:
    #         report.delete = True
    #         report.save()
    #     else:
    #         raise Exception(error_message)
    # else:
    if report.status == 1 and report.user.id == user.id:
        report.delete = True
        report.save()
    else:
        raise Exception(error_message)


def download_file(parametes, flag):
    # 创建Excel内存对象，用StringIO填充
    output = BytesIO()
    writer = pandas.ExcelWriter(output, engine="xlsxwriter")
    if flag in ["1", "2"]:
        parametes = DimPlatform.objects.filter(code__in=parametes).values_list('name', flat=True)
        # dimension_df = pandas.DataFrame.from_records(list(), columns=["BGC/KOL", "所在地", "帐号"])
        dimension_df = pandas.DataFrame.from_records(list(), columns=["所在地", "帐号"])
        for paramete in parametes:
            dimension_df.to_excel(writer, sheet_name=paramete, index=0)
    else:
        dimension_df = pandas.DataFrame.from_records(list(), columns=["帖子链接(必填)", "帐号类型(必填)", "子活动名称(选填总类型不超过5类)"])
        dimension_df.to_excel(writer, sheet_name="链接列表", index=0)
    writer.save()
    output.seek(0)
    return output.getvalue(), "{0}.xlsx".format("template" + str(datetime.datetime.now().date()))


def read_excle(file):
    xl = pandas.ExcelFile(file)
    sheets = xl.sheet_names
    data_list =list()
    # 验证帐号

    def verify_account(value):
        if value.lower() not in ("bgc", "kol"):
            raise Exception("填写的帐号名必须是BGC或者KOL")

    for num, value in enumerate(sheets):
        try:
            platform = DimPlatform.objects.get(name=value)
        except Exception:
            raise Exception("表名称不存在,请按照下载模板填写")
        df1 = pandas.read_excel(file, encoding="utf-8", sheetname=sheets[num])
        df1["BGC/KOL"].apply(verify_account)
        df1.fillna("", inplace=True)
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
            report.data = json.dumps(data, ensure_ascii=False)
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
        reports = list(Report.objects.filter(status=status, delete=False).annotate(
            category_name=F("category__name"),
            industry_name=F("industry__name"),
        ).values("id", "name", "industry__name", "industry_name", "category_name", "tag", "monitor_start_date",
                 "monitor_end_date", "platform", "accounts", "sales_points", "brand_id", "competitors")
                       )

        map(lambda r: r.update(
            tag=json.loads(r["tag"]),
            accounts=json.loads(r["accounts"]),
            platform=json.loads(r["platform"]),
            sales_points=json.loads(r["sales_points"]),
            brand_id=json.loads(r["brand_id"]),
            competitors=json.loads(r["competitors"]),
        ), reports)

    except:
        logger.error("[[get_report request data]]  status={}".format(status))
        return dict(code=500)

    return dict(code=200, data=reports)


def read_url_excle(file_url):
    """
    处理url链接的的帐号数据
    :param file_url:
    :return:
    """
    xl = pandas.ExcelFile(file_url)
    sheets = xl.sheet_names
    if "链接列表" not in sheets:
        raise Exception("缺少表名字链接列表")
    num = sheets.index("链接列表")
    # 验证帐号
    data_dict = dict()

    def verify_account(value):
        if value.lower() not in ("bgc", "kol"):
            raise Exception("填写的帐号类型必须是BGC或者KOL")

    def verify_is_null(value):
        if not value:
            raise Exception("填写的帖子链接不能为空")

    def verify_type_is_null(value):
        if not value:
            raise Exception("填写的帐号类型不能为空")

    df1 = pandas.read_excel(xl, encoding="utf-8", sheetname=sheets[num])
    if df1.empty:
        raise Exception("上传的url不能为空")
    if ("帐号类型(必填)" and "帖子链接(必填)" and "子活动名称(选填总类型不超过5类)") not in df1.keys():
        raise Exception("请按照模板抬头填写注意抬头是否和模板对应,帐号类型(必填), 帖子链接(必填), 子活动名称(选填总类型不超过5类)")
    df1 = df1[["帐号类型(必填)", "帖子链接(必填)", "子活动名称(选填总类型不超过5类)"]]
    df1.fillna("", inplace=True)
    df1["帐号类型(必填)"].apply(verify_type_is_null)
    df1["帐号类型(必填)"].apply(verify_account)
    df1["帖子链接(必填)"].apply(verify_is_null)

    dict_dfs = df1.to_dict("records")
    data_dict.update(url=dict_dfs)
    data_dict.update(kol=list())
    data_dict.update(bgc=list())
    return data_dict


def read_bgc_kol_excle(file_kol, file_bgc):
    data_dict = dict()
    data_dict.update(url=list())

    def verify_is_null(value):
        if not value:
            raise Exception("填写的帐号不能为空")

    def get_data_from_df(sheets, file, flag):
        list_data = list()
        for num, value in enumerate(sheets):
            dict_platform = dict()
            try:
                platform = DimPlatform.objects.get(name=value)
            except Exception:
                raise Exception("表名称不存在,请按照下载模板填写")
            df1 = pandas.read_excel(file, encoding="utf-8", sheetname=value)
            # df1["BGC/KOL"].apply(verify_account)
            if("所在地" and "帐号") not in df1.keys():
                raise Exception("表名称必须含有列所在地, 帐号")
            df1 = df1[["所在地", "帐号"]]
            df1.fillna("", inplace=True)
            df1["帐号"].apply(verify_is_null)
            if df1.empty:
                continue
            df1["platform_name"] = value
            df1["platform_id"] = platform.id
            if flag == 1:
                df1["type"] = "bgc"
            else:
                df1["type"] = "kol"
            dict_dfs = df1.to_dict("records")
            dict_platform.update({platform.id: dict_dfs})
            list_data.append(dict_platform)
        if flag == 1:
            data_dict.update(bgc=list_data)
        else:
            data_dict.update(kol=list_data)

    def get_file(filename):
        xl = pandas.ExcelFile(filename)
        sheets = xl.sheet_names
        return xl, sheets

    if file_kol:
        xl_kol, sheets_kol = get_file(file_kol)
        get_data_from_df(sheets_kol, xl_kol, flag=2)
    else:
        data_dict.update(kol=list())
    if file_bgc:
        xl_bgc, sheets_bgc = get_file(file_bgc)
        get_data_from_df(sheets_bgc, xl_bgc, flag=1)
    else:
        data_dict.update(bgc=list())
    return data_dict


def make_new_form(report_id):
    # 创建Excel内存对象，用StringIO填充
    file_name = "{0}.xlsx".format("accounts" + str(datetime.datetime.now().date()))
    try:
        report_obj = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if report_obj.accounts:
        """
            分为 url帐号
                bgc帐号  下面两个帐号合并下载
                kol帐号
        """
        parametes = json.loads(report_obj.accounts)
        output = BytesIO()
        writer = pandas.ExcelWriter(output, engine="xlsxwriter")

        dict_all = dict()
        for key, value in parametes.items():
            # 把相同平台的帐号合并到一起然后开始生成 excle
            if key in ["bgc", "kol"]:
                for list_account in value:
                    for pla_id, val_list in list_account.items():
                        if dict_all.get(pla_id):
                            dict_all.get(pla_id).extend(val_list)
                        else:
                            dict_all.update({pla_id: val_list})
            # 下载 url 帖子链接
            if key in ["url", ] and value:
                df = pandas.DataFrame.from_records(value)
                df_download = df[["帖子链接(必填)", "帐号类型(必填)", "子活动名称(选填总类型不超过5类)"]]
                df_download.to_excel(writer, sheet_name="链接列表", index=0)

        # 下载bgc或者kol
        if dict_all:
            for platform_id, dict_account in dict_all.items():
                df = pandas.DataFrame.from_dict(dict_account)
                df_download = df[["type", "所在地", "帐号"]]
                df_download["BGC/KOL"] = df_download['type']
                for value_list in dict_account:
                    df_download.to_excel(writer, sheet_name=value_list.get("platform_name"), index=0,
                                         columns=["BGC/KOL", "所在地", "帐号"])
        writer.save()
        output.seek(0)

    return output.getvalue() if report_obj.accounts else "", file_name

