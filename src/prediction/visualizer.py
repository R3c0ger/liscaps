#!usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import matplotlib.pyplot as plt
import numpy as np

from src.prediction.config import Config
from src.prediction.data_processor import Data


def display_prediction(
        config: Config,
        origin_data: Data,
        logger,
        predict_norm_data: np.ndarray
):
    label_data = origin_data.data[
        origin_data.train_num + origin_data.start_num_in_test:,
        config.label_in_feature_index
    ]
    # 通过保存的均值和方差还原数据
    predict_data = predict_norm_data * origin_data.std[config.label_in_feature_index] \
        + origin_data.mean[config.label_in_feature_index]
    assert label_data.shape[0] == predict_data.shape[0], \
        "The element number in origin and predicted data is different."

    label_name = [origin_data.data_column_name[i] for i in config.label_in_feature_index]
    label_column_num = len(config.label_columns)

    # label 和 predict 是错开config.predict_day天的数据的
    # 下面是两种norm后的loss的计算方式，结果是一样的，可以简单手推一下
    # label_norm_data = origin_data.norm_data[origin_data.train_num + origin_data.start_num_in_test:,
    #              config.label_in_feature_index]
    # loss_norm = np.mean((label_norm_data[config.predict_day:] - predict_norm_data[:-config.predict_day]) ** 2, axis=0)
    # logger.info("The mean squared error of stock {} is ".format(label_name) + str(loss_norm))

    loss = np.mean((label_data[config.predict_day:] - predict_data[:-config.predict_day]) ** 2, axis=0)
    loss_norm = loss / (origin_data.std[config.label_in_feature_index] ** 2)
    logger.info(f"The mean squared error of stock {label_name} is {str(loss_norm)}.")

    label_x = range(origin_data.data_num - origin_data.train_num - origin_data.start_num_in_test)
    predict_x = [x + config.predict_day for x in label_x]

    # 无桌面的Linux下无法输出，如果是有桌面的Linux，如Ubuntu，可去掉这部分判断
    if sys.platform.startswith('linux'):
        return

    img_pil_list = []
    for i in range(label_column_num):
        plt.figure(i+1)  # 预测数据绘制
        plt.plot(label_x, label_data[:, i], label='label')
        plt.plot(predict_x, predict_data[:, i], label='predict')
        plt.legend()
        plt.title(f"Predict stock {label_name[i]} price")
        logger.info(
            f"The predicted stock {label_name[i]} for the next {config.predict_day} day(s) is: "
            f"{np.squeeze(predict_data[-config.predict_day:, i])}"
        )
        if config.do_save_figure:
            plt.savefig(f"{config.figure_save_path}{config.continue_flag}"
                        f"predict_{label_name[i]}.png")
            logger.info(f"Save predict figure of {label_name[i]} successfully.")
        img_pil_list.append(plt)
    plt.show()
    return img_pil_list
