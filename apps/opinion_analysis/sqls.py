# coding: utf-8
# __author__: ""
from __future__ import unicode_literals


compete_brand = """
select competitors from sm_competitor where json_index(brand, -1, '.id') = {brand_id};
"""