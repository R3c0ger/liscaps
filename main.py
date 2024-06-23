#!usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

PROJECT_NAME = "Liscaps"
TITLE_CN = f"{PROJECT_NAME.upper()}：基于 LSTM 的智能股票爬取分析与预测系统"
TITLE_EN = f"{PROJECT_NAME.upper()}: LSTM-based Intelligent Stock Crawl, Analysis and Prediction System"
VERSION = "0.1.0"


if __name__ == "__main__":
    subprocess.run(["streamlit", "run", r".\ui\home_page.py"])
    sys.exit(0)
