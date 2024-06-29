#!usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from prediction import *
from utils import load_logger


def run_train_predict(config=None, _logger=None):
    if not config:
        config = Config()
    if not _logger:
        _logger = load_logger(config)
    try:
        np.random.seed(config.random_seed)  # 设置随机种子，保证可复现
        data_gainer = Data(config)

        if config.do_train:
            train_x, valid_x, train_y, valid_y = data_gainer.get_train_and_valid_data()
            train(config, _logger, [train_x, train_y, valid_x, valid_y])

        if config.do_predict:
            test_x, test_y = data_gainer.get_test_data(return_label_data=True)
            pred_result = predict(config, test_x)  # 输出未还原的归一化预测数据
            display_prediction(config, data_gainer, _logger, pred_result)
    except Exception as e:
        _logger.error(f"Run Error: {e}", exc_info=True)


def run_train_predict_svm(config=None, logger=None):
    if not config:
        config = Config()
    if not logger:
        logger = load_logger(config)
    try:
        np.random.seed(config.random_seed)  # 设置随机种子，保证可复现
        data_gainer = Data(config)

        if config.do_train:
            train_x, valid_x, train_y, valid_y = data_gainer.get_train_and_valid_data()
            train_svm(config, logger, [train_x, train_y, valid_x, valid_y])

        if config.do_predict:
            test_x, test_y = data_gainer.get_test_data(return_label_data=True)
            pred_result = predict_svm(config, test_x)  # 输出未还原的归一化预测数据
            display_prediction(config, data_gainer, logger, pred_result)
    except Exception as e:
        logger.error(f"Run Error: {e}", exc_info=True)


if __name__ == '__main__':
    # run_train_predict()
    run_train_predict_svm()
