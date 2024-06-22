#!usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time


class Config:
    def __init__(
            self, do_train=True, do_predict=True, batch_size=64, epoch=20,
            do_log_print_to_screen=True, do_log_save_to_file=True,
    ):
        # 数据参数
        self.feature_columns = list(range(2, 9))  # 要作为feature的列，按原数据从0开始计算，也可以用list
        self.label_columns = [4, 5]  # 要预测的列，按原数据从0开始计算, 如同时预测第四，五列 最低价和最高价
        self.label_in_feature_index = (lambda x, y: [x.index(i) for i in y])(self.feature_columns, self.label_columns)
        self.predict_day = 1  # 预测未来几天的窗口

        # 网络参数
        self.input_size = len(self.feature_columns)
        self.output_size = len(self.label_columns)
        self.hidden_size = 128  # LSTM的隐藏层大小，也是输出大小
        self.lstm_layers = 2  # LSTM的堆叠层数
        self.dropout_rate = 0.2  # dropout概率
        self.time_step = 20  # 设置用前多少天的数据来预测，也是LSTM的time step数，训练数据量需大于它

        # 训练参数
        self.do_train = do_train
        self.do_predict = do_predict
        self.add_train = False  # 是否载入已有模型参数进行增量训练
        self.shuffle_train_data = True  # 是否对训练数据做shuffle
        self.use_cuda = False  # 是否使用GPU训练
        self.train_data_rate = 0.95  # 训练数据占总体数据比例，测试数据就是 1-train_data_rate
        self.valid_data_rate = 0.15  # 验证数据占训练数据比例，验证集在训练过程使用，为了做模型和参数选择
        self.batch_size = batch_size
        self.learning_rate = 0.001
        self.epoch = epoch  # 整个训练集被训练多少遍，不考虑早停的前提下
        self.patience = 5  # 训练多少epoch，验证集没提升就停掉
        self.random_seed = 42  # 随机种子，保证可复现
        self.do_continue_train = False  # 每次训练把上一次的final_state作为下一次的init_state，仅用于RNN类型模型
        self.continue_flag = ""  # 但实际效果不佳，可能原因：仅能以 batch_size = 1 训练
        if self.do_continue_train:
            self.shuffle_train_data = False
            self.batch_size = 1
            self.continue_flag = "continue_"

        # 训练模式
        self.debug_mode = False
        self.debug_num = 500  # 调试数据条数

        # 路径、日志参数
        self.train_data_path = "./data/crawl_rst/stock_data.csv"
        self.model_save_path = f"./data/checkpoint/"
        self.model_name = f"{self.continue_flag}model.pth"
        self.figure_save_path = "./data/figure/"
        self.log_save_path = "./log/"
        self.do_log_print_to_screen = do_log_print_to_screen
        self.do_log_save_to_file = do_log_save_to_file
        self.do_save_figure = True
        self.do_train_visualized = False
        # 创建路径
        if not os.path.exists(self.model_save_path):
            os.makedirs(self.model_save_path)
        if not os.path.exists(self.figure_save_path):
            os.mkdir(self.figure_save_path)
        if self.do_log_save_to_file or self.do_train_visualized:
            cur_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            self.log_save_path = f"{self.log_save_path}{cur_time}/"
            os.makedirs(self.log_save_path)

    def __str__(self):
        config_dict = {}
        for key in dir(self):
            if not key.startswith("_"):
                config_dict[key] = getattr(self, key)
        config_str = str(config_dict)
        config_list = config_str[1:-1].split(", '")
        config_str = "\nConfig:\n" + "\n'".join(config_list)
        return config_str
