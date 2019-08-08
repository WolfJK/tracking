# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

from django.core.serializers.json import DjangoJSONEncoder
import json
import traceback
from utils.zrpc import rpc
from common.logger import Logger
from common.models import Report, ReportStatus


logger = Logger.getLoggerInstance()


@rpc.register()
def update_report(report_id, status):
    try:
        print(report_id)
        report = Report.objects.get(id=report_id)
        report.status = status
        report.save()

        ReportStatus(report=report, status=status).save()
    except:
        logger.error(traceback.format_exc() + "\r\n"
                     + "[update_report request data]  report_id={0}, status={1}".format(report_id, status))
        return "报告不存在"

    return 1


@rpc.register()
def get_report(status=0):
    try:
        reports = list(Report.objects.filter(status=status, delete=False).values(
            "id", "name", "tag", "monitor_start_date", "monitor_end_date",
            "platform", "accounts", "sales_point__name",
        ))
        map(lambda r: r.update(tag=json.loads(r["tag"]), accounts=json.loads(r["accounts"])), reports)

    except:
        logger.error(traceback.format_exc() + "\r\n"
                     + "[[get_report request data]]  status={}".format(status))
        return 0

    return json.dumps(reports, cls=DjangoJSONEncoder)


