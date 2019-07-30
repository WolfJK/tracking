# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from itertools import chain
from operator import itemgetter
from common.db_helper import DB
from django.db.models import Q
from common.models import *
from datetime import datetime
from django.db.models import F, Q, Func
from common.db_helper import DB

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
    values = ("monitor_start_date", "monitor_end_date", "create_time", "username", "status")
    db = DB()
    sql = "select * from report "
    if report_status or monitor_end_time or monitor_cycle or key_word:
        sql = "select * from report where {}"
    if report_status:
        sql_format.append("{}={}".format("status", report_status))
    if monitor_end_time:
        if monitor_end_time == "1":
            sql_format.append("datediff('{}', {})<{}".format(datetime.now(), "monitor_end_date", 30))
        elif monitor_end_time == "2":
            sql_format.append("datediff('{}', {})<{}".format(datetime.now(), "monitor_end_date", 90))
        elif monitor_end_time == "3":
            sql_format.append("datediff('{}', {})<{}".format(datetime.now(), "monitor_end_date", 120))
        elif monitor_end_time == "4":
            sql_format.append("datediff('{}', {})>{}".format(datetime.now(), "monitor_end_date", 120))

    if monitor_cycle:
        if monitor_cycle == "1":
            sql_format.append("datediff({}, {})<{}".format("monitor_end_date", "monitor_start_date", 15))
        if monitor_cycle == "2":
            sql_format.append("datediff({}, {})<{}".format("monitor_end_date", "monitor_start_date", 30))

    if key_word:
        name = key_word.lower()
        user_list = SmUser.objects.annotate(name=Func(F("username"), function="LOWER"),
                                            ).filter(Q(name__contains=name)).values_list("id", flat=True)
        str_user_list = "".join([str(i) for i in user_list])

        sql_title = "{} like '%{}%'".format("name", key_word)
        if user_list:
            sql_name = "{} in ({})".format("user_id", str_user_list)
            sql_format.append(sql_title + "or" + sql_name)
        else:
            sql_format.append(sql_title)

    # 判断是管理员内部用户
    if user.is_admin and user.user_type == 1:
        sql_format = " and ".join(sql_format)
        sql = sql.format(sql_format)
    elif user.is_admin:
        corporation = user.corporation
        sql_user = "{}={}".format("corporation", corporation)
        sql_format.append(sql_user)
        sql_format = " and ".join(sql_format)
        sql = sql.format(sql_format)
    else:
        user_id = user.id
        sql_user = "{}={}".format("user_id", user_id)
        sql_format.append(sql_user)
        sql_format = " and ".join(sql_format)
        sql = sql.format(sql_format)
    res = db.search(sql)
    return res


def get_common_info():

    return report_affilication, report_status, report_monitor_end_time, monitor_cycle