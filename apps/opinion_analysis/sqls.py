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
select * from vc_monitor_brand where category_id = {category_id} order by create_time desc;
"""

search_one_brand = """
select * from vc_monitor_brand where id={brand_id};
"""

# 按照品类获取所有监测品牌名称
get_all_brand_id = """
select id, json_index(brand, -1, '.name') as brand_name, competitor, time_slot from vc_monitor_brand where category_id = {category_id};
"""

# 当前品牌的声量
monitor_data_analysis_voice = """
select IFNULL(sum(count), 0) as voice from vc_saas_platform_volume where platform='全部' and 
brand = {brand_name} and category = {category_name} %s;
"""

# 竞品所有的声量
monitor_data_compete_voice = """
select IFNULL(sum(count), 0) as voice_all from  vc_saas_platform_volume  
where brand in %s and platform='全部' and category = {category_name}  %s ;
"""


# 全品类的声量
all_monitor_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_saas_platform_volume where platform='全部' and category = {category_name} %s;
"""


# 声量的趋势数据
all_data_card_voice_assert = """
with base0 as (
    select b.name, a.date
    from (select name from view_dim_brand where name = {brand_name}) b
    cross join (select date from dim_date a where 1= 1 %s ) a
),
base1 as (
    select brand, date, sum(count) count
        from vc_saas_platform_volume a
        where brand = {brand_name} and  platform='全部' and category={category_name} %s 
        group by date, brand order by date
) select base0.name brand, base0.date, ifnull(count, 0) count from base0 left join base1 on base0.date=base1.date
order by base0.date;
"""

# 按照id获取某一个品牌的name
get_brand_by_id = """
select category_id, time_slot, competitor,json_index(brand, -1, '.name') brand_name from vc_monitor_brand where id={brand_id};
"""


# 获取竞品的年月日各个声量
compete_day_month_week_voice = """
with e as (
    select brand, category, sum(count) count, date
    from vc_saas_platform_volume a
    where %s and brand in %s
        and category = {category_name} and  platform='全部' 
    group by date, brand, category
),
base1 as(
     select b.name, a.date from
        (select name from view_dim_brand where name in %s ) b cross join
        ( select * from dim_date a where %s) a
    )
select base1.name brand, %s date, sum(ifnull(e.count, 0)) count
from base1 left join e on base1.name = e.brand and e.date=base1.date
join dim_date base2 on base2.date=base1.date
group by base1.name, %s
order by base1.name, %s;
"""

# top5声量 全网不含本品
net_all_top5 = """
with e as (
    select a.brand,
           a.count,
           a.date
    from vc_saas_platform_volume a
    where a.brand != {brand_name} 
    and a.category = {category_name} %s
)select brand, ifnull(sum(count), 0) as count from e  group by brand order by count desc limit 5;
"""


bbv_classify_all_top5 = """
with e as (
    select a.brand,
           a.count,
           a.date
    from vc_mp_platform_area_volume a
    where a.brand != {brand_name}
    and platform in %s
    and a.category = {category_name} %s
)select brand, ifnull(sum(count), 0) as count from e  group by brand order by count desc limit 5;
"""

bbv_all_top5 = """
with e as (
    select a.brand,
           a.count,
           a.date
    from vc_mp_platform_area_volume a
    where a.brand != {brand_name} and type='bbv' 
    and a.category = {category_name} %s
)select brand, ifnull(sum(count), 0) as count from e  group by brand order by count desc limit 5;
"""

ww_net_all_top5 = """
with e as (
    select a.brand,
           a.count,
           a.date
    from vc_saas_platform_volume a
    where a.brand != {brand_name} and platform in %s
    and a.category = {category_name} %s
)select brand, ifnull(sum(count), 0) as count from e  group by brand order by count desc limit 5;
"""

