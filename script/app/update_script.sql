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
insert into sm_api(name, url) values ('新建报告-根据品类品牌获取 竞品', '/apps/report/get-competitor/');

insert into sm_api(name, url) values ('活动定位-标签列表', '/apps/opinion-analysis/ao-activity-tag-list/');
insert into sm_api(name, url) values ('活动定位-品牌声量趋势', '/apps/opinion-analysis/ao-volume-trend/');
insert into sm_api(name, url) values ('活动定位-获取关键词云', '/apps/opinion-analysis/ao-keywords-cloud/');
insert into sm_api(name, url) values ('活动定位-热帖一览', '/apps/opinion-analysis/ao-activity-content/');

select * from sm_menu_apis;
insert into sm_menu_apis(smmenu_id, smapi_id) values (5, 17);

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

