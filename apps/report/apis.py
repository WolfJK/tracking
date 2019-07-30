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


def report_details(report_id):
    """
    生成报告详情
    聚合结果为0时，是不出现在数据里的，需要后端补全, 也可能出现长度为0的列表
    :param report_id:
    :return:
    """
    data = dict(
        # 1. 传播实况
        spread_overview=dict(
            # 1.1. 投放声量总计
            post_count=124,

            # 1.2. 投放账号数总计
            account_count=33,

            # 1.3. 投放声量分布
            activity=[
                # 报告内所有子活动的投放声量
                dict(name="抗敏大挑战", value=48),
                dict(name="get过敏小知识", value=41),
                dict(name="换季过敏", value=35)
            ],

            # 1.4. 投放渠道分布
            platform=dict(
                # 微博投放声量数
                weibo=120,

                # 母垂投放声量数
                motherbaby=[

                    # 母锤投放具体到各个平台
                    dict(name="宝宝树", value=3),
                    dict(name="辣妈帮", value=1)
                ]
            ),

            # 1.5. 投放账号分布
            account=[
                # 账号、所属平台、账号投放声量总计
                dict(account="张三", platform="微博", post_count=33),
                dict(account="Edward", platform="宝宝树", post_count=2),
                dict(account="李四", platform="辣妈帮", post_count=1),
            ],

            # 1.6. 投放声量趋势及账号趋势
            trend=[
                # 由于count可以直接相加，所以数据格式固定是按天给，如果要转换成按周，需要再次聚合
                dict(date="2019-01-01", post_count=55, account_count=12),
                dict(date="2019-01-02", post_count=51, account_count=9),
                dict(date="2019-01-03", post_count=59, account_count=13),
                dict(date="2019-01-04", post_count=45, account_count=6)
            ]
        ),

        # 2. 活动传播效率
        spread_efficiency=dict(
            # 2.1. 平台效率 - 累计传播效率
            platform_cumulative=[
                # 分别表示 累计传播广度, 累计互动量, 平台, 投放声量
                dict(breadth=10, interaction=50, name="微博", value=100),
                dict(breadth=30, interaction=20, name="宝宝树", value=10)
            ],

            # 2.2. 平台效率 - 单位传播效率
            platform_average=[
                # 分别表示 单位传播广度, 单位互动量, 平台, 投放声量
                dict(breadth=10, interaction=50, name="微博", value=100),
                dict(breadth=30, interaction=20, name="宝宝树", value=10)
            ],

            # 2.3. 账号效率 - 单位传播效率
            account_cumulative=[
                # 分别表示 累计传播广度, 累计互动量, 账号, 平台, 投放声量
                dict(breadth=5, interaction=18, name="张三", platform="微博", value=100),
                dict(breadth=30, interaction=20, name="王五", platform="宝宝树", value=10)
            ],

            # 2.4. 账号效率 - 单位传播效率
            account_average=[
                # 分别表示 单位传播广度, 单位互动量, 账号, 平台, 投放声量
                dict(breadth=5, interaction=18, name="张三", platform="微博", value=100),
                dict(breadth=30, interaction=20, name="王五", platform="宝宝树", value=10)
            ],

            # 2.5. 子活动效率 - 单位传播效率
            activity_cumulative=[
                # 分别表示 累计传播广度, 累计互动量, 账号, 子活动, 投放声量
                dict(breadth=50, interaction=33, name="张三", platform="微博", value=100),
                dict(breadth=30, interaction=99, name="王五", platform="宝宝树", value=10)
            ],

            # 2.6. 子活动效率 - 单位传播效率
            activity_average=[
                # 分别表示 单位传播广度, 单位互动量, 账号, 子活动, 投放声量
                dict(breadth=5, interaction=33, name="张三", platform="微博", value=100),
                dict(breadth=30, interaction=99, name="王五", platform="宝宝树", value=10)
            ],

            # 2.7. 互动量来源
            activity_composition=[
                dict(name="转发", value=60),
                dict(name="评论", value=21),
                dict(name="点赞", value=43)
            ],

            # 2.8. 评论账号分布
            user_type_composition=[
                dict(name="BGC", value=20),
                dict(name="KOL", value=7),
                dict(name="水军", value=14),
            ]
        ),

        # 3. 传播效率排行
        spread_efficiency_rank=dict(
            # 3.1. 文章
            article=[
                # 分别是 文本内容, 来源平台, 转发数, 评论数, 点赞数, 如果该平台没有相应的字段，值为None
                dict(content="文章1", platform="微博", transmit_count=1, reply_count=2, like_count=3),
                dict(content="文章2", platform="宝宝树", transmit_count=None, reply_count=2, like_count=None),
            ],

            # 3.2. KOL
            kol=[
                # 分别是 KOL用户名, 来源平台, 发帖数, 贴均互动量, 贴均传播广度
                dict(nick_name="用户1", platform="微博", post_count=1, interaction_per_post=412.3, breadth_per_post=11.1),
                dict(nick_name="用户2", platform="宝宝树", post_count=1, interaction_per_post=412.3, breadth_per_post=11.1),
            ]
        ),

        # 4. 传播效果
        spread_effectiveness=dict(
            # 4.1. 活动期间UGC总计
            ugc_count=200,

            # 4.2. 活动UGC
            ugc_in_activity_count=135,

            # 4.3. 品牌UGC
            ugc_mentioned_brand_count=136,

            # 4.4. 活动UGC构成
            ugc_in_activity_composition=[
                dict(name="提及品牌", value=120),
                dict(name="未提及品牌", value=15)
            ],

            # 4.5. 子活动UGC构成
            activity_ugc_in_activity_composition=[
                # 图中一根柱子里的数据由两行数据表示
                dict(name="敏事大挑战", value=30, type="提及品牌"),
                dict(name="敏事大挑战", value=70, type="未提及品牌"),
            ]
        ),

        # 5. 品牌关注度
        brand_concern=dict(
            # 5.1. 浮动
            delta=0.1,

            # 5.2. 活动期实际品牌关注度
            activity=0.15,

            # 5.3. 年度品牌关注度
            annual=0.05,

            # 5.4. 年度趋势图
            trend=[
                # 年度品牌关注度是常量，可以将annual填入，一周一行数据
                dict(value=20, date="2019-01-07"),
                dict(value=30, date="2019-01-14")
            ]
        ),

        # 6. 宣传卖点认知度
        tags_concern=dict(
            # 6.1. 浮动
            delta=0.1,

            # 6.2. 活动期"过敏"认识度
            activity=0.15,

            # 6.3. 年度"过敏"认识度
            annual=0.05,

            # 6.4. 年度趋势图
            trend=[
                # 年度品牌关注度是常量，可以将annual填入，一周一行数据
                dict(value=20, date="2019-01-07"),
                dict(value=30, date="2019-01-14")
            ]
        )
    )
    return data


