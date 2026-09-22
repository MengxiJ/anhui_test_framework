# Copyright (C) 2026. All rights reserved.
"""日志设施（原子化项目自包含）。

提供按天滚动的文件日志器 ``GetLog`` 与业务层使用的 ``get_logger``，
不再依赖旧框架根目录 utils.py。
"""
from __future__ import annotations

import logging
import os
from logging import handlers

from lib.core.paths import OUTPUT_DIR


class GetLog:
    """统一日志器（TimedRotatingFileHandler，保留 3 天）。"""

    __log = None

    @classmethod
    def get_log(cls):
        if cls.__log is None:
            cls.__log = logging.getLogger()
            cls.__log.setLevel(logging.INFO)
            log_dir = os.path.join(OUTPUT_DIR, "log")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, "web.log")
            tf = handlers.TimedRotatingFileHandler(
                filename=filename,
                when="midnight",
                interval=1,
                backupCount=3,
                encoding="utf-8",
            )
            fmt = "%(asctime)s %(levelname)s [%(filename)s(%(funcName)s:%(lineno)d)] - %(message)s"
            fm = logging.Formatter(fmt)
            tf.setFormatter(fm)
            cls.__log.addHandler(tf)
        return cls.__log


def get_logger(name: str = "tblocks") -> logging.Logger:
    """获取挂接在统一文件日志器下的子 logger。

    Args:
        name: 调用方名称（子 logger 命名，handler 复用统一配置）。

    Returns:
        logging.Logger 实例。
    """
    base_logger = GetLog.get_log()
    child = logging.getLogger(name)
    child.parent = base_logger
    child.setLevel(logging.INFO)
    return child
