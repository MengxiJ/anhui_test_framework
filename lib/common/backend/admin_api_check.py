# Copyright (C) 2026. All rights reserved.
"""backend 域 Lib 入口：运营后台 HTTP 接口检查点。"""
from __future__ import annotations

from typing import Any, Dict

from lib.common.result_helper import check_result


def check_backend_api_business_code(code: Any, expected: int = 200) -> Dict[str, Any]:
    """检查后台接口业务码（200 成功 / 100 业务失败）。"""
    try:
        actual = int(code)
        wanted = int(expected)
    except (TypeError, ValueError):
        return check_result(
            "check_backend_api_business_code", False,
            f"业务码无法按整数比较: code={code!r}",
            expected=expected, actual=code,
        )
    passed = actual == wanted
    return check_result(
        "check_backend_api_business_code", passed,
        f"业务码 {actual} {'等于' if passed else '不等于'} 期望 {wanted}",
        expected=wanted, actual=actual,
        data={"code": actual, "expected": wanted},
    )


def check_backend_api_http_status(http_status: Any, expected: int = 200) -> Dict[str, Any]:
    """检查后台接口 HTTP 状态码。"""
    try:
        actual = int(http_status)
        wanted = int(expected)
    except (TypeError, ValueError):
        return check_result(
            "check_backend_api_http_status", False,
            f"HTTP 状态码无法比较: {http_status!r}",
            expected=expected, actual=http_status,
        )
    passed = actual == wanted
    return check_result(
        "check_backend_api_http_status", passed,
        f"HTTP 状态码 {actual} {'等于' if passed else '不等于'} 期望 {wanted}",
        expected=wanted, actual=actual,
    )


def check_backend_api_message_contains(message: Any, expected: str) -> Dict[str, Any]:
    """检查后台接口业务消息包含期望片段。"""
    text = "" if message is None else str(message)
    passed = str(expected) in text
    return check_result(
        "check_backend_api_message_contains", passed,
        f"业务消息{'包含' if passed else '不包含'} {expected!r}",
        expected=expected, actual=text,
    )


def check_backend_api_verifycode_size(body_length: Any, min_length: int = 1000) -> Dict[str, Any]:
    """检查后台图形验证码响应字节数不小于阈值。"""
    try:
        actual = int(body_length)
        threshold = int(min_length)
    except (TypeError, ValueError):
        return check_result(
            "check_backend_api_verifycode_size", False,
            f"响应字节数无法比较: {body_length!r}",
            expected=f">={min_length}", actual=body_length,
        )
    passed = actual >= threshold
    return check_result(
        "check_backend_api_verifycode_size", passed,
        f"验证码图片 {actual} 字节 {'>=' if passed else '<'} 阈值 {threshold}",
        expected=f">={threshold}", actual=actual,
    )
