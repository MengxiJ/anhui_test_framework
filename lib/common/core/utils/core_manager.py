# Copyright (C) 2026. All rights reserved.
"""通用原子能力核心类（普通类，不在类内做单例）。

只提供纯计算 / 纯内存能力，不持有浏览器、连接等需要释放的资源。
生命周期由 ``lib.common.core.core_step`` 入口层托管。
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

from lib.common.core.utils.text_number import parse_number_text


class CoreManager:
    """通用原子能力（等待、日志、数值运算、文本拼接、文本数值解析）。"""

    def wait_seconds(self, seconds: float) -> float:
        """阻塞等待指定秒数，返回实际等待秒数。"""
        seconds = max(0.0, float(seconds))
        time.sleep(seconds)
        return seconds

    def log_message(self, message: str, level: str = "info") -> str:
        """写入项目统一日志。

        Args:
            message: 日志内容。
            level: info / warning / error / debug。

        Returns:
            实际记录的消息文本。
        """
        from lib.core.logging_utils import get_logger

        logger = get_logger("tblocks.core")
        level_name = (level or "info").lower()
        log_func = getattr(logger, level_name, logger.info)
        log_func("[workflow-log] %s", message)
        return str(message)

    def add_numbers(self, left: float, right: float) -> float:
        """加法运算。"""
        return float(left) + float(right)

    def subtract_numbers(self, left: float, right: float) -> float:
        """减法运算（left - right）。"""
        return float(left) - float(right)

    def multiply_numbers(self, left: float, right: float) -> float:
        """乘法运算。"""
        return float(left) * float(right)

    def concatenate_text(self, left: Any, right: Any, separator: str = "") -> str:
        """文本拼接。

        整型运算结果（如 ``5.0``）会规整为 ``5`` 形式以便断言展示。
        """
        left_text = self._humanize(left)
        right_text = self._humanize(right)
        return f"{left_text}{separator}{right_text}"

    @staticmethod
    def _humanize(value: Any) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def parse_number_text(self, text: Any) -> float:
        """解析文本中的第一个数值（兼容 ￥78,000.00 / +100.00 / 10.00% 等格式）。"""
        return parse_number_text(text)
