#!usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import torch
from torch.nn import Module, LSTM, Linear
from torch.utils.data import DataLoader, TensorDataset


class Net(Module):
    """pytorch预测模型，包括LSTM时序预测层和Linear回归输出层"""
    def __init__(self, config):
        super(Net, self).__init__()
        self.lstm = LSTM(
            input_size=config.input_size,
            hidden_size=config.hidden_size,
            num_layers=config.lstm_layers,
            batch_first=True,
            dropout=config.dropout_rate
        )
        self.linear = Linear(in_features=config.hidden_size, out_features=config.output_size)

    def forward(self, x, hidden=None):
        lstm_out, hidden = self.lstm(x, hidden)
        linear_out = self.linear(lstm_out)
        return linear_out, hidden


def train(config, logger, train_and_valid_data):
    vis = None
    if config.do_train_visualized:
        import visdom
        vis = visdom.Visdom(env='model_pytorch')

    train_x, train_y, valid_x, valid_y = train_and_valid_data
    # 先转为Tensor
    train_x, train_y = torch.from_numpy(train_x).float(), torch.from_numpy(train_y).float()
    valid_x, valid_y = torch.from_numpy(valid_x).float(), torch.from_numpy(valid_y).float()
    # DataLoader可自动生成可训练的batch数据
    train_loader = DataLoader(TensorDataset(train_x, train_y), batch_size=config.batch_size)
    valid_loader = DataLoader(TensorDataset(valid_x, valid_y), batch_size=config.batch_size)

    # 选择CPU或GPU进行训练
    device = torch.device("cuda:0" if config.use_cuda and torch.cuda.is_available() else "cpu")
    # 如果是GPU训练，.to(device) 会把模型/数据复制到GPU显存中
    model = Net(config).to(device)
    # 如果是增量训练，会先加载原模型参数
    if config.add_train:
        model.load_state_dict(torch.load(config.model_save_path + config.model_name))
    # 定义优化器和loss
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    criterion = torch.nn.MSELoss()

    valid_loss_min = float("inf")
    bad_epoch = 0
    global_step = 0
    for epoch in range(config.epoch):
        logger.info(f"Epoch {epoch}/{config.epoch}")
        model.train()  # 转换成训练模式
        train_loss_array = []
        hidden_train = None

        for i, _data in enumerate(train_loader):
            _train_x, _train_y = _data[0].to(device), _data[1].to(device)
            optimizer.zero_grad()  # 训练前将梯度信息置0
            pred_y, hidden_train = model(_train_x, hidden_train)  # 走前向计算forward函数

            # 如果非连续训练，把hidden重置
            if not config.do_continue_train:
                hidden_train = None
            else:
                h_0, c_0 = hidden_train
                h_0.detach_(), c_0.detach_()  # 去掉梯度信息
                hidden_train = (h_0, c_0)
            loss = criterion(pred_y, _train_y)  # 计算loss
            loss.backward()  # 将loss反向传播
            optimizer.step()  # 用优化器更新参数
            train_loss_array.append(loss.item())

            global_step += 1
            if config.do_train_visualized and global_step % 100 == 0:  # 每一百步显示一次
                vis.line(
                    X=np.array([global_step]),
                    Y=np.array([loss.item()]),
                    win='Train_Loss',
                    update='append' if global_step > 0 else None,
                    name='Train',
                    opts=dict(showlegend=True)
                )

        # 以下为早停机制，当模型训练连续config.patience个epoch都没有使验证集预测效果提升时，就停止，防止过拟合
        model.eval()  # pytorch中，预测时要转换成预测模式
        valid_loss_array = []
        hidden_valid = None
        for _valid_x, _valid_y in valid_loader:
            _valid_x, _valid_y = _valid_x.to(device), _valid_y.to(device)
            pred_y, hidden_valid = model(_valid_x, hidden_valid)
            if not config.do_continue_train: hidden_valid = None
            loss = criterion(pred_y, _valid_y)  # 验证过程只有前向计算，无反向传播过程
            valid_loss_array.append(loss.item())

        train_loss_cur = np.mean(train_loss_array)
        valid_loss_cur = np.mean(valid_loss_array)
        logger.info(f"Train loss: {train_loss_cur:.6f}. "
                    f"Valid loss: {valid_loss_cur:.6f}.")

        # 若开启了可视化，则绘制loss曲线
        if config.do_train_visualized:
            vis.line(
                X=np.array([epoch]), Y=np.array([train_loss_cur]),
                win='Epoch_Loss', update='append' if epoch > 0 else None,
                opts=dict(showlegend=True), name='Train',
            )
            vis.line(
                X=np.array([epoch]), Y=np.array([valid_loss_cur]),
                win='Epoch_Loss', update='append' if epoch > 0 else None,
                opts=dict(showlegend=True), name='Eval',
            )

        if valid_loss_cur < valid_loss_min:
            valid_loss_min = valid_loss_cur
            bad_epoch = 0
            # 模型保存
            torch.save(model.state_dict(), config.model_save_path + config.model_name)
        else:
            bad_epoch += 1
            # 如果验证集指标连续patience个epoch没有提升，就停掉训练
            if bad_epoch >= config.patience:
                logger.info(f"The training stops early in epoch {epoch}.")
                break


def predict(config, test_x):
    # 获取测试数据
    test_x = torch.from_numpy(test_x).float()
    test_set = TensorDataset(test_x)
    test_loader = DataLoader(test_set, batch_size=1)

    # 加载模型与参数
    device = torch.device("cuda:0" if config.use_cuda and torch.cuda.is_available() else "cpu")
    model = Net(config).to(device)
    model_path = config.model_save_path + config.model_name
    model.load_state_dict(torch.load(model_path))

    # 先定义一个tensor保存预测结果
    result = torch.Tensor().to(device)

    # 预测过程
    model.eval()
    hidden_predict = None
    for _data in test_loader:
        data_x = _data[0].to(device)
        pred_x, hidden_predict = model(data_x, hidden_predict)
        # if not config.do_continue_train: hidden_predict = None
        # 实验发现无论是否是连续训练模式，把上一个time_step的hidden传入下一个效果都更好
        cur_pred = torch.squeeze(pred_x, dim=0)
        result = torch.cat((result, cur_pred), dim=0)

    # 先去梯度信息，如果在gpu要转到cpu，最后要返回numpy数据
    return result.detach().cpu().numpy()
