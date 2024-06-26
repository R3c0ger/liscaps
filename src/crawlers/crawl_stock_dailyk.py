#!usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import pandas as pd
import requests


def crawl_stock_dailyk(
        stock_code,
        stock_exchange='1',
        start_date='19900101',
        end_date=None,
        fq="1",
        other_info=None,
        logger=None,
):
    """爬取指定股票日K数据
    :param stock_code: 股票代码
    :param stock_exchange: 交易所代码，1为沪市，0为深市和北证，默认为1
    :param start_date: 开始日期，字符串格式，默认为'19900101'
    :param end_date: 结束日期，字符串格式，默认为当前日期
    :param fq: 复权类型，1为前复权，2为后复权，默认为1
    :param other_info: 其他信息，行业、地域、概念，如提供则会保存到csv文件中
    :param logger: 日志对象
    :return: 包含历史K线数据的DataFrame
    """
    if end_date is None:  # 如果未指定结束日期，则默认为今天
        end_date = datetime.now().strftime('%Y%m%d')
    logger.info(f"Fetching data from {start_date} to {end_date} for stock {stock_code}...")
    # 所需字段
    columns = [
        '股票代码', '股票名称', '日期', '开盘价', '收盘价', '最高价', '最低价',
        '成交量', '成交额', '振幅(%)', '涨跌幅(%)', '涨跌额', '换手率(%)',
    ]
    if other_info is not None:
        columns += ['行业', '地域', '概念', ]

    # 请求API获取部分数据
    base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
    # secid字段：0.代表沪市，1.代表深市；.后面跟随股票代码
    secid_fields1 = f"secid={stock_exchange}.{stock_code}&fields1=f1,f2,f3,f4,f5,f6&"
    # fields2字段：f51: 日期；f52: 开盘价；f53: 收盘价；f54: 最高价；f55: 最低价；
    #   f56: 成交量；f57: 成交额；f58: 振幅；f59: 涨跌幅；f60: 涨跌额；f61: 换手率；
    fields2 = "fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
    # klt字段：101代表日K线，102代表周K线，103代表月K线；fqt字段：1代表前复权，2代表后复权；beg和end字段：开始和结束日期
    klt_fqt_beg_end = f"klt=101&fqt={fq}&beg={start_date}&end={end_date}"
    url_api = base_url + secid_fields1 + fields2 + klt_fqt_beg_end
    logger.info(f"API URL: {url_api}")
    response = requests.get(url_api)
    response.raise_for_status()
    data = response.json()

    # 解析数据
    data = data['data']
    try:
        klines = data['klines']
    except TypeError:
        logger.error(f"Failed to fetch data for stock {stock_code}. "
                     f"Please check your input or choices.")
        return None
    klines = [line.split(',') for line in klines]
    df = pd.DataFrame(klines, columns=columns[2:])
    df['股票代码'] = stock_code
    df['股票名称'] = data['name']
    df = df[['股票代码', '股票名称'] + columns[2:]]
    if other_info is not None:
        df['行业'] = other_info['行业']
        df['地域'] = other_info['地域']
        df['概念'] = other_info['概念']

    return df



