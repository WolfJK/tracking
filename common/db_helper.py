# coding: utf-8
# __author__: "Rich"
from __future__ import unicode_literals
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections
from common.logger import Logger
from redis_helper import REDIS
from datetime import datetime
from hashlib import sha256
import json
import time
import re
from django.conf import settings

logger = Logger.getLoggerInstance()


def encode(obj, encoding="utf8"):
    if isinstance(obj, unicode):
        obj = obj.encode(encoding)
    return obj


def set_cache(sql, args, data):
    key = sha256(encode(sql + json.dumps(args))).hexdigest()
    expired_time = "{0} 23:59:59".format(datetime.now().strftime("%Y-%m-%d"))
    expired_timestamp = time.mktime(time.strptime(expired_time, "%Y-%m-%d %H:%M:%S"))
    expire = int(expired_timestamp - time.time())
    value = json.dumps(data, cls=DjangoJSONEncoder)
    REDIS.set(key, value, expire)


def get_cache(sql, args):
    key = sha256(encode(sql + json.dumps(args))).hexdigest()
    return REDIS.get(key)


class DB(object):
    @classmethod
    def convert(cls, sql, dargs=None):
        """
        为防止sql注入, 将sql参数化转义成%s

        :param sql: 参数化sql, 如select * from table where a={a} and b={b}
        :param dargs: sql参数, 如{a: 1, b: 2}

        :returns
            sql: 转义后的sql, 如select * from table where a=%s and b=%s
            args: 转义后的参数, 如[1, 2]
        """
        args = []
        debug_sql = sql
        for _ in re.findall('{[^}]+}', sql):
            key = _.replace('{', '').replace('}', '')
            if isinstance(dargs[key], list):
                sql = sql.replace(_, ','.join(['%s' for i in dargs[key]]))
                debug_sql = debug_sql.replace(_, ','.join(["'{0}'".format(i) for i in dargs[key]]))
                args += dargs[key]
            else:
                args.append(dargs[key])
                sql = sql.replace(_, '%s')
                debug_sql = debug_sql.replace(_, "'{0}'".format(dargs[key]))

        logger.debug(debug_sql)

        return sql, args, debug_sql

    @classmethod
    def search(cls, sql, dargs=None, connection_name='default', use_catched=None):
        if use_catched is None:
            use_catched = settings.USE_CATCHED

        try:
            dbs = connections[connection_name]
            with dbs.cursor() as cursor:
                sql, args, debug_sql = cls.convert(sql, dargs)
                if use_catched:
                    results = get_cache(sql, args)
                    if results:
                        return results

                cursor.execute(sql, args)
                columns = [_[0].lower() for _ in cursor.description]
                results = [dict(zip(columns, _)) for _ in cursor]
                if use_catched:
                    set_cache(sql, args, results)
                return results
        except Exception as e:
            pass
        finally:
            dbs.close()

    @classmethod
    def get(cls, sql, dargs=None, connection_name='default', use_catched=None):
        if use_catched is None:
            use_catched = settings.USE_CATCHED

        results = cls.search(sql, dargs, connection_name, use_catched)
        return results[0] if len(results) else None

    @classmethod
    def total(cls, sql, dargs=None, connection_name='default'):
        try:
            dbs = connections[connection_name]
            with dbs.cursor() as cursor:
                sql, args, debug_sql = cls.convert(sql, dargs)
                cursor.execute(sql, args)
                columns = [_[0].lower() for _ in cursor.description]
                results = [dict(zip(columns, _)) for _ in cursor]
                return results[0][columns[0]]
        except Exception as e:
            pass
        finally:
            dbs.close()

    @classmethod
    def execute(cls, sql, dargs=None, connection_name='default'):
        try:
            dbs = connections[connection_name]
            with dbs.cursor() as cursor:
                sql, args, debug_sql = cls.convert(sql, dargs)
                cursor.execute(sql, args)
                dbs.commit()
        except Exception as e:
            pass
        finally:
            dbs.close()
