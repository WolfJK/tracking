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
select IFNULL(sum(count), 0) as voice from vc_saas_platform_volume where 
brand = {brand_name} and cagegory = {category_name} %s;
"""

# 竞品所有的声量
monitor_data_compete_voice = """
select IFNULL(sum(count), 0) as voice_all from  vc_saas_platform_volume  
where brand in %s and cagegory = {category_name}  %s ;
"""


# 全品类的声量
all_monitor_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_saas_platform_volume where cagegory = {category_name} %s;
"""


# 声量的趋势数据
all_data_card_voice_assert = """
select count, date from vc_saas_platform_volume where brand={brand_name} and cagegory={category_name}  
order by date limit %s;
"""

# 按照id获取某一个品牌的name
get_brand_by_id = """
select category_id, time_slot, competitor,json_index(brand, -1, '.name') brand_name from vc_monitor_brand where id={brand_id};
"""


# 获取竞品的年月日各个声量
compete_day_month_week_voice = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_saas_area_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
      and a.cagegory = {category_name} %s 
)select brand, %s, sum(count) as count from e group by %s, brand order by brand, %s asc;
"""

# top5声量 不含本品
all_top5 = """
with e as (
    select a.brand,
           a.count,
           a.date
    from vc_saas_platform_volume a
    where a.brand != {bran_name} 
    and a.cagegory = {category_name} %s 
)select brand, sum(count) as count from e  group by brand order by count desc limit 5;
"""

# 品牌声量柱形图
brand_voice_histogram = """
with e as (
    select a.brand,
           a.cagegory,
           a.count,
           a.date
    from vc_saas_platform_volume a
    where a.brand in %s
    and a.cagegory = {category_name}  %s 
)select brand, sum(count) as count from e  group by brand order by count desc;
"""

# 单前所选时间段的各品牌的总和用于计算环形图sov
round_sum_sov = """
with e as (
    select a.count
    from vc_saas_platform_volume a
    where a.brand in %s
    and a.cagegory = {category_name}  %s
)select sum(count) as count from e;
"""

# 获取分类的年月周的分类数据总和 用于计算sov的趋势图
area_of_tend_sov = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_saas_platform_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
    and a.cagegory = {category_name} %s
)select %s, sum(count) as count from e group by %s order by %s asc;
"""

# 获取各个平台总的声量
platform_voice_sum = """
select brand, sum(count) as count from vc_saas_platform_volume a where brand in %s
and cagegory = {category_name} %s
group by brand;
"""

# 各个平台的分类的声量
platfom_classify_count = """
select platform, brand, sum(count) as  count from vc_saas_platform_volume a where brand in %s
and cagegory = {category_name}  %s
group by platform, brand;
"""

# 各个地域声量的总计
area_voice_sum = """
select area, sum(count) as count from vc_saas_area_volume a where brand in %s
 and cagegory = {category_name} %s
group by area;
"""


# 各个地域的分类的声量
area_voice_classify = """
select area, sum(count) count from vc_saas_area_volume a where brand in %s
 and cagegory = {category_name}  %s
group by area order by count desc ;
"""

# 全网关键词获取
net_keywords = """
select keywords, sum(count) as count from vc_mp_keywords_cloud a where
    brand in %s and
    a.cagegory= {category_name} %s 
group by keywords
order by count desc limit 20;
"""


# 内容分布雷达图总数
content_radar = """
select sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name} %s;
"""

content_radar_classify = """
select cognition, sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name} %s
group by  cognition
"""


# bbv竞品所有的声量
monitor_data_bbv_all_compete_voice = """
select ifnull(sum(count), 0) as voice_all from vc_mp_platform_area_volume
where brand in %s
and cagegory = {category_name} and type='bbv' %s;
"""

# bbv各个平台的竞品所有的声量
monitor_data_classify_compete_voice = """
select ifnull(sum(count), 0) as voice_all from vc_mp_platform_area_volume
where brand in %s
and cagegory = {category_name} and platform in %s %s;
"""

# bbv获取全品类的声量
bbv_all_sum_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_mp_platform_area_volume 
where cagegory = {category_name}  and type='bbv' %s;
"""

bbv_platform_classify_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_mp_platform_area_volume 
where cagegory = {category_name} and platform in %s %s;
"""

# 本品的bbv平台分类
self_brand_bbv_classify = """
select IFNULL(sum(count), 0) as voice from vc_mp_platform_area_volume
where brand = {brand_name} and cagegory = {category_name} 
and platform in %s %s
"""

