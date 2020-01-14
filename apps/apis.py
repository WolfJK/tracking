# coding: utf-8
# __author__: ""
from __future__ import unicode_literals
import json
import re
import socket
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_parameter(request_data, parameters):
    """
    简单获取 请求参数
    :param request_data: request_data.GET
    :param parameters:  例如 ('brand_id', '请输入brand_id')
    :return:
    """
    param = dict()
    hooks = []
    for parameter in parameters:
        default = dict(dict={}, list=[], str='', int=0, bool=False)
        parameter_value = request_data.get(parameter[0], default[parameter[2]])
        # 处理 json、dict 格式数据, '[]', '{}' 也视为有数据, 但是参数为 false
        try:
            if parameter_value and parameter[2] in ('list', 'dict') and not isinstance(parameter_value, (list, dict)):
                parameter_value = json.loads(parameter_value)
        except:
            raise Exception("参数类型错误")

        # 如果为必须参数,但是未传入,则抛出异常【必须在 json 处理之后】
        if not parameter_value and parameter[1]:
            raise Exception(parameter[1])
        # 获取 默认参数
        if not parameter_value:
            parameter_value = default[parameter[2]]

        # int、bool 型参数进行格式转化
        try:
            # 如果是 list 类型
            if parameter[2] == 'int':
                parameter_value = int(parameter_value)

            if parameter[2] == 'bool':
                parameter_value = bool(int(parameter_value))
        except:
            raise Exception("参数类型错误")

        # 添加 钩子 函数, 进行参数验证处理
        if len(parameter) > 3 and parameter[3]:
            hooks.append(parameter[3])

        param.update({parameter[0]: parameter_value})

    # 进行额外的验证处理
    map(lambda hook: hook(param), hooks)
    return param


def get_ip(request):
    """
    取货 访问 ip
    :param request:
    :return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def del_key_in_ld(data, keys):
    """
    删除 字典中的 keys
    :param data: [dict(aa=1,bb=2,cc=3)]
    :param keys: ["aa"]
    :return:
    """
    for _ in data:
        map(lambda x: _.pop(x), keys)

    return data


def domains_2_ips(domains):
    """
    将域名转换为 ip
    :param domains: 域名列表 []
    :return:
    """
    def domain_2_ip(domain):
        if re.search("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", domain):
            return domain

        try:
            ip = socket.getaddrinfo(domain, None)[0][4][0]
            return ip

        except:
            return None

    return filter(lambda _: _, map(lambda x: domain_2_ip(x), domains))


def str2date(dts, ft="%Y-%m-%d"):
    """
    str 转为 date
    :param dts:
    :param ft:
    :return:
    """
    return datetime.strptime(dts, ft)


def date2str(dt, ft="%Y-%m-%d"):
    """
    str 转为 date
    :param dt:
    :param ft:
    :return:
    """
    return dt.strftime(ft)


def date_after(d1, **params):
    """
    获取一个 日期 之后 都少 天的 日期
    :param d1:
    :param params:
    :return:
    """
    if not d1:
        d1 = datetime.now()

    return d1 + relativedelta(**params)


def set_precision(data, keys, precision=2, pct=1.0):
    """
    设置 list<map> or map
    :param data: lsit<map>
    :param keys: 处理的 keys
    :param precision: 精度
    :param pct: 是否是百分比, 1 不是, 100 是
    :return:
    """
    if isinstance(data, dict):
        data = [data]

    for d in data:
        map(lambda k: d.update({k: round(d[k] * pct, precision)}), keys)


def trend_type(begin, end):
    """
    过去数据趋势的时间类型: week  or day
    :return:
    """
    if (str2date(end) - str2date(begin)) + 1 > 30:
        return "week"
    else:
        return "day"


def begin_date(begin, d_type):
    """
    将 begin 时间 向前推一年
    :param begin:
    :param d_type:
    :return:
    """
    begin = str2date(begin)

    if d_type == "week":
        begin = begin - relativedelta(days=begin.weekday(), weeks=52)
    elif d_type == "month":
        begin = begin - relativedelta(days=begin.day - 1, months=12)
    else:
        begin = begin - relativedelta(years=1)

    return date2str(begin)


def division_ratio(a, b, precision=2):
    """
    两个数的除法
    :param a:
    :param b:
    :param precision: 精度
    :return:
    """
    if not b:
        return 0.00

    return round(float(a) * 100.0 / float(b), precision)


def ratio(data, column, precision=2):
    """
    求 一个字断的 占比
    :param data:
    :param column:
    :param precision:
    :return:
    """
    sum_data = sum([_[column] for _ in data])

    for _ in data:
        _[column + "_ratio"] = division_ratio(_[column], sum_data, precision)

    return data


def next_period(date):
    """
    获取 日期的下一个周期
    :param date:
    :return:
    """
    if len(date) == 10:
        date = str2date(date) + relativedelta(days=1)
        return date2str(date)

    elif len(date) > 10:
        date = date.split("~")
        begin = str2date(date[0]) + relativedelta(weeks=1)
        end = str2date(date[1]) + relativedelta(weeks=1)
        return "~".join((date2str(begin), date2str(end)))

    elif len(date) == 7:
        date = str2date(date + "-01") + relativedelta(months=1)
        return date2str(date, "%Y-%m")

    else:
        raise Exception("数据计算结果有误")


def combine_list_map(lm1, lm2, key, default):
    """
    以 lm1 为基数合并 lm2
    :param lm1:
    :param lm2:
    :param key:
    :param default:
    :return:
    """
    lm2_map = {lm[key]: lm for lm in lm2}
    map(lambda lm: lm.update(lm2_map.get(lm[key], default)), lm1)
    return lm1


def brand_to_name(brands):
    """
    将 [id_name, id_name, id_name] 转化为 name.name.name
    :param brands:
    :return:
    """
    return ".".join([brand.split("_")[1] for brand in brands])


def brand_to_brand(params):
    """
    将 [id_name, id_name, id_name] 转化为 name.name.name
    将 [id_name-id_name, id_name-id_name-id_name, id_name] 转化为 [name.name, name.name.name, name]
    :param params:
    :return:
    """
    if params.has_key("brand"):
        params.update(brand=brand_to_name(params["brand"]))

    if params.has_key("competitor"):
        params.update(competitor=[brand_to_name(competitor.split("-")) for competitor in params["competitor"]])

    return params


def month_to_day(params):
    """
    将 参数 为 月的开始时间 结束时间, 转换为 日的格式
    :param params: {"start_date": "2019-10", "end_date": "2019-12"}
    :return: {"start_date": "2019-10-01", "end_date": "2019-12-31"}
    """
    params.update(start_date=params["start_date"][:7] + "-01", end_date=last_day_of_month(params["end_date"]),)

    return params


def last_day_of_month(date):
    """
    求 一个 日期 所在月的最后一弹
    :param date: 日期, eg: 2019-10-12
    :return:
    """
    last_day = str2date(date[:7] + "-01") + relativedelta(months=1, days=-1)

    return date2str(last_day)



