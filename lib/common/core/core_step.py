# Copyright (C) 2026. All rights reserved.
"""core 域 Lib 入口：通用步骤（无装饰器，纯实现）。

实例管理（has/register/get/clear）仅在本层出现；
``tblocks/step_impl/core`` 中的同名原子节点只做薄封装调用本模块。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.result_helper import step_result
from lib.common.framework.step_singletons import current_device_id
from lib.core import instance_manager
from lib.common.core.utils.core_manager import CoreManager

_CORE_PREFIX = "core_manager"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> CoreManager:
    """懒创建并注册 CoreManager（普通类，缓存于实例管理器）。"""
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, CoreManager())
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 CoreManager。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


def step_wait_seconds(seconds: float = 1) -> Dict[str, Any]:
    """等待指定秒数。"""
    actual = _get_core().wait_seconds(seconds)
    return step_result(
        "step_wait_seconds",
        True,
        f"已等待 {actual:g} 秒",
        {"result": actual, "seconds": actual},
    )


def step_log_message(message: str, level: str = "info") -> Dict[str, Any]:
    """向项目日志写入一条消息。"""
    text = _get_core().log_message(message, level=level)
    return step_result(
        "step_log_message",
        True,
        f"已记录日志: {text}",
        {"result": text, "message": text, "level": level},
    )


def step_add_numbers(left: float, right: float) -> Dict[str, Any]:
    """两个数值相加，结果放入 ``data.result``。"""
    result = _get_core().add_numbers(left, right)
    return step_result(
        "step_add_numbers",
        True,
        f"{left:g} + {right:g} = {result:g}",
        {"result": result, "left": float(left), "right": float(right)},
    )


def step_subtract_numbers(left: float, right: float) -> Dict[str, Any]:
    """两个数值相减（left - right）。"""
    result = _get_core().subtract_numbers(left, right)
    return step_result(
        "step_subtract_numbers",
        True,
        f"{left:g} - {right:g} = {result:g}",
        {"result": result, "left": float(left), "right": float(right)},
    )


def step_multiply_numbers(left: float, right: float) -> Dict[str, Any]:
    """两个数值相乘。"""
    result = _get_core().multiply_numbers(left, right)
    return step_result(
        "step_multiply_numbers",
        True,
        f"{left:g} * {right:g} = {result:g}",
        {"result": result, "left": float(left), "right": float(right)},
    )


def step_concatenate_text(left: Any, right: Any, separator: str = "") -> Dict[str, Any]:
    """文本拼接，结果放入 ``data.result``。"""
    result = _get_core().concatenate_text(left, right, separator=separator)
    return step_result(
        "step_concatenate_text",
        True,
        f"拼接结果: {result}",
        {"result": result},
    )


def step_parse_number_text(text: Any) -> Dict[str, Any]:
    """解析文本中的第一个数值（兼容 ``￥78,000.00`` / ``+100.00`` / ``10.00%`` 格式）。"""
    value = _get_core().parse_number_text(text)
    return step_result(
        "step_parse_number_text",
        True,
        f"文本 {text!r} 解析数值: {value:g}",
        {"result": value, "value": value, "source_text": str(text)},
    )
