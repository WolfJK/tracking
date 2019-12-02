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

get_all_brand_id = """
select id, json_index(brand, -1, '.name') as brand_name, competitor, time_slot from vc_monitor_brand where category_id = {category_id};
"""

monitor_data_analysis_voice = """
select sum(IFNULL(count, 0)) as voice from vc_saas_area_volume where 
brand = {brand_name} and cagegory = {category_name} order by date desc limit %s;
"""

monitor_data_compete_voice = """
SELECT sum(tt) AS voice_all
FROM 
    (SELECT brand,
         sum(IFNULL(count,
         0)) AS tt
    FROM 
        (SELECT *
        FROM vc_saas_area_volume
        WHERE brand IN %s
                AND cagegory = {category_name}
        ORDER BY  date DESC limit %s) a
        GROUP BY  brand) b
"""

all_monitor_voice = """
SELECT sum(tt) AS voice_all
FROM 
    (SELECT brand,
         sum(IFNULL(count,
        0)) AS tt
    FROM 
        (SELECT *
        FROM vc_saas_area_volume
        WHERE cagegory = {category_name}
        ORDER BY  date limit %s) a
        GROUP BY  brand) b;
"""