def report_config_create(param, user):
    """
    生成报告
    :param param: 报告参数
    :param user: 当前用户
    :return:
    """
    param.update(user=user)
    Report(param).save()


def delete_report(user, report_id):
    # 删除报告 公司管理员可以删除公司的所有报告， 普通用户只能删除自己的报告
    report_id = int(report_id)
    error_message = "报告未生成,不允许删除"
    if user.is_admin:
        corporation = user.corporation
        report_list = Report.objects.filter(user__corporation=corporation, status=0).values_list("id", flat=True)
        if report_id in report_list:
            Report.objects.get(id=report_id).delete()
        else:
            raise Exception(error_message)
    else:
        report_list = Report.objects.filter(user_id=user.id, status=0).values_list("id", flat=True)
        if report_id in report_list:
            Report.objects.get(id=report_id).delete()
        else:
            raise Exception(error_message)


def cancel_report(user, report_id):
    error_message = "报告已经被受理,不允许取消"
    try:
        report = Report.objects.get(id=report_id)
    except Exception:
        raise Exception("报告不存在")

    if user.is_admin:
        if report.status == 1 and report.user.corporation == user.corporation:
            report.status = 5
            report.save()
        else:
            raise Exception(error_message)
    else:
        if report.status == 1 and report.user.id == user.id:
            report.status = 5
            report.save()
        else:
            raise Exception(error_message)
