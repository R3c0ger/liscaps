#!usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import os
import sys


st.set_page_config(layout="wide")  # 撑满页面，必须在第一句

# 从根目录导入 main.py 中的全局变量
ui_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(ui_dir)
root = os.path.dirname(src_dir)
sys.path.append(root)
main = __import__('main')

st.title(main.TITLE_CN)
st.write(f"Version: {main.VERSION}")
