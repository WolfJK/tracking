-- 数据库升级脚本

-- 1、品牌、品类、行业的调整
ALTER TABLE dim_category ADD industry_id int(11) NOT NULL default 1;
ALTER TABLE dim_brand DROP FOREIGN KEY dim_brand_industry_id_2caed131615ff999_fk_dim_industry_id;
alter table dim_brand drop column industry_id;
ALTER TABLE dim_brand ADD parent_id int NULL;

-- 2、report

DROP INDEX report_sales_point_id_5b0bb778e38ce642_uniq ON report;
ALTER TABLE report CHANGE sales_point_id sales_points varchar(512) COMMENT '主要竞品【json list 字符串】';

ALTER TABLE report ADD competitorss varchar(1024) NULL;

DROP INDEX report_brand_id_6195e9f82a8a6648_fk_dim_brand_id ON report;
ALTER TABLE report MODIFY brand_id varchar(1024) NOT NULL;

-- 3、修改 user
ALTER TABLE sm_user ADD activity_contrast_history varchar(1024) DEFAULT '[]' NOT NULL COMMENT '活动对比的历史记录, json 格式';


-- 3、添加 自定义函数
-- 使用说明: 该函数为处理 json 函数, 为json_extract 的升级补充, 支持 index 为 负数 和 嵌套使用。
drop FUNCTION json_index;
delimiter //
create function json_index(json_array varchar(1024), i int, path varchar(64)) returns varchar(1024)
begin
    declare ret varchar(1024);
    if i < 0 then set i = json_length(json_array) + i; end if ;
    set ret = json_unquote(json_extract(json_array, concat('$[', i, ']', path)));
RETURN ret;
end
//
delimiter ;


-- 4、添加 api 权限

select * from sm_menu;


insert into sm_menu(name, code) values ('活动对比', 'm005');
insert into sm_menu(name, code) values ('活动定位', 'm006');
insert into sm_menu(name, code) values ('品牌设置', 'm007');


select * from sm_api;

insert into sm_api(name, url) values ('设置-品牌设置_主要竞品新增', '/apps/common/competitor-save/');
insert into sm_api(name, url) values ('设置-品牌设置_主要竞品信息', '/apps/common/competitor-get/');
insert into sm_api(name, url) values ('设置-品牌设置_主要竞品删除', '/apps/common/competitor-del/');
insert into sm_api(name, url) values ('设置-品牌设置-主要竞品列表', '/apps/common/competitor-list/');

insert into sm_api(name, url) values ('活动对比', '/apps/report/activity-contrast/');
insert into sm_api(name, url) values ('活动对比-获取活动对比 的历史记录', '/apps/report/activity-contrast-history/');
insert into sm_api(name, url) values ('新建报告-根据品类品牌获取 竞品', '/apps/report/get-competitor/');

insert into sm_api(name, url) values ('活动定位-标签列表', '/apps/opinion-analysis/ao-activity-tag-list/');
insert into sm_api(name, url) values ('活动定位-品牌声量趋势', '/apps/opinion-analysis/ao-volume-trend/');
insert into sm_api(name, url) values ('活动定位-获取关键词云', '/apps/opinion-analysis/ao-keywords-cloud/');
insert into sm_api(name, url) values ('活动定位-热帖一览', '/apps/opinion-analysis/ao-activity-content/');

select * from sm_menu_apis;
insert into sm_menu_apis(smmenu_id, smapi_id) values (5, 17);
insert into sm_menu_apis(smmenu_id, smapi_id) values (5, 23);

insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 18);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 19);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 20);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 21);

insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 13);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 14);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 15);
insert into sm_menu_apis(smmenu_id, smapi_id) values (6, 16);

insert into sm_menu_apis(smmenu_id, smapi_id) values (2, 22);





select  * from sm_role;
select  * from sm_role_menus;

insert into sm_role_menus(smrole_id, smmenu_id) values (1, 5);
insert into sm_role_menus(smrole_id, smmenu_id) values (1, 6);
insert into sm_role_menus(smrole_id, smmenu_id) values (1, 7);

insert into sm_role_menus(smrole_id, smmenu_id) values (2, 5);
insert into sm_role_menus(smrole_id, smmenu_id) values (2, 6);
insert into sm_role_menus(smrole_id, smmenu_id) values (2, 7);




