# coding: utf-8
# __author__: ""
from __future__ import unicode_literals
import json
import re
import socket
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_parameter(request_data, parameters):
    '''
    简单获取 请求参数
    :param request_data: request_data.GET
    :param parameters:  例如 ('brand_id', '请输入brand_id')
    :return:
    '''
    param = dict()
    for parameter in parameters:
        default = dict(dict={}, list=[], str='', int=0)
        parameter_value = request_data.get(parameter[0], default[parameter[2]])

        if parameter_value and parameter[2] in ('list', 'dict') and not isinstance(parameter_value, (list, dict)):
            parameter_value = json.loads(parameter_value)

        if not parameter_value and parameter[1]:
            raise Exception(parameter[1])

        if not parameter_value:
            parameter_value = default[parameter[2]]

        # 如果是 list 类型
        if parameter[2] == 'int':
            parameter_value = int(parameter_value)

        param.update({parameter[0]: parameter_value})

    return param


def get_ip(request):
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
    '''
    str 转为 date
    :param dts:
    :param ft:
    :return:
    '''
    return datetime.strptime(dts, ft)


def date2str(dt, ft="%Y-%m-%d"):
    '''
    str 转为 date
    :param dt:
    :param ft:
    :return:
    '''
    return dt.strftime(ft)


def set_precision(data, keys, precision=2, pct=1.0):
    '''
    设置 list<map> or map
    :param data: lsit<map>
    :param keys: 处理的 keys
    :param precision: 精度
    :param pct: 是否是百分比, 1 不是, 100 是
    :return:
    '''
    if isinstance(data, dict):
        data = [data]

    for d in data:
        map(lambda k: d.update({k: round(d[k] * pct, precision)}), keys)


def trend_type(begin, end):
    '''
    过去数据趋势的时间类型: week  or day
    :return:
    '''
    if (str2date(end) - str2date(begin)) + 1 > 30:
        return "week"
    else:
        return "day"


def begin_date(begin, d_type):
    '''
    将 begin 时间 向前推一年
    :param begin:
    :param d_type:
    :return:
    '''
    begin = str2date(begin)

    if d_type == "week":
        begin = begin - relativedelta(days=begin.weekday(), weeks=52)
    elif d_type == "month":
        begin = begin - relativedelta(days=begin.day - 1, months=12)
    else:
        begin = begin - relativedelta(years=1)

    return date2str(begin)


def division_ratio(a, b, precision=2):
    '''
    两个数的除法
    :param a:
    :param b:
    :param precision: 精度
    :return:
    '''
    if not b:
        return 0.00

    return round(float(a) * 100.0 / float(b), precision)


def ratio(data, column, precision=2):
    '''
    求 一个字断的 占比
    :param data:
    :param column:
    :param precision:
    :return:
    '''
    sum_data = sum([_[column] for _ in data])

    for _ in data:
        _[column + "_ratio"] = division_ratio(_[column], sum_data, precision)

    return data


def next_period(date):
    '''
    获取 日期的下一个周期
    :param date:
    :return:
    '''
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