self_brand_bbv_all = """
select IFNULL(sum(count), 0) as voice from vc_mp_platform_area_volume
where brand = {brand_name} and cagegory = {category_name}  and type='bbv' %s
"""

# ==========bbv================
# 获取竞品的年月日各个声量 all
bbv_compete_day_month_week_voice = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_mp_platform_area_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
    and a.cagegory = {category_name}
    and a.type = 'bbv' %s 
)select brand, %s, sum(count) as count from e group by %s, brand order by brand, %s asc;
"""

bbv_platform_compete_day_month_week_voice = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_mp_platform_area_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
    and a.cagegory = {category_name}
    and a.platform in %s %s 
)select brand, %s, sum(count) as count from e group by %s, brand order by brand, %s asc;
"""

bbv_area_of_tend_sov = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_mp_platform_area_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.type = 'bbv' %s
)select %s, sum(count) as count from e group by %s order by %s asc;
"""

bbv_platform_area_of_tend_sov = """
with e as (
    select a.brand,
           a.cagegory,
           b.month,
           a.count,
           b.week,
           a.date
    from vc_mp_platform_area_volume a
    join dim_date b on a.date = b.date
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.platform in %s %s
)select %s, sum(count) as count from e group by %s order by %s asc;
"""

# all品牌声量条形图
bbv_brand_voice_histogram = """
with e as (
    select a.brand,
           a.cagegory,
           a.count,
           a.date
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.type = 'bbv' %s 
)select brand, sum(count) as count from e  group by brand order by count desc;
"""

bbv_platform_brand_voice_histogram = """
with e as (
    select a.brand,
           a.cagegory,
           a.count,
           a.date
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.platform in %s %s 
)select brand, sum(count) as count from e  group by brand order by count desc;
"""

# bbv_声量总数用于计算sov面积图的百分比
bbv_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.type = 'bbv' %s 
)select sum(count) as count from e;
"""

bbv_platform_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.cagegory = {category_name} 
    and a.platform in %s %s 
)select sum(count) as count from e;
"""

# bbv获取各个平台总的声量
bbv_platform_voice_sum_all = """
select brand, sum(count) as count from vc_mp_platform_area_volume a 
where brand in %s
and cagegory = {category_name}  and a.type = 'bbv' %s 
group by brand;
"""

bbv_platform_voice_all_classify = """
select platform, brand, sum(count) as count from vc_mp_platform_area_volume a 
where brand in %s
and cagegory = {category_name}  and a.type = 'bbv' %s 
group by platform, brand;
"""


# 子集下面平台的分类的声量
bbv_platfom_classify_sum = """
select platform, brand, sum(count) as  count from vc_mp_platform_area_volume a where brand in %s
and cagegory = {category_name}  and a.platform in %s %s 
group by platform, brand;
"""

bbv_platfom_classify_count = """
select brand, sum(count) as  count from vc_mp_platform_area_volume a where brand in %s
and cagegory = {category_name}  and a.platform in %s %s 
group by brand;
"""

# bbv各个地域的分类的声量
bbv_area_voice_classify = """
select area, sum(count) count from vc_mp_platform_area_volume a where brand in %s
and cagegory = {category_name} and a.type='bbv'  %s
group by area  order by count desc ;
"""

# bbv全网关键词获取
bbv_all_keywords = """
select keywords, sum(count) as count from vc_mp_keywords_cloud a where
    brand in %s and
    a.cagegory= {category_name} and a.type='bbv' %s 
group by keywords
order by count desc limit 20;
"""

bbv_platform_keywords_classify = """
select keywords, sum(count) as count from vc_mp_keywords_cloud a where
    brand in %s and
    a.cagegory= {category_name} and a.platform in %s %s 
group by keywords
order by count desc limit 20;
"""

# bbv内容分布雷达图总数
bbv_content_radar = """
select sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name} and a.type='bbv' %s;
"""

bbv_content_radar_classify = """
select cognition, sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name}  and a.type='bbv' %s
group by  cognition
"""

bbv_platform_content_radar = """
select sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name} and a.platform in %s %s;
"""

bbv_platform_content_radar_classify = """
select cognition, sum(count) count  from vc_mp_first_level_cognition a
where brand in %s and cagegory= {category_name} and a.platform in %s %s
group by  cognition
"""