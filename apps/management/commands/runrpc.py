# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

import zerorpc
from utils.zrpc import rpc, ServerExecMiddleware
from django.core.management.base import BaseCommand
from website.settings import tcp_port
import importlib


class Command(BaseCommand):

    help = 'set your rpc params'

    def handle(self, *args, **options):
        importlib.import_module("apps.rpcs")
        server = zerorpc.Server(rpc, heartbeat=30)
        server.bind("tcp://0.0.0.0:{}".format(tcp_port))
        zerorpc.Context.get_instance().register_middleware(ServerExecMiddleware())
        server.run()

    def add_arguments(self, parser):
        pass


