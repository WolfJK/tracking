# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.core.serializers.json import DjangoJSONEncoder
import json
import traceback
from utils.zrpc import rpc
from common.logger import Logger
from common.models import Report


logger = Logger.getLoggerInstance()

@rpc.register()
def update_report(report_id, status):
    try:
        print(report_id)
        report = Report.objects.get(id=report_id)
        report.status = status
        report.save()
    except:
        logger.error(traceback.format_exc())
        return "报告不存在"

    return 1


@rpc.register()
def get_report(status=0):
    try:
        reports = list(Report.objects.filter(status=status, delete=False).values(
            "id", "name", "tag", "monitor_start_date", "monitor_end_date",
            "platform", "accounts", "sales_point",
        ))

    except:
        logger.error(traceback.format_exc())
        return 0

    return json.dumps(reports, cls=DjangoJSONEncoder)