# 品牌声量柱形图
brand_voice_histogram = """
select a.name brand, sum(ifnull(count, 0)) count
from (select name from view_dim_brand
  where name in %s 
  group by name
)a
left join (
    select a.brand, a.count
    from vc_saas_platform_volume a
    where a.brand in %s 
    and platform='全部'
    and a.category =  {category_name}  %s
    ) b on a.name = b.brand
group by a.name order by count desc ;
"""

brand_ww_voice_histogram = """
select a.name brand, sum(ifnull(count, 0)) count
from (select name from view_dim_brand
  where name in %s 
  group by name
)a
left join (
    select a.brand, a.count
    from vc_saas_platform_volume a
    where a.brand in %s 
    and a.platform in %s 
    and a.category =  {category_name}  %s
    ) b on a.name = b.brand
group by a.name order by count desc ;
"""


# 单前所选时间段的各品牌的总和用于计算环形图sov
round_sum_sov = """
with e as (
    select a.count
    from vc_saas_platform_volume a
    where a.brand in %s
    and  platform='全部'
    and a.category = {category_name}  %s
)select ifnull(sum(count), 0) as count from e;
"""

round_ww_sum_sov = """
with e as (
    select a.count
    from vc_saas_platform_volume a
    where a.brand in %s
    and a.platform in %s 
    and a.category = {category_name}  %s
)select ifnull(sum(count), 0) as count from e;
"""


round_all_brand_sum_sov = """
with e as (
    select a.count
    from vc_saas_platform_volume a
    where a.category = {category_name} and platform='全部'  %s
)select ifnull(sum(count), 0) as count from e;
"""

ww_round_sum_sov = """
with e as (
    select a.count
    from vc_saas_platform_volume a
    where a.platform in %s
    and a.category = {category_name}  %s
)select ifnull(sum(count), 0) as count from e;
"""

# 获取分类的年月周的分类数据总和 用于计算sov的趋势图
area_of_tend_sov = """
with e as (
    select sum(count) count, a.date
    from vc_saas_platform_volume a
    where %s 
    and a.brand in %s 
    and a.category = {category_name}
    and platform='全部'
    group by a.date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s 
group by %s
order by %s asc;
"""

area_of_all_brand_tend_sov = """
with e as (
    select sum(count) count, a.date
    from vc_saas_platform_volume a
    where %s 
    and a.category = {category_name}
    and  platform='全部'
    group by a.date
)
select %s date, 
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where %s
group by %s
order by %s asc;
"""



# 获取各个平台总的声量
platform_voice_sum = """
select a.name brand, ifnull(b.count, 0) count
from (select name from view_dim_brand
  where name in %s 
  group by name
) a
left join (select brand, sum(count) as count from vc_saas_platform_volume a
where brand in %s and platform='全部' 
and category = {category_name}  %s 
group by brand) b on a.name = b.brand
;
"""

# 各个平台的分类的声量
platfom_classify_count_milk = """
with base0 as (
    select a.name, b.platform
    from
    (select name from view_dim_brand
      where name in %s 
      group by name) a cross join
    (select name platform from dim_platform where json_contains(visible, '[3]') group by name) b
) select base0.name brand, base0.platform, ifnull(base1.count, 0) count
    from base0 left join (
    select platform, brand, sum(count) as  count
        from vc_saas_platform_volume a where brand in %s 
        and category = {category_name}  %s 
        group by platform, brand
    ) base1 on base0.name=base1.brand and base0.platform=base1.platform;
"""

platfom_classify_count_coffee = """
with base0 as (
    select a.name, b.platform
    from
    (select name from view_dim_brand
      where name in %s 
      group by name) a cross join
    (select name platform from dim_platform where json_contains(visible, '[4]') group by name) b
) select base0.name brand, base0.platform, ifnull(base1.count, 0) count
    from base0 left join (
    select platform, brand, sum(count) as  count
        from vc_saas_platform_volume a where brand in %s 
        and category = {category_name}  %s 
        group by platform, brand
    ) base1 on base0.name=base1.brand and base0.platform=base1.platform;
"""

