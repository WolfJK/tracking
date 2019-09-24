# coding: utf-8
# __author__: ""
from __future__ import unicode_literals


unscramble_rule = dict(
    transmission=dict(
        unscramble=[
            ("1", "本次活动共投放{post_count}篇帖子，启用{account_all}个账号。\n "),
            ("{activity_count} > 1", "{activity_max}主题活动投放声量最高（{activity_post_count}篇）；"),
            ("1", "活动主要在{platform_max}平台投放，共投放{platform_post_count}篇帖子，约占总投放声量的{platform_max_ratio}%。\n"),
            ("'{account_max}' == '{account_post_max}'", "从账号分布来看，{account_max}账号数量最多（{account_count}个），发布的帖子数也最多（{account_post_count}篇）\n"),
            ("'{account_max}' != '{account_post_max}'", "从账号分布来看，{account_max}账号数量最多（{account_count}个），而{account_post_max}账号发布帖子数最多（{account_post_count}篇）\n"),
        ],
        user=None,
        date=None,
    ),

    efficiency=dict(
        unscramble=[
            ("{platform_count} > 1 and '{cb_platform_max}' != '{hd_platform_max}'", "从平台角度看，本次活动在{cb_platform_max}的累计传播广度最高（{cb_platform_count}人次），而在{hd_platform_max}引发了最高的累计互动量（{hd_platform_count}人次）\n"),
            ("{platform_count} > 1 and '{cb_platform_max}' == '{hd_platform_max}'", "从平台角度看，本次活动在{cb_platform_max}引发了最高的累计互动量（{hd_platform_count}人次）和最高的累计传播广度（{cb_platform_count}人次）\n"),
            ("{platform_count} == 1", "本次活动累计互动量{hd_platform_count}人次，累计传播广度{cb_platform_count}人次 \n"),
            ("'{hd_account_max}' != '{cb_account_max}'", "从账号角度看，{cb_account_max}的发帖累计传播广度最高（{cb_account_count}人次），而{hd_account_max}的发帖引发了最高的累计互动量（{hd_account_count}人次） \n"),
            ("'{hd_account_max}' == '{cb_account_max}'", "从账号角度看，{cb_account_max}的发帖累计传播广度最高（{cb_account_count}人次），且引发了最高的累计互动量（{hd_account_count}人次）\n"),
            ("'{hd_activity_max}' != '{cb_activity_max}'", "从子活动角度看，“{cb_activity_max}”累计传播广度最高（{cb_activity_count}人次），而“{hd_activity_max}”引发了最高的累计互动量（{hd_activity_count}人次）\n"),
            ("'{hd_activity_max}' == '{cb_activity_max}'", "从子活动角度看，“{cb_activity_max}”累计传播广度最高（{cb_activity_count}人次），且引发了最高的累计互动量（{hd_activity_count}人次）\n"),
            ("1", "互动大部分来源于{source_max}，约占整体的{source_ratio}%；评论中{account_comment_max}账号的占比最高，约为{account_comment_ratio}%。\n"),
        ],
        user=None,
        date=None,
    ),

    effect_ugc=dict(
            unscramble=[
                ("{activity_count} > 1", "本次活动期间UGC总计{ugc_count}人，其中活动UGC{activitys_ugc_count}人，品牌UGC{brands_ugc_count}人。\n"),
                ("1", "活动UGC中有{activitys_brand_ugc_count}人（{activitys_brand_ugc_ratio}%）提及品牌名称，增加了品牌声量；以#{activity_ugc_max}# 为主题的子活动引发的UGC人数最多，达{activity_ugc_count}个。\n"),
                ("{activitys_ugc_count} < {brand_ugc_pre_count}", "活动期内总计产生品牌UGC{activitys_ugc_count}人。基于过往一年历史数据的预测，活动期内品牌UGC应该可以达到{brand_ugc_pre_count}，相差{brand_ugc_diff_count}人（-{brand_ugc_diff_ratio}%），没有达到预期效果\n"),
                ("{activitys_ugc_count} >= {brand_ugc_pre_count}", "活动期内总计产生品牌UGC{activitys_ugc_count}人。基于过往一年历史数据的预测，活动期内品牌UGC可以达到{brand_ugc_pre_count}人，活动为品牌贡献了{brand_ugc_diff_count}个（{brand_ugc_diff_ratio}%）UGC，超出预期效果\n"),
            ],
            user=None,
            date=None,
    ),

    effect_brand=dict(
        unscramble=[
            ("{brand_attention} > {brand_attention_year}", "活动期间内品牌关注度达{brand_attention}%，较年度关注度提升{brand_attention_ratio}%。\n"),
            ("{brand_attention} < {brand_attention_year}", "活动期间内品牌关注度达{brand_attention}%，较年度关注度下降{brand_attention_ratio}%。\n"),
        ],
        user=None,
        date=None,
    ),

    effect_sales_point=dict(
        unscramble=[
            ("{sales_point_cognitive} > {sales_point_cognitive_year}", "活动期内用户对于宣传卖点——“{sales_point}”的认知度为{sales_point_cognitive}%，较年度“{sales_point}”认知度提升{sales_point_cognitive_ratio}%\n"),
            ("{sales_point_cognitive} < {sales_point_cognitive_year}", "活动期内用户对于宣传卖点——“{sales_point}”的认知度为{sales_point_cognitive}%，较年度“{sales_point}”认知度下降{sales_point_cognitive_ratio}%\n"),
        ],
        user=None,
        date=None,
    ),
)