# coding: utf-8
# __author__: ""
from __future__ import unicode_literals
import json


def get_parameter(request_data, parameters):
    '''
    简单获取 请求参数
    :param request_data: request_data.GET
    :param parameters:  例如 ('brand_id', '请输入brand_id')
    :return:
    '''
    param = dict()
    for parameter in parameters:
        default = dict(dict={}, list=[], str=None, int=0)
        parameter_value = request_data.get(parameter[0], default[parameter[2]])

        if not parameter_value and parameter[1]:
            raise Exception(parameter[1])

        if not parameter_value:
            parameter_value = default[parameter[2]]

        # 如果是 list 类型
        if parameter[2] in ('list', 'dict') and not isinstance(parameter_value, (list, dict)):
            parameter_value = json.loads(parameter_value)
        elif parameter[2] == 'int':
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

