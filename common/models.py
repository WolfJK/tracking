# coding: utf8
# __author__ = "James"
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class SmApi(models.Model):
    name = models.CharField(max_length=32, help_text="接口名称")
    url = models.CharField(max_length=64, help_text="接口名称")

    class Meta:
        db_table = "sm_api"

    def __str__(self):
        return self.name


class SmMenu(models.Model):
    name = models.CharField(max_length=32, help_text="菜单名称")
    code = models.CharField(max_length=32, help_text="菜单编号")
    apis = models.ManyToManyField(to='SmApi', blank=True, db_constraint=False)

    class Meta:
        db_table = "sm_menu"

    def __str__(self):
        return self.name


class SmRole(models.Model):
    name = models.CharField(max_length=32, help_text="角色名称")
    menus = models.ManyToManyField(to='SmMenu', blank=True)

    class Meta:
        db_table = "sm_role"

    def __str__(self):
        return self.name


class DimIndustry(models.Model):
    """
    行业表
    """
    name = models.CharField(max_length=32, help_text="行业")

    class Meta:
        db_table = "dim_industry"


class DimBrand(models.Model):
    # TODO 和品类是 那种关系 M - M
    name = models.CharField(max_length=32, help_text="品牌名称")
    keyword = models.CharField(max_length=512, help_text="抓取关键词")
    industry = models.ForeignKey(DimIndustry, help_text="所属行业", on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "dim_brand"


class DimCategory(models.Model):
    """
    品类表
    """
    name = models.CharField(max_length=32, help_text="品类名称")

    class Meta:
        db_table = "dim_category"


class DimBrandCategory(models.Model):
    """
    品牌 品类关系表
    """
    brand = models.ForeignKey(DimBrand, help_text="品牌", on_delete=models.DO_NOTHING)
    category = models.ForeignKey(DimCategory, help_text="品类", on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "dim_brand_category"


class SmUser(AbstractBaseUser):
    """
        TODO 用户是否会是以组织/机构/公司的形式出现?
        公司多用户

        TODO 登陆用户名是支持哪些格式，手机号邮箱，普通用户名，限制是什么
        仅账号

        TODO 密码限制是什么
        6-20位同时包含数字英文，允许大小写英文和数字

        TODO 内部外部用户权限具体有哪些不同
        内部用户可以看全部的，能删除自己的，但是不能删除外部用户的信息，外部用户仅可查看和删除自己的

        """
    USER_TYPE_CHOICE = (
        (1, "内部用户"),
        (2, "外部用户")
    )
    username = models.CharField(help_text="用户名", max_length=32, unique=True)
    corporation = models.CharField(max_length=32, help_text="所属公司")

    industry = models.ForeignKey(DimIndustry, help_text="所属行业")
    category = models.ForeignKey(DimCategory, help_text="所属所属品类")
    brand = models.ForeignKey(DimBrand, help_text="所属品牌")

    is_active = models.BooleanField(help_text="是否可用", default=True)
    is_admin = models.BooleanField(help_text="是否是管理员", default=False)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICE, help_text="用户类型")
    role = models.ForeignKey(SmRole, help_text="角色", on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = "sm_user"

    def __str__(self):
        return self.username


class DimPlatform(models.Model):
    """
    渠道表
    """
    name = models.CharField(max_length=32, help_text="平台名称")
    parent = models.CharField(max_length=32, help_text="父平台名称")

    class Meta:
        db_table = "dim_platform"


class DimSalesPoint(models.Model):
    """
    宣传卖点 - 标签表
    """
    name = models.CharField(max_length=64, help_text="宣传卖点")
    category = models.ForeignKey(DimCategory, help_text="品类", on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = "dim_sales_point"


class Report(models.Model):
    STATUS_CHOICE = (
        (-1, "失败"),
        (0, "成功"),
        (1, "创建"),
        (2, "爬取中"),
        (3, "入库中"),
        (4, "计算中"),
        (5, "已取消"),
    )
    name = models.CharField(max_length=32, help_text="报告名称")
    user = models.ForeignKey(SmUser, help_text="所属用户", on_delete=models.DO_NOTHING)
    industry = models.ForeignKey(DimIndustry, help_text="行业", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=64, help_text="报告主题")
    tag = models.CharField(max_length=256, help_text="活动标签，逗号分隔")

    monitor_start_date = models.DateField(help_text="检测周期开始时间")
    monitor_end_date = models.DateField(help_text="检测周期结束时间")
    platform = models.CharField(max_length=64, help_text="渠道，逗号分隔")

    # industry = models.ForeignKey(DimIndustry, help_text="行业", on_delete=models.DO_NOTHING)
    brand = models.ForeignKey(DimBrand, help_text="品牌", on_delete=models.DO_NOTHING)
    category = models.ForeignKey(DimCategory, help_text="品类", on_delete=models.DO_NOTHING)
    product_line = models.CharField(max_length=32, help_text="产品线", null=True)

    accounts = models.TextField(help_text="投放账号, JSon格式", null=True)
    sales_point = models.ForeignKey(DimSalesPoint, help_text="宣传卖点", on_delete=models.DO_NOTHING)
    remark = models.CharField(max_length=128, help_text="备注")
    status = models.IntegerField(help_text="状态", choices=STATUS_CHOICE, default=1)
    data = models.TextField(help_text="报表数据，JSon格式", null=True)
    error_info = models.TextField(help_text="错误信息", null=True)
    delete = models.BooleanField(default=False, help_text="是否删除")
    create_time = models.DateTimeField(help_text="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(help_text="更新时间", null=True)

    class Meta:
        db_table = "report"


class APILog(models.Model):
    uri = models.CharField(max_length=64, help_text="访问 url")
    method = models.CharField(max_length=16, help_text="方法类型")
    user = models.CharField(max_length=32, blank=True, help_text="访问的用户")
    params = models.TextField(help_text="访问参数", blank=True)
    error_info = models.TextField(blank=True, help_text="错误信息")
    create_date = models.DateTimeField(help_text="访问时间")

    class Meta:
        db_table = "api_log"


# TODO 检测结束时间和检测周期什么关系
# 以检测周期的结束时间和当天的关系


# TODO 检测周期本身是什么范围 x个月以内怎么计算范围
# 发帖和回帖时间都在周期内
# 周期最长3个月
# 2019年1月1号是最早的起始日期


# TODO 关键字包含什么范围
# 报告名称 和 创建者


# 创建报告
# TODO 恢复默认恢复成什么内容  --  用户所属品牌，固定母婴行业，固定婴儿奶粉品类
# TODO 行业自己维护？  -- 母婴和医疗，不会再多
# TODO 品牌 品类 数据来源，客户上传，自己维护  -- 我们配置，客户购买可看的内容
# TODO 竞品和本品是否有关系，竞品数据来源  -- 无关系, 竞品也是需要购买查看
# TODO 活动标签是否要维护，用户自由操作吗？  -- 先不用
# TODO 投放账号的管理是否需要单独的页面  -- 加个隐藏的下载excel内容（非模板）
# TODO 投放账号默认数据是什么  -- 所有的(BGC) + 部分水军（待定）
# TODO 宣传卖点如何维护, 单选还是多选  -- 词库系统 - 品牌健康 , 单


# 报告详情
## 传播实况
# TODO 投放声量分布，活动和子活动怎么区分, 活动和子活动都要平级出来，还是按层级显示   -- 子活动 - 活动标签 ， 活动 - 报告
# TODO 投放账号分布是否要区分渠道（平台） 不分

## 传播效率
# TODO 是不是只看第一层转发  -- 是
# TODO 累计效率是什么  -- 累计传播广度和累计互动量
# TODO 评论账号是什么，需要维护吗  -- 原创帖的回帖， 不用维护

## 传播效率排行
# TODO 展示内容 -- 只展示互动量的KPI


## 传播效果
# TODO 活动期间UGC和活动UGC是不是一个定义  -- 活动期间UGC，活动范围内产生的所有UGC，包括活动UGC和品牌UGC  >  活动UGC， 活动投放贴下面所有的评论
# TODO 品牌UGC和活动期实际品牌UGC是不是相等  -- 是的
# TODO 品牌UGC移动年平均和年均品牌UGC是不是相同  -- 是的
##### 编辑解读 TODO 增加了是怎么比较的 -- 有活动期间UGC人数就是增加

## 品牌关注度
# TODO 年度品牌关注度和品牌UGC移动年平均算法是不是一致 -- 不是， 年度品牌关注度是一个值，移动年平均是52个值

## 爬虫相关
# TODO 年平均数据怎么抓取


"""
聚合结果为0时，是不出现在数据里的，需要后端补全, 也可能出现长度为0的列表
"""
RDL_JSON = dict(
    # 1. 传播实况
    spread_overview=dict(
        # 1.1. 投放声量总计
        post_count=124,

        # 1.2. 投放账号数总计
        account_count=33,

        # 1.3. 投放声量分布
        activity=[
            # 报告内所有子活动的投放声量
            dict(name="抗敏大挑战", value=48),
            dict(name="get过敏小知识", value=41),
            dict(name="换季过敏", value=35)
        ],

        # 1.4. 投放渠道分布
        platform=dict(
            # 微博投放声量数
            weibo=120,

            # 母垂投放声量数
            motherbaby=[

                # 母锤投放具体到各个平台
                dict(name="宝宝树", value=3),
                dict(name="辣妈帮", value=1)
            ]
        ),

        # 1.5. 投放账号分布
        account=[
            # 账号、所属平台、账号投放声量总计
            dict(account="张三", platform="微博", post_count=33, user_type="BGC"),
            dict(account="Edward", platform="宝宝树", post_count=2, user_type="KOL"),
            dict(account="李四", platform="辣妈帮", post_count=1, user_type="水军"),
            dict(account="李四", platform="辣妈帮", post_count=1, user_type="水军"),
            dict(account="王五", platform="辣妈帮", post_count=1, user_type="水军"),
            dict(account="张柳", platform="宝宝树", post_count=1, user_type="水军"),
        ],

        # 1.6. 投放声量趋势及账号趋势
        trend=[
            # 由于count可以直接相加，所以数据格式固定是按天给，如果要转换成按周，需要再次聚合
            dict(date="2019-01-01", post_count=55, account_count=12),
            dict(date="2019-01-02", post_count=51, account_count=9),
            dict(date="2019-01-03", post_count=59, account_count=13),
            dict(date="2019-01-04", post_count=45, account_count=6)
        ]
    ),

    # 2. 活动传播效率
    spread_efficiency=dict(
        # 2.1. 平台效率 - 累计传播效率
        platform_cumulative=[
            # 分别表示 累计传播广度, 累计互动量, 平台, 投放声量, 评论数，点赞数，转发数，阅读数，粉丝数
            dict(breadth=10, interaction=50, name="微博", value=100, reply_count=32, like_count=23, transimit_count=34, view_count=45, fans_count=54),
            dict(breadth=30, interaction=20, name="宝宝树", value=10)
        ],

        # 2.2. 平台效率 - 单位传播效率
        platform_average=[
            # 分别表示 单位传播广度, 单位互动量, 平台, 投放声量
            dict(breadth=10, interaction=50, name="微博", value=100),
            dict(breadth=30, interaction=20, name="宝宝树", value=10)
        ],

        # 2.3. 账号效率 - 单位传播效率
        account_cumulative=[
            # 分别表示 累计传播广度, 累计互动量, 账号, 平台, 投放声量
            dict(breadth=5, interaction=18, name="张三", platform="微博", value=100, reply_count=32, like_count=23, transimit_count=34, view_count=45, fans_count=54),
            dict(breadth=30, interaction=20, name="王五", platform="宝宝树", value=10)
        ],

        # 2.4. 账号效率 - 单位传播效率
        account_average=[
            # 分别表示 单位传播广度, 单位互动量, 账号, 平台, 投放声量
            dict(breadth=5, interaction=18, name="张三", platform="微博", value=100),
            dict(breadth=30, interaction=20, name="王五", platform="宝宝树", value=10)
        ],

        # 2.5. 子活动效率 - 单位传播效率
        activity_cumulative=[
            # 分别表示 累计传播广度, 累计互动量, 账号, 子活动, 投放声量
            dict(breadth=50, interaction=33, name="张三", platform="微博", value=100, reply_count=32, like_count=23, transimit_count=34, view_count=45, fans_count=54),
            dict(breadth=30, interaction=99, name="王五", platform="宝宝树", value=10)
        ],

        # 2.6. 子活动效率 - 单位传播效率
        activity_average=[
            # 分别表示 单位传播广度, 单位互动量, 账号, 子活动, 投放声量
            dict(breadth=5, interaction=33, name="张三", platform="微博", value=100),
            dict(breadth=30, interaction=99, name="王五", platform="宝宝树", value=10)
        ],

        # 2.7. 互动量来源
        activity_composition=[
            dict(name="转发", value=60),
            dict(name="评论", value=21),
            dict(name="点赞", value=43)
        ],

        # 2.8. 评论账号分布
        user_type_composition=[
            dict(name="BGC", value=20),
            dict(name="KOL", value=7),
            dict(name="水军", value=14),
        ]
    ),

    # 3. 传播效率排行
    spread_efficiency_rank=dict(
        # 3.1. 文章
        article=[
            # 分别是 文本内容, 来源平台, 转发数, 评论数, 点赞数, 如果该平台没有相应的字段，值为None
            dict(content="文章1", platform="微博", transmit_count=1, reply_count=2, like_count=3),
            dict(content="文章2", platform="宝宝树", transmit_count=None, reply_count=2, like_count=None),
        ],

        # 3.2. KOL
        kol=[
            # 分别是 KOL用户名, 来源平台, 发帖数, 贴均互动量, 贴均传播广度
            dict(nick_name="用户1", platform="微博", post_count=1, interaction_per_post=412.3, breadth_per_post=11.1),
            dict(nick_name="用户2", platform="宝宝树", post_count=1, interaction_per_post=412.3, breadth_per_post=11.1),
        ]
    ),

    # 4. 传播效果
    spread_effectiveness=dict(
        # 4.1. 活动期间UGC总计
        ugc_count=200,

        # 4.2. 活动UGC
        ugc_in_activity_count=135,

        # 4.3. 品牌UGC
        ugc_mentioned_brand_count=136,

        # 4.2 - 4.3 补充 活动UGC & 品牌UGC
        ugc_intersect_count=35,

        # 4.4. 活动UGC构成
        ugc_in_activity_composition=[
            dict(name="提及品牌", value=120),
            dict(name="未提及品牌", value=15)
        ],

        # 4.5. 子活动UGC构成
        activity_ugc_in_activity_composition=[
            # 图中一根柱子里的数据由两行数据表示
            dict(name="敏事大挑战", value=30, type="提及品牌"),
            dict(name="敏事大挑战", value=70, type="未提及品牌"),
        ],

        # 4.6 活动对品牌UGC的贡献
        # 4.6.1 活动期预测UGC
        predict=232,

        # 4.6.2 浮动绝对值
        delta_absolute=-97,

        # 4.6.3 浮动比例
        delta=-0.42,

        # 4.6.4 年均品牌UGC
        annual_average_trend=[
            dict(value=20, date="2019-01-07"),
            dict(value=30, date="2019-01-14")
        ],
        # 4.6.5 实际品牌UGC
        brand_ugc_trend=[
            dict(value=20, date="2019-01-07"),
            dict(value=30, date="2019-01-14")
        ]
    ),

    # 5. 品牌关注度
    brand_concern=dict(
        # 5.1. 浮动
        delta=0.1,

        # 5.2. 活动期实际品牌关注度
        activity=0.15,

        # 5.3. 年度品牌关注度
        annual=0.05,

        # 5.4. 趋势图
        trend=[
            dict(value=20, date="2019-01-07"),
            dict(value=30, date="2019-01-14")
        ],
    ),

    # 6. 宣传卖点认知度
    tags_concern=dict(
        # 6.1. 浮动
        delta=0.1,

        # 6.2. 活动期"过敏"认识度
        activity=0.15,

        # 6.3. 年度"过敏"认识度
        annual=0.05,

        # 6.4. 年度趋势图
        trend=[
            # 年度品牌关注度是常量，可以将annual填入，一周一行数据
            dict(value=20, date="2019-01-07"),
            dict(value=30, date="2019-01-14")
        ]
    )
)