# 各个地域声量的总计
area_voice_sum = """
select area, ifnull(sum(count), 0) as count from vc_saas_area_volume a where brand in %s
 and category = {category_name} %s
group by area;
"""


# 各个地域的分类的声量
area_voice_classify = """
select area, ifnull(sum(count), 0) count from vc_saas_area_volume a where brand={brand_name}
 and category = {category_name}  %s
 and area not in ('其他', '')
group by area order by count desc ;
"""

# 全网关键词获取
net_keywords = """
select keywords, ifnull(sum(count), 0) as count from vc_mp_keywords_cloud a where
    brand={brand_name} and a.category= {category_name} %s and %s
group by keywords
order by count desc limit 20;
"""


# 内容分布雷达图总数
content_radar = """
select brand, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s 
and category= {category_name} %s
group by brand;
"""

content_radar_bbv_all = """
select brand, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s
and category= {category_name}
and a.type='bbv' %s
group by brand;
"""

content_radar_other_platform = """
select brand, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s
and category= {category_name} 
and a.platform in %s %s 
group by brand;
"""

content_radar_classify = """
select brand, cognition, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s 
and category={category_name} %s
group by  cognition, brand;
"""

content_radar_classify_bbv_all = """
select brand, cognition, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s 
and a.type ='bbv'
and category={category_name} %s
group by  cognition, brand;
"""

content_radar_classify_other_platform = """
select brand, cognition, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s
and category= {category_name} 
and a.platform in %s %s 
group by brand, cognition;
"""

# bbv竞品所有的声量全部品牌的话为0 bbv子集的话为1
monitor_data_bbv_all_compete_voice = """
select ifnull(sum(count), 0) as voice_all from vc_mp_platform_area_volume
where brand in %s and platform !='其他'
and category = {category_name} and type='bbv' %s;
"""

# bbv各个平台的竞品所有的声量
monitor_data_classify_compete_voice = """
select ifnull(sum(count), 0) as voice_all from vc_mp_platform_area_volume
where brand in %s
and category = {category_name} and platform in %s %s;
"""

# bbv获取全品类的声量
bbv_all_sum_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_mp_platform_area_volume 
where platform !='其他' 
and category = {category_name}  and type='bbv' %s;
"""

bbv_platform_classify_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_mp_platform_area_volume 
where category = {category_name} and platform in %s %s;
"""

# 本品的bbv平台分类
self_brand_bbv_classify = """
select IFNULL(sum(count), 0) as voice from vc_mp_platform_area_volume
where brand = {brand_name} and category = {category_name}
and platform in %s %s
"""

self_brand_bbv_all = """
select IFNULL(sum(count), 0) as voice from vc_mp_platform_area_volume
where platform !='其他' 
and brand = {brand_name} and category = {category_name}  and type='bbv' %s
"""

# ==========bbv================
# 获取竞品的年月日各个声量 all
bbv_compete_day_month_week_voice = """
with e as (
    select brand, category, sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and brand in %s 
        and category = {category_name}
        and a.type = 'bbv' 
        and platform !='其他' 
    group by date, brand, category
),
base1 as(
     select b.name, a.date from
        (select name from view_dim_brand
         where name in %s) b cross join
        ( select * from dim_date a where %s) a
    )
select base1.name  brand, %s date, sum(ifnull(e.count, 0)) count
from base1 left join e on base1.name = e.brand and e.date=base1.date
join dim_date base2 on base2.date=base1.date
group by base1.name, %s
order by base1.name, %s;
"""

bbv_platform_compete_day_month_week_voice = """
with e as (
    select brand, category, sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and brand in %s  and a.platform in %s 
        and category = {category_name}
    group by date, brand, category
),
base1 as(
     select b.name, a.date from
        (select name from view_dim_brand
         where name in %s) b cross join
        ( select * from dim_date a where %s) a
    )
select base1.name  brand, %s date, sum(ifnull(e.count, 0)) count
from base1 left join e on base1.name = e.brand and e.date=base1.date
join dim_date base2 on base2.date=base1.date
group by base1.name, %s
order by base1.name, %s;
"""

