# coding: utf-8
# __author__: 'GUO'
from __future__ import unicode_literals

from common.models import *
import json
from apps.opinion_analysis import sqls
from common.db_helper import DB
from datetime import datetime


def add_monitor_brand(monitor_id, category, brand, time_slot, competitor):
    brand = json.loads(brand)
    if competitor:
        competitor = json.loads(competitor)
    if not monitor_id:
        if isinstance(competitor, list):  # 新增竞品
            VcMonitorBrand(category_id=category, brand=json.dumps(brand),
                           competitor=json.dumps(competitor), time_slot=time_slot).save()
        else:  # 新增全品类
            VcMonitorBrand(category_id=category, brand=json.dumps(brand), competitor=competitor, time_slot=time_slot).save()
    else:
        monitor_brand = VcMonitorBrand.objects.get(id=monitor_id)
        if isinstance(competitor, list):  # 修改竞品
            monitor_brand.competitor = json.dumps(competitor)
            monitor_brand.time_slot = time_slot
        else:  # 修改全品类
            monitor_brand.competitor = None
        monitor_brand.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        monitor_brand.save()


def get_compete_brand(vc_monitor_list):
    if isinstance(vc_monitor_list, list):
        data = vc_monitor_list[-1]
        brand_id = data.get("id")
        results_dict = DB.get(sqls.compete_brand, {"brand_id": brand_id})
        results_str = results_dict.get("competitors")
        results = json.loads(results_str)
    else:
        results = []
    return results


