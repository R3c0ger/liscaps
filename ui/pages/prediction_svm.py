#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import streamlit as st

from src import run_train_predict_svm, load_logger_st, Config


st.set_page_config(layout="wide")

st.write("# 使用SVM预测股票价格")

st.write("## 训练和预测配置")
do_train, do_predict = st.columns(2)
do_train = do_train.checkbox("训练", value=True)
do_predict = do_predict.checkbox("预测", value=True)
batch_size, epoch = st.columns(2)
batch_size = batch_size.number_input("批次大小（Batch Size）", value=64)
epoch = epoch.number_input("训练轮数（Epochs）", value=20)
run_svm_button = st.button("运行SVM训练和预测")

if run_svm_button:
    # 设置日志和图片显示区域
    log_expander = st.expander(expanded=True, label="SVM训练日志")
    log_placeholder = log_expander.empty()
    image_placeholder_low, image_placeholder_high = st.columns(2)
    logger = load_logger_st(log_placeholder)

    conf = Config(do_train, do_predict, batch_size, epoch)  # 初始化配置
    run_train_predict_svm(conf)  # 运行训练和预测

    # 展示预测图片
    if do_predict:
        time.sleep(0.5)
        figure_save_path = conf.figure_save_path
        image_path_low = os.path.join(figure_save_path, f"predict_low.png")
        image_path_high = os.path.join(figure_save_path, f"predict_high.png")
        if os.path.exists(image_path_low):
            image_placeholder_low.image(image_path_low, caption="预测低价")
        if os.path.exists(image_path_high):
            image_placeholder_high.image(image_path_high, caption="预测高价")
