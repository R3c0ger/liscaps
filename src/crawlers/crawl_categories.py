#!usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import requests


def crawl_all_categories(category_type=3, sort_order=1, sort_key=3):
    """爬取所有沪深京板块
    :param category_type: 板块类型，1:地域，2:行业，3:概念
    :param sort_order: 排序方式，1:降序，0:升序
    :param sort_key: 排序关键字，3:涨跌幅
    """
    base_url = r'https://push2.eastmoney.com/api/qt/clist/get?&pn=1&pz=5000&'
    args = rf'po={sort_order}&np=1&fltt=2&fid=f{sort_key}&fs=m:90+t:{category_type}+f:!50&'
    # f2:最新价，f3:涨跌幅，f4:涨跌额，f12:板块代码，f14:板块中文名，f20:总市值，
    # f8:换手率，f104:上涨家数，f105:下跌家数，f128:领涨股票，f140:领涨股票代码
    fields = r'fields=f2,f3,f4,f8,f12,f14,f20,f104,f105,f128,f140'
    url = base_url + args + fields
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    data = data['data']['diff']
    df = pd.DataFrame(data)
    df = df.rename(columns={
        'f12': '板块代码',
        'f14': '板块中文名',
        'f2': '最新价',
        'f3': '涨跌幅(%)',
        'f4': '涨跌额',
        'f20': '总市值(亿)',
        'f8': '换手率(%)',
        'f104': '上涨家数',
        'f105': '下跌家数',
        'f128': '领涨股票',
        'f140': '领涨股票代码'
    })

    return df
