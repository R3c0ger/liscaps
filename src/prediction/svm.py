#!usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
import joblib


class SVMModel:
    """SVM预测模型"""
    def __init__(self, config):
        self.config = config
        self.model = SVR(kernel='rbf', C=config.svm_C, gamma=config.svm_gamma)

    def train(self, train_x, train_y):
        train_x = train_x.reshape(-1, train_x.shape[-1])  # 展平
        train_y = train_y.flatten()
        self.model.fit(train_x, train_y)
        joblib.dump(self.model, self.config.model_save_path + self.config.model_name)

    def predict(self, test_x):
        test_x = test_x.reshape(-1, test_x.shape[-1])
        return self.model.predict(test_x)


def train_svm(config, logger, train_and_valid_data):
    train_x, train_y, valid_x, valid_y = train_and_valid_data

    model = SVMModel(config)
    model.train(train_x, train_y)

    valid_pred = model.predict(valid_x)
    valid_y = valid_y.flatten()
    valid_loss = mean_squared_error(valid_y, valid_pred)

    logger.info(f"Valid MSE: {valid_loss:.6f}")

    if valid_loss < config.valid_loss_min:
        joblib.dump(model, config.model_save_path + config.model_name)
        logger.info(f"Model saved to {config.model_save_path + config.model_name}")
    else:
        logger.info("Validation loss did not improve, model not saved.")


def predict_svm(config, test_x):
    model = joblib.load(config.model_save_path + config.model_name)
    return model.predict(test_x)
