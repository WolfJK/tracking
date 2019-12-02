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
