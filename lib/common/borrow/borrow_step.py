# Copyright (C) 2026. All rights reserved.
"""borrow 域 Lib 入口：前台借款（发标）步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.borrow.utils.borrow_manager import BorrowManager
from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "borrow_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> BorrowManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, BorrowManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 BorrowManager（浏览器由 reset_instances 统一退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


# ---- 发标 ----
def step_open_loan_index(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开「品质理财 → 个人借款」页。"""
    _get_core(device_id).open_loan_index()
    return step_result("step_open_loan_index", True, "已打开个人借款页", {"result": "loan_index"})


def step_publish_borrow(
    title: str,
    use: str = "周转",
    amount: str = "200",
    apr: str = "5",
    repay_type: str = "等额本息",
    period: str = "1个月",
    validate: str = "3天",
    tender_min: str = "50元",
    tender_max: str = "不限",
    contents: str = "自动化测试借款标，到期还本付息。",
    valicode: str = "8888",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """前台发标：立即借款 → 填写表单 → 提交。

    业务成败不由本节点判定：由后续结果文本 check 核对。
    """
    info = _get_core(device_id).publish_loan(
        title=title,
        use=use,
        amount=amount,
        apr=apr,
        repay_type=repay_type,
        period=period,
        validate=validate,
        tender_min=tender_min,
        tender_max=tender_max,
        contents=contents,
        valicode=valicode,
    )
    return step_result(
        "step_publish_borrow",
        True,
        f"已提交发标「{title}」金额 {amount} 元，利率 {apr}%",
        {"result": "submitted", **info},
    )


def step_get_borrow_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取发标提交结果文本。"""
    text = _get_core(device_id).get_publish_result_text()
    return step_result(
        "step_get_borrow_result_text",
        True,
        f"发标结果文本: {text}",
        {"result": text, "text": text},
    )
