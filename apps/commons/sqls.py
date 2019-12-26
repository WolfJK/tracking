# coding: utf-8
# __author__: ""
from __future__ import unicode_literals

# 设置, 竞品列表
competitor_list = '''
select
    c1.id,
    c3.name as industry,
    c2.name as category,
    c1.brand as brand,
    c1.competitors
from
    sm_competitor c1
left join
    dim_category c2
on c1.category_id = c2.id
left join
    dim_industry c3
on c2.industry_id = c3.id
where
    (c3.name regexp {queue_filter}
 or c2.name regexp {queue_filter}
 or json_index(brand, -1, '') regexp {queue_filter}
 or '' = {queue_filter}
 ) and user_id = {user_id}
 order by c1.update_time desc, c1.create_time desc
;

'''