bbv_area_of_tend_sov = """
with e as (
    select sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and category = {category_name}
    and a.brand in %s 
    and a.platform !='其他' 
    and type = 'bbv'  group by date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s
group by %s
order by %s asc;
"""


bbv_area_all_brand_of_tend_sov = """
with e as (
    select sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and category = {category_name}
    and platform !='其他' 
    and type = 'bbv'  group by date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s
group by %s
order by %s asc;
"""


bbv_platform_area_of_tend_sov = """
with e as (
    select sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and category = {category_name}
    and a.brand in %s  and a.platform in %s  group by date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s
group by %s
order by %s asc;
"""

bbv_platform_area_all_brand_of_tend_sov = """
with e as (
    select sum(count) count, date
    from vc_mp_platform_area_volume a
    where %s and category = {category_name} 
    and a.platform in %s group by date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s
group by %s
order by %s asc;
"""



# all品牌声量条形图
bbv_brand_voice_histogram = """
select a.name brand, sum(ifnull(count, 0)) count
from (select name from view_dim_brand
  where name in %s 
  group by name
)a
left join (
    select a.brand, a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s 
    and platform != '其他' 
    and a.category = {category_name}  and a.type = 'bbv' %s 
    ) b on a.name = b.brand
group by a.name order by count desc;
"""

bbv_platform_brand_voice_histogram = """
select a.name brand, sum(ifnull(count, 0)) count
from (select name from view_dim_brand
  where name in %s 
  group by name
)a
left join (
    select a.brand, a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s 
    and a.category = {category_name} 
    and a.platform in %s  %s 
    ) b on a.name = b.brand
group by a.name order by count desc;
"""

# bbv_声量总数用于计算sov面积图的百分比
bbv_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.category = {category_name}
    and a.platform != '其他'
    and a.type = 'bbv' %s 
)select ifnull(sum(count), 0) as count from e;
"""


bbv_all_brand_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.category = {category_name}
    and platform != '其他' 
    and a.type = 'bbv' %s 
)select ifnull(sum(count), 0) as count from e;
"""

bbv_platform_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.brand in %s
    and a.category = {category_name}
    and a.platform in %s %s 
)select ifnull(sum(count), 0) as count from e;
"""

bbv_platform_all_brand_round_sum_sov = """
with e as (
    select a.count
    from vc_mp_platform_area_volume a
    where a.category = {category_name}
    and a.platform in %s %s 
)select ifnull(sum(count), 0)  as count from e;
"""


# bbv获取各个平台总的声量
bbv_platform_voice_sum_all = """
select a.name brand, ifnull(b.count, 0) count
from (select name from view_dim_brand
  where name in %s 
  group by name
) a
left join (select brand, sum(count) as count from vc_mp_platform_area_volume a
where brand in %s and platform in (select name platform from dim_platform where json_contains(visible, '[2]') group by name)
and category = {category_name}  and a.type = 'bbv'  %s 
group by brand)b on a.name = b.brand
;
"""

bbv_platform_voice_all_classify = """
with base0 as (
    select a.name, b.platform
    from
    (select name from view_dim_brand
      where name in %s 
      group by name) a cross join
    (select name platform from dim_platform where json_contains(visible, '[2]') group by name) b
) select base0.name brand, base0.platform, ifnull(base1.count, 0) count
    from base0 left join (
    select platform, brand, sum(count) as count from vc_mp_platform_area_volume a
    where brand in %s 
    and category = {category_name}  and a.type = 'bbv'  %s 
    group by platform, brand
    ) base1 on base0.name=base1.brand and base0.platform=base1.platform;
    
