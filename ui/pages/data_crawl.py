#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import streamlit as st

from src import (
    load_logger_st,
    crawl_all_categories,
    crawl_stock_dailyk,
)
from src.crawlers.crawl_category_stocks_dailyk import crawl_category_stocks


st.set_page_config(layout="wide")

SIDE_TOC_STYLE = f'''class="side-toc" style="
  text-decoration: none;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  -moz-box-align: center;
  align-items: center;
  gap: 0.5rem;
  border-radius: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  margin: 0.5rem 0;
  line-height: 2;
  text-decoration: none;
  color: rgb(32, 32, 32);
"'''

sidebar_content = """
<style>
  .side-toc:hover {
    color: rgb(255, 75, 75) !important;
  }
</style>
""" + f"""
<a href="#crawlers" {SIDE_TOC_STYLE}><b>数据爬取</b></a>
<a href="#all_categories" {SIDE_TOC_STYLE}>爬取沪深京所有板块</a>
<a href="#all_data" {SIDE_TOC_STYLE}>爬取指定板块所有股票日K数据</a>
<a href="#one_data" {SIDE_TOC_STYLE}>爬取指定股票日K数据</a>
"""
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)


# 页面内容
st.title("数据爬取", anchor="crawlers")

st.subheader("爬取沪深京所有板块", anchor="all_categories")
type_dict = {1: "地域", 2: "行业", 3: "概念"}
category_type, sort_order, sort_key = st.columns(3)
category_type = category_type.selectbox(
    "选择板块类型", options=[1, 2, 3],
    format_func=lambda x: type_dict[x]
)
sort_order = sort_order.selectbox(
    "选择排序方式", options=[1, 0],
    format_func=lambda x: {1: "降序", 0: "升序"}[x]
)
sort_key = sort_key.selectbox(
    "选择排序关键字", options=[2, 3, 4, 8, 20],
    format_func=lambda x: {2: "最新价", 3: "涨跌幅", 4: "涨跌额", 8: "换手率", 20: "总市值"}[x]
)
crawl_category_button = st.button("**爬取沪深京所有板块**", use_container_width=True)

if crawl_category_button:
    crawl_category_df_expander = st.expander(expanded=True, label=f"#### 沪深京所有{type_dict[category_type]}板块")
    crawl_category_df_placeholder = crawl_category_df_expander.empty()
    df = crawl_all_categories(
        category_type=category_type,
        sort_order=sort_order,
        sort_key=sort_key
    )
    crawl_category_df_placeholder.write(df)

    # 保存为csv文件
    save_dir = f"data/crawl_rst/category_data/"
    save_path = save_dir + f"{type_dict[category_type]}板块数据.csv"
    if not os.path.exists(save_dir) and not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    df.to_csv(save_path, index=False)


st.subheader("爬取指定板块所有股票日K数据", anchor="all_data")

category_code, crawl_all_stocks = st.columns(2)
category_code = category_code.text_input("输入板块代码", value="0420")
crawl_all_stocks = crawl_all_stocks.checkbox("是否爬取所有股票", value=False)
crawl_category_stocks_button = st.button("**爬取指定板块所有股票日K数据**", use_container_width=True)

if crawl_category_stocks_button:
    category_stocks_expander = st.expander(expanded=True, label=f"#### 板块代码: {category_code} 的所有股票日K数据")
    category_stocks_df_placeholder = category_stocks_expander.empty()

    # 设置日志
    category_log_placeholder = category_stocks_expander.empty()
    logger = load_logger_st(category_log_placeholder)

    # 爬取指定板块所有股票日K数据
    df_category = crawl_category_stocks(
        category_code=category_code,
        crawl_all=crawl_all_stocks,
        logger=logger
    )
    if df_category is not None:
        category_stocks_df_placeholder.write(df_category)
    else:
        category_stocks_df_placeholder.write("没有爬取到任何数据，或数据爬取失败。")


st.subheader("爬取指定股票日K数据", anchor="one_data")
stock_code, stock_exchange, fq = st.columns(3)
stock_code = stock_code.text_input("输入股票代码", value="000001")
stock_exchange = stock_exchange.selectbox(
    "选择交易所", options=['0', '1'],
    format_func=lambda x: {'1': "沪市", '0': "深市/北证"}[x]
)
fq = fq.selectbox(
    "选择复权类型", options=["1", "2"],
    format_func=lambda x: {"1": "前复权", "2": "后复权"}[x]
)
start_date, end_date, _ = st.columns(3)
start_date = start_date.date_input("开始日期", value=datetime(1900, 1, 1))
end_date = end_date.date_input("结束日期", value=datetime.now())
crawl_stock_dailyk_button = st.button("**爬取指定股票日K数据**", use_container_width=True)

if crawl_stock_dailyk_button:
    stock_dailyk_expander = st.expander(expanded=True, label=f"#### 股票代码: {stock_code} 的日K数据")
    stock_dailyk_df_placeholder = stock_dailyk_expander.empty()

    # 设置日志
    stock_log_placeholder = stock_dailyk_expander.empty()
    logger = load_logger_st(stock_log_placeholder)

    # 爬取指定股票日K数据
    df_stock = crawl_stock_dailyk(
        stock_code=stock_code,
        stock_exchange=stock_exchange,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        fq=fq,
        logger=logger
    )
    if df_stock is not None:
        stock_dailyk_df_placeholder.write(df_stock)
    else:
        stock_dailyk_df_placeholder.write("没有爬取到任何数据，或数据爬取失败。")

    # 保存为csv文件
    save_dir = f"data/crawl_rst/daily_kline/"
    save_path = save_dir + f"{stock_code}.csv"
    if not os.path.exists(save_dir) and not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    df_stock.to_csv(save_path, index=False)
    logger.info(f"数据已保存到 {save_path}。")
