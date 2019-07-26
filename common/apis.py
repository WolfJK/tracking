# coding: utf-8
# __author__: "Rich"
from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

def days_daterange(start_date, end_date):
    """
    获取当时段间隔天数
    :param start_date: 开始时间, 字符串
    :param end_date: 结束时间, 字符串
    :return: 间隔天数
    """
    start_date, end_date = str2date(start_date), str2date(end_date)

    if end_date < start_date:
        raise Exception("结束时间必须大于开始时间")

    days = (end_date - start_date).days
    return days


def week_daterange():
    """
    获取当前时间的自然周时间段, 因数据是T+1,所以需要减1天
    :return: 本周开始时间, 本周结束时间
    """
    now = datetime.now() - relativedelta(days=1)
    week_start_date = now - relativedelta(days=now.weekday())
    week_end_date = now + relativedelta(days=6 - now.weekday())

    return date2str(week_start_date), date2str(week_end_date)


def ring_daterange(start_date, end_date):
    """
    获取环比时间段
    :param start_date: 开始时间, 字符串
    :param end_date: 结束时间, 字符串
    :return: 环比开始时间, 环比结束时间
    """
    start_date, end_date = str2date(start_date), str2date(end_date)

    if end_date < start_date:
        raise Exception("结束时间必须大于开始时间")

    days = (end_date - start_date).days + 1

    ring_end_date = start_date - relativedelta(days=1)
    ring_start_date = start_date - relativedelta(days=days)

    return date2str(ring_start_date), date2str(ring_end_date)


def year_daterange(start_date, end_date):
    """"
    获取同比时间段
    :param start_date: 开始日期, str, %Y-%m-%d
    :param end_date: 结束日期, str, %Y-%m-%d
    :return: 同比起始日期，同比结束日期
    """
    start_date, end_date = str2date(start_date), str2date(end_date)

    if end_date < start_date:
        raise Exception("结束时间必须大于开始时间")

    year_start_date = start_date - relativedelta(years=1)
    year_end_date = end_date - relativedelta(years=1)
    return date2str(year_start_date), date2str(year_end_date)


def pagination(rows, page_number=1, page_size=10):
    """
    分页器
    :param rows :QuerySet: Model.objects.filter().values()
    :param page_number :int: 第几页, 默认为1
    :param page_size :int: 一页的记录数, 默认为10
    :return (single_page:list, total_item_count:int):
    """
    if not page_number:
        page_number = 1
    if not page_size:
        page_size = 10
    paginator = Paginator(rows, page_size)
    return list(paginator.page(page_number).object_list), paginator.count


def get_default_start_end_date():
    """
    获取默认的起始和结束日期
    :return (start_date:str, end_date:str):
    """
    today = datetime.now()
    end_date = today.strftime(DATE_FORMAT)
    start_date = (today + relativedelta(today, months=-3)).strftime(DATE_FORMAT)
    return start_date, end_date


def get_recent7days_start_end_date():
    """
    获取最近7天的起始和结束时间，结束时间是当天，起始时间为 T-6
    :return:
    """
    end_date = datetime.now()
    start_date = end_date - relativedelta(end_date, days=6)
    return date2str(start_date), date2str(end_date)


def date2str(date_object, str_format=DATE_FORMAT):
    """
    datetime object 转换成 str object
    :param date_object:
    :param str_format:
    :return:
    """
    if isinstance(date_object, datetime):
        date_object = date_object.strftime(str_format)
    return date_object


def str2date(str_object, str_format=DATE_FORMAT):
    """
    str object 转换成 datetime object
    :param str_object:
    :param str_format:
    :return:
    """
    if isinstance(str_object, basestring):
        str_object = datetime.strptime(str_object, str_format)
    return str_object


def datetime_range(start_date, end_date=None):
    """
    由于 ORM 没有对应数据 DATE 的函数，所以要查某一天的数据会比较麻烦，这里采用range方法
    create_time__range=('2019-01-01', '2019-01-02')
    注：这里因为是在 DateTime 类型的字段用 Date 类型的数据进行查询才需要转换
    仅传递 start_date 是查询特定某天的数据，同时传递 start_date 和 end_date 才是范围时间
    :param start_date:
    :param end_date:
    :return:
    """
    start_date, end_date = str2date(start_date), str2date(end_date)
    if not end_date:
        end_date = start_date + relativedelta(days=1)
    else:
        end_date += relativedelta(days=1)
    return date2str(start_date), date2str(end_date)


def daterange_beyond3month_check(start_date, end_date):
    """
    根据起始时间和结束时间判断是否在3个月内
    :param start_date: %Y-%m-%d str:
    :param end_date: %Y-%m-%d str:
    :return:
    """
    if start_date > end_date:
        raise Exception("起始日期必须小于等于结束日期")

    start_date, end_date = str2date(start_date), str2date(end_date)
    if start_date < end_date - relativedelta(days=90):
        raise Exception("时间范围超过了3个月，最大可查询时间范围为3个月")
