#!usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from logging.handlers import RotatingFileHandler


class StreamlitLogHandler(logging.StreamHandler):
    def __init__(self, _log_placeholder, stream=None):
        super().__init__(stream)
        self.log_text = ""
        self.log_placeholder = _log_placeholder

    def emit(self, record):
        log_entry = self.format(record)
        self.log_text += log_entry + "\n"
        self.log_placeholder.text(self.log_text)


def load_logger_st(_log_placeholder, level=logging.INFO):
    _logger = logging.getLogger()
    _logger.setLevel(level)

    # 移除之前的handler
    for handler in _logger.handlers[:]:
        _logger.removeHandler(handler)

    streamlit_handler = StreamlitLogHandler(_log_placeholder)
    streamlit_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    streamlit_handler.setFormatter(formatter)
    _logger.addHandler(streamlit_handler)

    return _logger


def load_logger(config):
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)

    # StreamHandler
    if config.do_log_print_to_screen:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level=logging.INFO)
        formatter = logging.Formatter(
            datefmt='%Y/%m/%d %H:%M:%S',
            fmt='[ %(asctime)s ] %(message)s'
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # FileHandler
    if config.do_log_save_to_file:
        log_path = config.log_save_path + "out.log"
        file_handler = RotatingFileHandler(log_path, maxBytes=1024000, backupCount=5)
        file_handler.setLevel(level=logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 把config信息也记录到log文件中
        config_save_str = config.__str__()
        logger.info(config_save_str)

    return logger
