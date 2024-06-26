#!usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pandas as pd
import requests

from src.crawlers.crawl_stock_dailyk import crawl_stock_dailyk


def crawl_category_stocks(category_code, crawl_all=False, logger=None):
    """
    获取指定行业/概念/地域板块内所有股票的代码。
    :param category_code: 行业/概念/地域板块代码，如'0447'（互联网服务）、'0918'（特高压）
    :param crawl_all: 是否爬取所有股票的数据，默认为False
    :param logger: 日志对象
    :return: 行业/概念/地域板块内所有股票的代码列表
    """
    # pn: 页码；pz: 每页数量；po: 排序方式(0: 正序，1: 倒序)；fid: 排序字段
    base_url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1000&po=0&np=1&fltt=2&invt=2&fid=f12&"
    # fs: 股票筛选条件；bk: 板块代码
    fs = f"fs=b:BK{category_code}&"
    # fields: 返回字段；f12: 股票代码；f13: 交易所，0为深证，1为上证；f14: 股票名称；f100: 行业；f102: 地域；f103: 概念
    fields = "fields=f12,f13,f14,f100,f102,f103"
    url = base_url + fs + fields
    logger.info(f"请求API URL: {url}")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    stocks = data['data']['diff']
    stocks_all_info = [list(stock.values()) for stock in stocks]
    # 股票代码开头900、200为B股，5位为H股，需要排除
    stocks_all_info = [stock for stock in stocks_all_info if
                       not stock[0].startswith(('900', '200')) and len(stock[0]) == 6]
    stock_codes = [stock[0] for stock in stocks_all_info]  # 股票代码

    # 将数据转换为dataframe
    stocks_all_df = pd.DataFrame(
        stocks_all_info,
        columns=['股票代码', '交易所', '股票名称', '行业', '地域', '概念']
    )
    if not crawl_all:
        return stocks_all_df

    # 收集股票信息，爬取所有股票的数据
    stock_exchanges = [stock[1] for stock in stocks_all_info]  # 交易所
    stock_info = [[stock[3], stock[4], stock[5]] for stock in stocks_all_info]  # 行业、地域、概念
    len_stock_codes = len(stock_codes)

    stock_dfs = []
    for i in range(len_stock_codes):
        logger.info(f"[{i + 1}/{len_stock_codes}]")
        stock_df = crawl_stock_dailyk(
            stock_codes[i],
            stock_exchange=stock_exchanges[i],
            other_info=stock_info[i],
            logger=logger
        )
        stock_dfs.append(stock_df)
    folder_name = f"data/crawl_rst/kline_data/BK{category_code}_kline_data"
    if not os.path.exists(folder_name) and not os.path.isdir(folder_name):
        os.makedirs(folder_name)
    for i, stock_code in enumerate(stock_codes):
        stock_dfs[i].to_csv(f"{folder_name}/{stock_code}.csv", index=False)
    return stocks_all_df


if __name__ == '__main__':
    industry = "0447"  # 互联网服务
    crawl_category_stocks(industry, crawl_all=True)
