# Copyright (C) 2026. All rights reserved.
"""browser 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.browser import browser_check as lib


@composer_check(
    name="check_element_exists",
    description="检查元素在给定时间内出现在页面上",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "timeout": {"name": "等待秒数", "type": "int", "required": False,
                    "default": 5, "description": "出现超时"},
    },
)
def check_element_exists(by, value, timeout=5):
    """元素存在检查。"""
    return lib.check_element_exists(by, value, timeout=timeout)


@composer_check(
    name="check_element_text_contains",
    description="检查指定元素文本包含期望子串",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "expected": {"name": "期望子串", "type": "str", "required": True, "description": "期望文本"},
    },
)
def check_element_text_contains(by, value, expected):
    """元素文本包含检查。"""
    return lib.check_element_text_contains(by, value, expected)


@composer_check(
    name="check_current_url_contains",
    description="检查当前浏览器 URL 包含期望片段",
    category="browser",
    params={"expected": {"name": "URL 片段", "type": "str", "required": True,
                         "description": "期望出现在 URL 中的文本"}},
)
def check_current_url_contains(expected):
    """当前 URL 检查。"""
    return lib.check_current_url_contains(expected)


@composer_check(
    name="check_page_title_equal",
    description="检查页面标题等于期望值",
    category="browser",
    params={"expected": {"name": "期望标题", "type": "str", "required": True, "description": "页面标题"}},
)
def check_page_title_equal(expected):
    """页面标题检查。"""
    return lib.check_page_title_equal(expected)


@composer_check(
    name="check_element_visible",
    description="检查元素在给定时间内可见",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "timeout": {"name": "等待秒数", "type": "float", "required": False,
                    "default": 5, "description": "可见超时"},
    },
)
def check_element_visible(by, value, timeout=5):
    """元素可见检查。"""
    return lib.check_element_visible(by, value, timeout=timeout)


@composer_check(
    name="check_elements_count_at_least",
    description="检查匹配元素数量不少于 N",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "min_count": {"name": "最小数量", "type": "int", "required": False,
                      "default": 1, "description": "数量下限"},
        "timeout": {"name": "等待秒数", "type": "float", "required": False,
                    "default": 10, "description": "等待至少一个元素出现的超时"},
    },
)
def check_elements_count_at_least(by, value, min_count=1, timeout=10):
    """元素数量检查。"""
    return lib.check_elements_count_at_least(by, value, min_count=min_count, timeout=timeout)


@composer_check(
    name="check_current_url_matches",
    description="检查当前 URL 匹配期望值（contains=包含 / prefix=前缀 / equals=全等）",
    category="browser",
    params={
        "expected": {"name": "期望 URL", "type": "str", "required": True, "description": "期望匹配的 URL"},
        "mode": {"name": "匹配模式", "type": "str", "required": False,
                 "default": "contains", "enum": ["contains", "prefix", "equals"],
                 "description": "匹配方式"},
    },
)
def check_current_url_matches(expected, mode="contains"):
    """当前 URL 匹配检查。"""
    return lib.check_current_url_matches(expected, mode=mode)