"""


# 子集下面平台的分类的声量
bbv_platfom_classify_sum = """
select platform, brand, ifnull(sum(count), 0) as  count from vc_mp_platform_area_volume a where brand in %s
and category = {category_name}  and a.platform in %s %s
group by platform, brand;
"""

bbv_platfom_classify_count = """
select brand, ifnull(sum(count), 0) as  count from vc_mp_platform_area_volume a where brand in %s
and category = {category_name}  and a.platform in %s %s
group by brand;
"""

# bbv各个地域的分类的声量
bbv_area_voice_classify = """
select area,ifnull(sum(count), 0) count from vc_mp_platform_area_volume a where brand={brand_name}
and category = {category_name} 
and area not in ('其他', '')
and a.type='bbv'  %s
group by area  order by count desc ;
"""

bbv_platform_area_voice_classify = """
select area, ifnull(sum(count), 0) count from vc_mp_platform_area_volume a where brand={brand_name}
and category = {category_name} 
and area not in ('其他', '') 
and a.platform in %s  %s
group by area  order by count desc ;
"""

# bbv全网关键词获取
bbv_all_keywords = """
select keywords, ifnull(sum(count), 0) as count from vc_mp_keywords_cloud a where
    brand={brand_name} and
    a.category= {category_name} and a.type='bbv' %s  and %s
group by keywords
order by count desc limit 20;
"""

bbv_platform_keywords_classify = """
select keywords, ifnull(sum(count), 0) as count from vc_mp_keywords_cloud a where
    brand={brand_name} and
    a.category= {category_name} and a.platform in %s %s and  %s
group by keywords
order by count desc limit 20;
"""

# bbv内容分布雷达图总数
bbv_content_radar = """
select ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s and category= {category_name} and a.type='bbv' %s;
"""

bbv_content_radar_classify = """
select cognition, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s and category= {category_name}  and a.type='bbv' %s
group by  cognition
"""

bbv_platform_content_radar = """
select ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s and category= {category_name} and a.platform in %s %s;
"""

bbv_platform_content_radar_classify = """
select cognition, ifnull(sum(count), 0) count  from vc_mp_first_level_cognition a
where brand in %s and category= {category_name} and a.platform in %s %s
group by  cognition
"""


# ====================奶粉社煤微博微信平台=================================
# 奶粉社煤竞品 微信 微博从sass
milk_dw_all_compete_voice = """
select ifnull(sum(count), 0) as voice_all from vc_saas_platform_volume
where brand in %s
and category = {category_name} and platform in %s %s;
"""

# 微薄微信全品类的声量
milk_platform_classify_voice = """
select IFNULL(sum(count), 0) as voice_all from vc_saas_platform_volume 
where category = {category_name} and platform in %s %s;
"""

# 微薄微信本品类的声量
self_brand_milk_classify = """
select IFNULL(sum(count), 0) as voice from vc_saas_platform_volume
where brand = {brand_name} and category = {category_name} 
and platform in %s %s
"""

ww_compete_day_month_week_voice = """
with e as (
    select brand, category, sum(count) count, date
    from vc_saas_platform_volume a
    where %s and brand in %s and  a.platform in %s 
        and category = {category_name}
    group by date, brand, category
),
base1 as(
     select b.name, a.date from
        (select name from view_dim_brand where name in %s ) b cross join
        ( select * from dim_date a where %s) a
    )
select base1.name brand, %s date, sum(ifnull(e.count, 0)) count
from base1 left join e on base1.name = e.brand and e.date=base1.date
join dim_date base2 on base2.date=base1.date
group by base1.name, %s
order by base1.name, %s;
"""


ww_area_of_tend_sov = """
with e as (
    select sum(count) count, a.date
    from vc_saas_platform_volume a 
    where %s 
    and a.brand in %s  and a.platform in %s
    and a.category = {category_name}
    group by a.date
)
select %s date,
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where  %s 
group by %s
order by %s asc;
"""

ww_area_all_brand_of_tend_sov = """
with e as (
    select sum(count) count, a.date
    from vc_saas_platform_volume a
    where %s and a.platform in %s
    and a.category = {category_name}
    group by a.date
)
select %s date, 
       ifnull(sum(count), 0) as count