-- ---------------- dim_brand 初始化 脚本
-- truncate dim_brand_tmp;   【先导入 数据到 dim_brand_tmp 临时表】
drop table if exists dim_brand_load_tmp;
create table dim_brand_load_tmp
(
    id                  int auto_increment primary key,
    tagName             varchar(128)  null,
    keyword             varchar(512)  null,
    saas_keyword        varchar(5120) null,
    saas_exclude        varchar(5120) null,
    saas_exclude_remark varchar(5120) null,
    brand_2             varchar(64)   null,
    brand_3             varchar(64)   null,
    brand_1             varchar(64)   null,
    parent_id           int           null,
    saas                varchar(32)   null comment 'saas 的品牌名',
    category            varchar(64)   null
)
;

-- 1、更新字段
update dim_brand_load_tmp set
    brand_1 = regexp_substr(tagName, '[^.]+', 1, 2),
    brand_2 = regexp_substr(tagName, '[^.]+', 1, 3),
    brand_3 = regexp_substr(tagName, '[^.]+', 1, 4),
    category = case
    when regexp_substr(tagName, '[^.]+', 1, 1) = '奶粉品牌' then '奶粉'
    when regexp_substr(tagName, '[^.]+', 1, 1) = '咖啡品牌' then '咖啡'
    end
;

-- 2、去除 二级 和三级, 一级 和二级重复
update dim_brand_load_tmp set brand_3 = null where brand_2 is not null and brand_3 is not null and brand_2 = brand_3;
update dim_brand_load_tmp set brand_2 = null where brand_1 is not null and brand_2 is not null and brand_1 = brand_2;


-- 3、去重
drop table if exists dim_brand_deduplication_tmp;
create table dim_brand_deduplication_tmp as
select
    brand_1, brand_2, brand_3, max(keyword) as keyword, max(parent_id) as parent_id, max(saas) as saas,
    max(category) as category, max(saas_keyword) as saas_keyword, max(saas_exclude) as saas_exclude, max(saas_exclude_remark) as saas_exclude_remark
from dim_brand_load_tmp group by brand_1, brand_2, brand_3
;

-- 添加主键
ALTER TABLE dim_brand_deduplication_tmp ADD id int NOT NULL PRIMARY KEY AUTO_INCREMENT;


-- 3、加工 saas
update dim_brand_deduplication_tmp set saas = case
    when brand_1 is not null and brand_2 is not null and brand_3 is not null then concat(brand_1, '.', brand_2, '.', brand_3)
    when brand_1 is not null and brand_2 is not null then concat(brand_1, '.', brand_2)
    else brand_1
    end;

-- 4、加工 parent_id
update dim_brand_deduplication_tmp t1, dim_brand_deduplication_tmp t2
    set t1.parent_id = t2.id
where
    t1.brand_1 is not null and t1.brand_2 is not null and t1.brand_3 is not null
and t2.brand_1 is not null and t2.brand_2 is not null and t2.brand_3 is null
and t1.brand_1 = t2.brand_1 and t1.brand_2 = t2.brand_2
;

update dim_brand_deduplication_tmp t1, dim_brand_deduplication_tmp t2
    set t1.parent_id = t2.id
where
    t1.brand_1 is not null and t1.brand_2 is not null and t1.brand_3 is null
and t2.brand_1 is not null and t2.brand_2 is null and t2.brand_3 is null
and t1.brand_1 = t2.brand_1
;


-- 5、生成 dim_brand 表
insert into dim_brand(id, name, parent_id, saas, keyword, saas_keyword, saas_exclude, saas_exclude_remark)
select id, brand_3 as name, parent_id, saas, keyword, saas_keyword, saas_exclude, saas_exclude_remark from dim_brand_deduplication_tmp where brand_3 is not null
union
select id, brand_2 as name, parent_id, saas, keyword, saas_keyword, saas_exclude, saas_exclude_remark from dim_brand_deduplication_tmp where brand_3 is null and brand_2 is not null
union
select id, brand_1 as name, parent_id, saas, keyword, saas_keyword, saas_exclude, saas_exclude_remark from dim_brand_deduplication_tmp where brand_3 is null and brand_2 is null and brand_1 is not null
;
-- 6、更新 品牌 品类表

insert into dim_brand_category(brand_id, category_id) select id, 1 from dim_brand_deduplication_tmp where category = '奶粉';
insert into dim_brand_category(brand_id, category_id) select id, 3 from dim_brand_deduplication_tmp where category = '咖啡';
