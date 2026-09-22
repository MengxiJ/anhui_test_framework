# Copyright (C) 2026. All rights reserved.
"""browser 域 Lib 入口：浏览器相关检查点。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.browser.browser_step import _get_core
from lib.common.result_helper import check_result


def check_element_exists(
    by: str,
    value: str,
    timeout: int = 5,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查元素在给定时间内出现。"""
    exists = _get_core(device_id).element_exists(by, value, timeout=timeout)
    return check_result(
        "check_element_exists",
        exists,
        f"元素 ({by}={value}) {'存在' if exists else '不存在'}",
        expected=f"元素存在 ({by}={value})",
        actual="存在" if exists else "不存在",
        data={"by": by, "value": value, "exists": exists},
    )


def check_element_text_contains(
    by: str,
    value: str,
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查指定元素文本包含期望子串。"""
    text = _get_core(device_id).get_text(by, value)
    passed = str(expected) in text
    return check_result(
        "check_element_text_contains",
        passed,
        f"元素 ({by}={value}) 文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"by": by, "value": value, "text": text},
    )


def check_current_url_contains(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查当前浏览器 URL 包含期望片段。"""
    current_url = _get_core(device_id).get_current_url()
    passed = str(expected) in current_url
    return check_result(
        "check_current_url_contains",
        passed,
        f"当前 URL {'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=current_url,
        data={"url": current_url},
    )


def check_page_title_equal(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查页面标题等于期望值。"""
    title = _get_core(device_id).get_title()
    passed = title == str(expected)
    return check_result(
        "check_page_title_equal",
        passed,
        f"页面标题 {'等于' if passed else '不等于'} {expected!r}",
        expected=expected,
        actual=title,
        data={"title": title},
    )


def check_element_visible(
    by: str,
    value: str,
    timeout: float = 5,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查元素在给定时间内可见。"""
    visible = _get_core(device_id).element_visible(by, value, timeout=timeout)
    return check_result(
        "check_element_visible",
        visible,
        f"元素 ({by}={value}) {'可见' if visible else '不可见'}",
        expected=f"元素可见 ({by}={value})",
        actual="可见" if visible else "不可见",
        data={"by": by, "value": value, "visible": visible},
    )


def check_elements_count_at_least(
    by: str,
    value: str,
    min_count: int = 1,
    timeout: float = 10,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查匹配元素数量不少于 N。"""
    count = _get_core(device_id).count_elements(by, value, timeout=timeout)
    passed = count >= int(min_count)
    return check_result(
        "check_elements_count_at_least",
        passed,
        f"匹配元素数量 {count} {'不少于' if passed else '少于'} {min_count}",
        expected=f">= {min_count}",
        actual=count,
        data={"by": by, "value": value, "count": count, "min_count": int(min_count)},
    )


def check_current_url_matches(
    expected: str,
    mode: str = "contains",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查当前 URL 匹配期望值（contains=包含 / prefix=前缀 / equals=全等）。"""
    current_url = _get_core(device_id).get_current_url()
    mode_key = str(mode).strip().lower()
    if mode_key == "contains":
        passed = str(expected) in current_url
    elif mode_key == "prefix":
        passed = current_url.startswith(str(expected))
    elif mode_key == "equals":
        passed = current_url == str(expected)
    else:
        return check_result(
            "check_current_url_matches",
            False,
            f"不支持的匹配模式: {mode!r}，支持: contains / prefix / equals",
            expected="模式 ∈ [contains, prefix, equals]",
            actual=str(mode),
            data={"url": current_url, "mode": mode_key},
        )
    return check_result(
        "check_current_url_matches",
        passed,
        f"当前 URL（{mode_key} 模式）{'匹配' if passed else '不匹配'} {expected!r}",
        expected=f"{mode_key} {expected!r}",
        actual=current_url,
        data={"url": current_url, "mode": mode_key, "expected": str(expected)},
    )
