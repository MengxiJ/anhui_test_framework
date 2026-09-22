# Copyright (C) 2026. All rights reserved.
"""backend 域 Lib 入口：运营后台相关检查点。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.backend.backend_step import _get_core
from lib.common.result_helper import check_result


def check_backend_login_result_contains(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查后台登录结果文本包含期望内容（如“欢迎光临”）。"""
    text = _get_core(device_id).get_back_login_result_text()
    passed = str(expected) in text
    return check_result(
        "check_backend_login_result_contains",
        passed,
        f"后台登录结果文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"text": text},
    )


def check_loan_review_status(
    expected: str = "通过",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查额度审核记录中的状态文本（期望“通过”）。"""
    text = _get_core(device_id).get_review_result_text()
    passed = str(expected) == text
    return check_result(
        "check_loan_review_status",
        passed,
        f"额度审核状态为 {text!r}，期望 {expected!r}",
        expected=expected,
        actual=text,
        data={"status": text},
    )


def check_loan_review_status_contains(
    expected: str = "通过",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查额度审核状态文本包含期望内容。"""
    text = _get_core(device_id).get_review_result_text()
    passed = str(expected) in text
    return check_result(
        "check_loan_review_status_contains",
        passed,
        f"额度审核状态文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"status": text},
    )
