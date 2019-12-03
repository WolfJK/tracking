# coding: utf-8
# __author__: ""
from __future__ import unicode_literals


sm_competitor_compete_brand = """
select competitors from sm_competitor where json_index(brand, -1, '.id') = {brand_id};
"""

vc_monitor_brand_compete = """
select competitor from vc_monitor_brand where id = {brand_id};
"""

search_monitor_brand = """
select * from vc_monitor_brand where json_index(brand, -1, '.name') regexp {brand_name} and category_id = {category_id};
"""

search_monitor_brand_type = """
select * from vc_monitor_brand where category_id = {category_id};
"""

# 按照品类获取所有监测品牌名称
get_all_brand_id = """
select id, json_index(brand, -1, '.name') as brand_name, competitor, time_slot from vc_monitor_brand where category_id = {category_id};
"""

# 当前品牌的声量
monitor_data_analysis_voice = """
select sum(IFNULL(count, 0)) as voice from vc_saas_area_volume where 
brand = {brand_name} and cagegory = {category_name} %s order by date desc limit %s;
"""

# 竞品所有的声量
monitor_data_compete_voice = """
with e as (
select brand,
       count,
       ROW_NUMBER() OVER(PARTITION BY brand ORDER BY date DESC) as rn
from vc_saas_area_volume where brand in %s and cagegory = {category_name}  %s
    ) select sum(count) as voice_all from e where rn<=%s;
"""


# 全品类的声量
all_monitor_voice = """
with e as (
select brand,
       count,
       ROW_NUMBER() OVER(PARTITION BY brand ORDER BY date DESC) as rn
from vc_saas_area_volume where cagegory = {category_name} %s
    ) select sum(count) as voice_all from e where rn<=%s;
"""


# 声量的趋势数据
all_data_card_voice_assert = """
select count, date from vc_saas_area_volume where brand={brand_name} and cagegory={category_name} %s 
order by date limit %s;
"""

# 按照id获取某一个品牌的name
get_brand_by_id = """
select category_id, time_slot, competitor,json_index(brand, -1, '.name') brand_name from vc_monitor_brand where id={brand_id};
"""