# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

import zerorpc
from django.db import close_old_connections


class RPC(object):
    @classmethod
    def register(cls, name=None, stream=False):
        def _wrapper(func):
            if stream:
                s = zerorpc.stream(lambda self, *args, **kwargs: func(*args, **kwargs))
            else:
                s = staticmethod(func)

            setattr(cls, name or func.__name__, s)
            return func

        return _wrapper


class ServerExecMiddleware(object):
    def server_before_exec(self, request_event):
        close_old_connections()

    def server_after_exec(self, request_event, reply_event):
        close_old_connections()


rpc = RPC()