from  dim_date a left join  e on e.date = a.date
where %s
group by %s
order by %s asc;
"""

# dsmtop20微博发帖
dsm_weibo_official_top20 = """
with e as (
 select id, url, sum(ifnull(reviews, 0) + ifnull(retweets, 0) + ifnull(praise_points, 0)) count
    from vc_mp_consensus_content a
      where  %s 
      and type={type_from}
      and a.platform ={platform}
      and a.brand ={brand_name}
      and a.category={category_name}
    group by id, url
),base1 as
    (select url, max(count) count, max(id) id from e  group by url limit 20)
select a.*, base1.count from vc_mp_consensus_content a join base1 on base1.id=a.id
    where %s 
    and type={type_from}
    and a.platform ={platform}
    and a.brand ={brand_name}
    and a.category={category_name}
order by base1.count desc;
"""
# 微信
dsm_weixin_official_top20 = """
with e as (
 select id, url, sum(ifnull(praise_points, 0)) count
    from vc_mp_consensus_content a
      where  %s 
      and type={type_from}
      and a.platform ={platform}
      and a.brand ={brand_name}
      and a.category={category_name}
    group by id, url
),base1 as
    (select url, max(count) count, max(id) id from e  group by url limit 20)
select a.*, base1.count from vc_mp_consensus_content a join base1 on base1.id=a.id
    where %s 
    and type={type_from}
    and a.platform ={platform}
    and a.brand ={brand_name}
    and a.category={category_name}
order by base1.count desc;
"""

# 小红书
dsm_redbook_official_top20 = """
with e as (
 select id, url, sum(ifnull(reviews, 0) + ifnull(retweets, 0) + ifnull(praise_points, 0) + ifnull(favorite, 0)) count
    from vc_mp_consensus_content a
      where  %s 
      and type={type_from}
      and a.platform ={platform}
      and a.brand ={brand_name}
      and a.category={category_name}
    group by id, url
),base1 as
    (select url, max(count) count, max(id) id from e  group by url limit 20)
select a.*, base1.count from vc_mp_consensus_content a join base1 on base1.id=a.id
    where %s 
    and type={type_from}
    and a.platform ={platform}
    and a.brand ={brand_name}
    and a.category={category_name}
order by base1.count desc;
"""


# 玉珏图统一取出的二级认知的top5
randar_patter_map = """
with t as (
    select level1, 
           level2, 
           round(count2/count1*100, 2) as count ,
           ROW_NUMBER() OVER(PARTITION BY level1 ORDER BY count2 DESC) as rn
    from (select level1, level2,
          sum(sum(count)) over(partition by level1) count1,
          sum(count) count2
          from vc_mp_cognition
          where brand = {brand_name}
          and category = {category_name}
          and platform = {platform} %s and level2 !=''
          group by level1, level2) e
) select * from t where rn<=5;
"""

# 三级认知的计算玉珏图
region_three_for_randar = """
with e as (
select
       level1,
       level2,
       level3,
       sum(sum(count)) over(partition by level1, level2) count1,
       sum(sum(count)) over(partition by level1, level2, level3) count2
from vc_mp_cognition
where brand = {brand_name}
and category = {category_name}
and platform = {platform}
and level1 in %s
and level2 in %s %s and level2!=''
group by level1, level2, level3),
base0 as (
    select level1,
       level2,
       level3,
       round(count2/count1*100, 2) as count ,
       row_number() over(partition by level1,level2 order by count2 desc) as rn
    from e
  )select * from base0 where rn<=5;
"""


# 获取地域
get_standard_area = """
select * from dim_area
"""


# 词云排除词
keywords_cloud_exclude = ['。', '；', '，', '：', '“', '”', '（', '）','、', '？', '《' '》', ' ',
                          '', '/', '*', '…', '」', '「', '↓', '-', 'Ⅱ', '', '·', '—', '', '‘',
                          '+', ',', '##', '\"', '&#', '～', ')', '(', '☕', '	', '	', ' 	', '⃣ ',
                          '❤', '$', '|', '➕', '✨', ' ', '']