# Copyright (C) 2026. All rights reserved.
"""account 域 Lib 入口：资金账户接口检查点。"""
from __future__ import annotations

from typing import Any, Dict

from lib.common.result_helper import check_result


def check_account_business_code(code: Any, expected: int = 200) -> Dict[str, Any]:
    """检查接口业务码是否等于期望值（成功 200 / 失败 100）。

    Args:
        code: 上游接口步骤 ``data.code``（或 ``data.result``）。
        expected: 期望业务码，默认 200；显式传 None 表示该行不校验业务码（N/A 跳过）。
    """
    if expected is None:
        return check_result(
            "check_account_business_code",
            True,
            f"未设置期望业务码（N/A），跳过：code={code!r}",
            expected=None,
            actual=code,
            data={"code": code, "expected": None, "skipped": True},
        )
    try:
        actual_code = int(code)
        expected_code = int(expected)
    except (TypeError, ValueError):
        return check_result(
            "check_account_business_code",
            False,
            f"业务码无法按整数比较: code={code!r}, expected={expected!r}",
            expected=expected,
            actual=code,
        )
    passed = actual_code == expected_code
    return check_result(
        "check_account_business_code",
        passed,
        f"业务码 {actual_code} {'等于' if passed else '不等于'} 期望 {expected_code}",
        expected=expected_code,
        actual=actual_code,
        data={"code": actual_code, "expected": expected_code},
    )


def check_account_http_status(http_status: Any, expected: int = 200) -> Dict[str, Any]:
    """检查 HTTP 状态码。"""
    try:
        actual_status = int(http_status)
        expected_status = int(expected)
    except (TypeError, ValueError):
        return check_result(
            "check_account_http_status",
            False,
            f"HTTP 状态码无法比较: {http_status!r}",
            expected=expected,
            actual=http_status,
        )
    passed = actual_status == expected_status
    return check_result(
        "check_account_http_status",
        passed,
        f"HTTP 状态码 {actual_status} {'等于' if passed else '不等于'} 期望 {expected_status}",
        expected=expected_status,
        actual=actual_status,
    )


def check_account_message_contains(message: Any, expected: str) -> Dict[str, Any]:
    """检查接口业务消息包含期望片段。

    expected 为 None（含数据驱动行传入空串，经 str 类型转换后为 None）时
    表示该行不做消息断言（N/A 跳过）。
    """
    if expected is None:
        return check_result(
            "check_account_message_contains",
            True,
            "未设置期望消息片段（N/A），跳过",
            expected=None,
            actual=message,
            data={"skipped": True},
        )
    text = "" if message is None else str(message)
    passed = str(expected) in text
    return check_result(
        "check_account_message_contains",
        passed,
        f"业务消息{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
    )
