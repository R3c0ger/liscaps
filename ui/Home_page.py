#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import streamlit as st
from st_pages import Page, show_pages

st.set_page_config(layout="wide")  # 撑满页面，必须在第一句

show_pages(
    [
        Page("ui/home_page.py", "Home", ":house_with_garden:"),
        Page("ui/pages/data_crawl.py", "Data_Crawl", ":mag:"),
        Page("ui/pages/prediction.py", "Prediction", ":chart_with_upwards_trend:"),
        Page("ui/pages/prediction_svm.py", "Prediction_With_SVM", ":chart_with_upwards_trend:"),
    ]
)

# 从根目录导入 main.py 中的全局变量
ui_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(ui_dir)
root = os.path.dirname(src_dir)
sys.path.append(root)
main = __import__('main')

st.title(main.TITLE_CN)
st.write(f"Version: {main.VERSION}")
