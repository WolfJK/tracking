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
from StringIO import StringIO
from io import BytesIO
from dateutil.relativedelta import relativedelta
import pandas
from compiler import ast
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

            # 1.4. 投放渠道分布
            platform1=[
                dict(
                    name="微博",
                    value=120,
                    children=[dict(name="weibo", value=120)]
                ),
                dict(
                    name="母垂",
                    value=24,
                    children=[
                        dict(name="宝宝树", value=12),
                        dict(name="辣妈帮", value=12),
                    ]
                ),

            ],

            # 1.5. 投放账号分布
            account=[
                # 账号、所属平台、账号投放声量总计
                dict(account="张三", platform="微博", post_count=33, user_type="BGC"),
                dict(account="Edward", platform="宝宝树", post_count=2, user_type="KOL"),
                dict(account="李四", platform="辣妈帮", post_count=1, user_type="水军"),
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

            # 4.2 - 4.3 补充 活动UGC & 品牌UGC
            ugc_intersect_count=35,

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
            ],

            # 4.6 活动对品牌UGC的贡献
            # 4.6.1 活动期预测UGC
            predict=232,

            # 4.6.2 浮动绝对值
            delta_absolute=-97,

            # 4.6.3 浮动比例
            delta=-0.42,

            # 4.6.4 年均品牌UGC
            annual_average_trend=[
                dict(value=20, date="2019-01-07"),
                dict(value=30, date="2019-01-14")
            ],
            # 4.6.5 实际品牌UGC
            brand_ugc_trend=[
                dict(value=20, date="2019-01-07"),
                dict(value=30, date="2019-01-14")
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

            # 5.4. 趋势图
            trend=[
                dict(value=20, date="2019-01-07"),
                dict(value=30, date="2019-01-14")
            ],
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


def get_unscramble(data):
    '''
    根据数据 获取解读结果
    :param data:
    :return:
    '''
    activity_max = max(data["spread_overview"]["activity"], key=lambda x: x["value"])
    platform_max = max(ast.flatten([x["children"] for x in data["spread_overview"]["platform"]]), key=lambda x: x["value"])
    platform_post_sum = sum([v["value"] for v in ast.flatten([x["children"] for x in data["spread_overview"]["platform"]])])


    param = dict(
        post_count=data["spread_overview"]["post_count"],
        account_all=data["spread_overview"]["account_count"],
        activity_count=len(data["spread_overview"]["activity"]),
        activity_max=activity_max["name"],
        activity_post_count=activity_max["value"],
        platform_max=platform_max["name"],
        platform_post_count=platform_max["value"],
        platform_max_ratio=float(platform_max["value"] * 100.0 / platform_post_sum, 2),
        account_max=float(platform_max["value"] * 100.0 / platform_post_sum, 2),
    )



unscramble_rule = dict(
    transmission=[
        ("1", "1, 本次活动共投放{post_count}篇帖子，启用{account_all}个账号。\n 2, "),
        ("{activity_count} > 1", "{activity_max}主题活动投放声量最高（{activity_post_count}篇）；"),
        ("1", "活动主要在{platform_max}平台投放，共投放{platform_post_count}篇帖子，约占总投放声量的{platform_max_ratio}%。\n"),
        ("{account_max} == {post_max}", "3, 从账号分布来看，{account_max}账号数量最多（{account_count}个），发布的帖子数也最多（{account_post_count}篇）\n"),
        ("{account_max} != {post_max}", "3, 从账号分布来看，{account_max}账号数量最多（{account_count}个），而{account_post_max}账号发布帖子数最多（{account_post_count}篇）\n"),

    ],
    efficiency=[
        ("{platform_count} > 1 and {cb_platform_max} != {hd_platform_max}", "从平台角度看，本次活动在{cb_platform_max}的累计传播广度最高（{cb_platform_count}人次），而在{hd_platform_max}引发了最高的累计互动量（{hd_platform_count}人次）\n"),
        ("{platform_count} > 1 and {cb_platform_max} == {hd_platform_max}", "从平台角度看，本次活动在{cb_platform_max}引发了最高的累计互动量（{hd_platform_count}人次）和最高的累计传播广度（{cb_platform_count}人次）\n"),
        ("{platform_count} == 1", "本次活动累计互动量{hd_platform_count}人次，累计传播广度{cb_platform_max}人次 \n"),
        ("{hd_account_max} != {cb_account_max}", "从账号角度看，{cb_account_max}的发帖累计传播广度最高（{cb_account_count}人次），而{hd_account_max}的发帖引发了最高的累计互动量（{hd_account_count}人次） \n"),
        ("{hd_account_max} == {cb_account_max}", "从账号角度看，{cb_account_max}的发帖累计传播广度最高（{cb_account_count}人次），且引发了最高的累计互动量（{hd_account_count}人次）\n"),

        ("{hd_activity_max} != {cb_activity_max}", "从子活动角度看，“{cb_activity_max}”累计传播广度最高（{cb_activity_count}人次），而“{hd_activity_max}”引发了最高的累计互动量（{hd_activity_count}人次）\n"),
        ("{hd_activity_max} == {cb_activity_max}", "从子活动角度看，“{cb_activity_max}”累计传播广度最高（{cb_activity_count}人次），且引发了最高的累计互动量（{hd_activity_count}人次）\n"),

        ("1", "互动大部分来源于{source}，约占整体的{source_ratio}%；评论中{account_comment}账号的占比最高，约为{account_comment_ratio}%。\n"),
    ],
    effect_ugc=[
        ("{activity_count} > 1", "本次活动期间UGC总计{ugc_count}人，其中活动UGC{activity_ugc_count}人，品牌UGC{brand_ugc_count}人。\n"),
        ("1", "活动UGC中有{activity_brand_ugc_count}人（{activity_brand_ugc_ratio}%）提及品牌名称，增加了品牌声量；以#{activity_ugc_max}# 为主题的子活动引发的UGC人数最多，达{activity_ugc_count}个。\n"),
        ("{activity_contribution} > {activity_contribution_pre}", "活动期内总计产生品牌UGC{brand_ugc_count}人。基于过往一年历史数据的预测，活动期内品牌UGC应该可以达到{brand_ugc_pre_count}，相差{brand_ugc_diff_count}人（-{brand_ugc_diff_ratio}%），没有达到预期效果\n"),
        ("{activity_contribution} < {activity_contribution_pre}", "活动期内总计产生品牌UGC{brand_ugc_count}人。基于过往一年历史数据的预测，活动期内品牌UGC可以达到{brand_ugc_pre_count}人，活动为品牌贡献了{brand_ugc_diff_count}个（{brand_ugc_diff_ratio}%）UGC，超出预期效果\n"),
    ],
    effect_brand=[
        ("{brand_attention} > {brand_attention_year}", "活动期间内品牌关注度达{brand_attention}%，较年度关注度提升{brand_attention_ratio}%。\n"),
        ("{brand_attention} < {brand_attention_year}", "活动期间内品牌关注度达{brand_attention}%，较年度关注度下降{brand_attention_ratio}%。\n"),
    ],
    effect_sales_point=[
        ("{sales_point_cognitive} > {sales_point_cognitive_year}", "活动期内用户对于宣传卖点——“{sales_point}”的认知度为{sales_point_cognitive}%，较年度“{sales_point}”认知度提升{sales_point_cognitive_ratio}%\n"),
        ("{sales_point_cognitive} < {sales_point_cognitive_year}", "活动期内用户对于宣传卖点——“{sales_point}”的认知度为{sales_point_cognitive}%，较年度“{sales_point}”认知度下降{sales_point_cognitive_ratio}%\n"),
    ],
)


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
