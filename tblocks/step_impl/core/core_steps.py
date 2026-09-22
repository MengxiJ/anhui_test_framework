# Copyright (C) 2026. All rights reserved.
"""core 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from typing import Any

from tblocks.utils.composer import composer_step
from lib.common.core import core_step as lib


@composer_step(
    name="step_wait_seconds",
    description="等待指定秒数（不依赖浏览器与网络，可用于离线工作流）",
    category="core",
    params={
        "seconds": {
            "name": "等待秒数",
            "type": "float",
            "required": False,
            "default": 1,
            "description": "阻塞等待的秒数",
            "min": 0,
        }
    },
)
def step_wait_seconds(seconds=1):
    """等待指定秒数。"""
    return lib.step_wait_seconds(seconds)


@composer_step(
    name="step_log_message",
    description="向项目统一日志写入一条消息",
    category="core",
    params={
        "message": {"name": "日志内容", "type": "str", "required": True, "description": "日志文本"},
        "level": {
            "name": "日志级别",
            "type": "str",
            "required": False,
            "default": "info",
            "enum": ["info", "warning", "error", "debug"],
            "description": "日志级别",
        },
    },
)
def step_log_message(message, level="info"):
    """写入一条工作流日志。"""
    return lib.step_log_message(message, level=level)


@composer_step(
    name="step_add_numbers",
    description="两个数值相加，结果放入 data.result，供后续节点 ${节点.data.result} 引用",
    category="core",
    params={
        "left": {"name": "左值", "type": "float", "required": True, "description": "加数 1"},
        "right": {"name": "右值", "type": "float", "required": True, "description": "加数 2"},
    },
)
def step_add_numbers(left, right):
    """数值加法。"""
    return lib.step_add_numbers(left, right)


@composer_step(
    name="step_subtract_numbers",
    description="两个数值相减（left - right），结果放入 data.result",
    category="core",
    params={
        "left": {"name": "左值", "type": "float", "required": True, "description": "被减数"},
        "right": {"name": "右值", "type": "float", "required": True, "description": "减数"},
    },
)
def step_subtract_numbers(left, right):
    """数值减法。"""
    return lib.step_subtract_numbers(left, right)


@composer_step(
    name="step_multiply_numbers",
    description="两个数值相乘，结果放入 data.result",
    category="core",
    params={
        "left": {"name": "左值", "type": "float", "required": True, "description": "乘数 1"},
        "right": {"name": "右值", "type": "float", "required": True, "description": "乘数 2"},
    },
)
def step_multiply_numbers(left, right):
    """数值乘法。"""
    return lib.step_multiply_numbers(left, right)


@composer_step(
    name="step_concatenate_text",
    description="文本拼接，结果放入 data.result",
    category="core",
    params={
        "left": {"name": "左文本", "type": "str", "required": True, "description": "拼接左侧"},
        "right": {"name": "右文本", "type": "str", "required": True, "description": "拼接右侧"},
        "separator": {
            "name": "分隔符",
            "type": "str",
            "required": False,
            "default": "",
            "description": "中间分隔符，默认无",
        },
    },
)
def step_concatenate_text(left: Any, right: Any, separator=""):
    """文本拼接。"""
    return lib.step_concatenate_text(left, right, separator=separator)


@composer_step(
    name="step_parse_number_text",
    description="解析文本中的第一个数值（兼容 ￥78,000.00 / +100.00 / 10.00% 格式），结果放入 data.result",
    category="core",
    params={
        "text": {
            "name": "数值文本",
            "type": "str",
            "required": True,
            "description": "含数值的文本，如 78,000.00元账户余额 / ￥1,234.56 / +100.00",
        },
    },
)
def step_parse_number_text(text):
    """文本数值解析。"""
    return lib.step_parse_number_text(text)
