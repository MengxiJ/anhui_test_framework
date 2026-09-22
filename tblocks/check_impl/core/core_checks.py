# Copyright (C) 2026. All rights reserved.
"""core 域 check 原子节点（纯内存断言，离线可运行）。"""
from __future__ import annotations

from typing import Any

from tblocks.utils.composer import composer_check
from lib.common.core import core_check as lib


@composer_check(
    name="check_value_equal",
    description="检查两个值相等（数值按数值比较，其余按字符串比较）",
    category="core",
    params={
        "actual": {"name": "实际值", "type": "str", "required": True,
                   "default": "${step_add_numbers.data.result}", "description": "实际值"},
        "expected": {"name": "期望值", "type": "str", "required": True, "description": "期望值"},
    },
)
def check_value_equal(actual: Any, expected: Any):
    """值相等检查。"""
    return lib.check_value_equal(actual, expected)


@composer_check(
    name="check_value_greater_than",
    description="检查实际数值大于期望值",
    category="core",
    params={
        "actual": {"name": "实际值", "type": "float", "required": True, "description": "实际值"},
        "expected": {"name": "期望值", "type": "float", "required": True, "description": "期望值"},
    },
)
def check_value_greater_than(actual: Any, expected: Any):
    """数值大于检查。"""
    return lib.check_value_greater_than(actual, expected)


@composer_check(
    name="check_value_within_range",
    description="检查实际数值落在 [lower, upper] 闭区间内",
    category="core",
    params={
        "actual": {"name": "实际值", "type": "float", "required": True, "description": "实际值"},
        "lower": {"name": "下限", "type": "float", "required": True, "description": "区间下限"},
        "upper": {"name": "上限", "type": "float", "required": True, "description": "区间上限"},
    },
)
def check_value_within_range(actual: Any, lower: Any, upper: Any):
    """区间检查。"""
    return lib.check_value_within_range(actual, lower, upper)


@composer_check(
    name="check_text_contains",
    description="检查实际文本包含期望子串",
    category="core",
    params={
        "actual": {"name": "实际文本", "type": "str", "required": True, "description": "实际文本"},
        "expected": {"name": "期望子串", "type": "str", "required": True, "description": "期望包含的子串"},
    },
)
def check_text_contains(actual: Any, expected: Any):
    """文本包含检查。"""
    return lib.check_text_contains(actual, expected)


@composer_check(
    name="check_text_not_contains",
    description="检查实际文本不包含指定子串",
    category="core",
    params={
        "actual": {"name": "实际文本", "type": "str", "required": True, "description": "实际文本"},
        "expected": {"name": "排除子串", "type": "str", "required": True, "description": "不应出现的子串"},
    },
)
def check_text_not_contains(actual: Any, expected: Any):
    """文本不包含检查。"""
    return lib.check_text_not_contains(actual, expected)


@composer_check(
    name="check_text_number_compare",
    description="解析文本第一个数值并与期望值比较（兼容 ￥78,000.00 / +100.00 / 10.00% 格式）",
    category="core",
    params={
        "text": {
            "name": "数值文本",
            "type": "str",
            "required": True,
            "description": "含数值的文本，如 78,000.00元账户余额 / ￥1,234.56 / +100.00",
        },
        "operator": {
            "name": "比较运算符",
            "type": "str",
            "required": False,
            "default": ">=",
            "enum": [">", ">=", "<", "<=", "==", "!="],
            "description": "解析值与期望值的比较方式",
        },
        "expected": {
            "name": "期望数值",
            "type": "float",
            "required": True,
            "description": "比较基准值",
        },
    },
)
def check_text_number_compare(text: Any, operator=">=", expected=0):
    """文本数值比较检查。"""
    return lib.check_text_number_compare(text, operator, expected)
