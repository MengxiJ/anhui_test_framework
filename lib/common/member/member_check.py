# Copyright (C) 2026. All rights reserved.
"""member 域 Lib 入口：前台会员相关检查点。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.member.member_step import _get_core
from lib.common.result_helper import check_result


def check_member_login_result_contains(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查前台登录后页面文本包含期望内容。"""
    text = _get_core(device_id).get_login_result_text()
    passed = str(expected) in text
    return check_result(
        "check_member_login_result_contains",
        passed,
        f"登录结果文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"text": text},
    )


def check_member_register_result_contains(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查注册结果文本包含期望内容（如“注册成功”）。"""
    text = _get_core(device_id).get_register_result_text()
    passed = str(expected) in text
    return check_result(
        "check_member_register_result_contains",
        passed,
        f"注册结果文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"text": text},
    )


def check_credit_apply_result_contains(
    expected: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查前台额度申请结果文本包含期望内容（如申请金额）。"""
    text = _get_core(device_id).get_credit_application_result_text()
    passed = str(expected) in text
    return check_result(
        "check_credit_apply_result_contains",
        passed,
        f"额度申请结果文本{'包含' if passed else '不包含'} {expected!r}",
        expected=expected,
        actual=text,
        data={"text": text},
    )


# ---- 会员中心总览 ----
def check_member_center_summary_loaded(
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查会员中心总览：余额可解析为数值、未读数为非负整数。"""
    info = _get_core(device_id).center_page.read_center_info()
    balance = info.get("balance")
    unread = info.get("unread_count")
    passed = isinstance(balance, (int, float)) and balance >= 0 and isinstance(unread, int) and unread >= 0
    return check_result(
        "check_member_center_summary_loaded",
        passed,
        f"余额解析={balance}，未读消息数={unread}，含测评等级文本={info.get('risk_level_present')}",
        expected="余额为数值且未读数为非负整数",
        actual=f"balance={balance}, unread={unread}",
        data=dict(info),
    )


def check_recent_transactions_loaded(
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查最近交易表格：有表头列（时间/类型/金额/余额任一）或明确空态。"""
    data = _get_core(device_id).get_recent_transactions()
    headers = data.get("headers", [])
    empty_state = bool(data.get("empty_state"))
    header_text = " ".join(headers)
    structure_ok = any(kw in header_text for kw in ("时间", "类型", "金额", "余额", "存入", "支出"))
    passed = structure_ok or empty_state
    return check_result(
        "check_recent_transactions_loaded",
        passed,
        f"最近交易表头 {len(headers)} 列，数据 {data.get('row_count', 0)} 行，空态={empty_state}",
        expected="表头含时间/类型/金额等列，或明确空态",
        actual=f"headers={headers}",
        data=dict(data),
    )


# ---- 站内消息 ----
def check_unread_count_consistent(
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查未读消息数一致性：页面级未读数优先与顶栏比对；无页面级计数时顶栏与中心页一致。"""
    core = _get_core(device_id)
    info = core.message_page.read_message_info(center_unread=core._center_unread)  # noqa: SLF001
    topbar = info.get("topbar_unread")
    page_unread = info.get("page_unread")
    center_unread = info.get("center_unread")
    if page_unread is not None:
        passed = topbar == page_unread
        compare_basis = "页面计数 vs 顶栏"
        expected = f"页面未读={topbar}"
        actual = f"页面未读={page_unread}"
    else:
        # 消息页无独立计数时，顶栏未读数应与进入前中心页一致
        passed = center_unread is not None and topbar == center_unread
        compare_basis = "中心顶栏 vs 消息页顶栏"
        expected = f"未读数={center_unread}"
        actual = f"未读数={topbar}"
    return check_result(
        "check_unread_count_consistent",
        passed,
        f"未读数一致性（{compare_basis}）：中心={center_unread}，顶栏={topbar}，页面={page_unread}",
        expected=expected,
        actual=actual,
        data=dict(info),
    )


# ---- 账户管理杂项页 ----
def check_member_page_loaded(
    page: str,
    expected_head: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查账户管理页面关键区块标题存在（打开页面后实时核对）。"""
    core = _get_core(device_id)
    info = core.misc_page.read_page_info(page)
    head_present = bool(info.get("head_present"))
    head = expected_head or info.get("expected_head")
    return check_result(
        "check_member_page_loaded",
        head_present,
        f"页面 {page} 区块「{head}」{'存在' if head_present else '不存在'}，"
        f"最终 URL: {info.get('final_url')}",
        expected=f"包含区块标题 {head}",
        actual=f"head_present={head_present}",
        data=dict(info),
    )


# ---- 基础资料 ----
def check_profile_field_updated(
    field: str,
    expected_value: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """重新打开资料页回读字段，核对值等于提交值（忽略空白差异）。"""
    core = _get_core(device_id)
    actual = core.read_profile_field(field)
    expected_norm = "".join(str(expected_value).split())
    actual_norm = "".join(str(actual).split())
    passed = expected_norm == actual_norm or expected_norm in actual_norm
    return check_result(
        "check_profile_field_updated",
        passed,
        f"字段 {field} 回读={actual!r}，期望={expected_value!r}",
        expected=expected_value,
        actual=actual,
        data={"field": field, "actual": actual},
    )


# ---- 提醒设置 ----
def check_remind_toggled(
    checkbox_id: str,
    before: bool,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """重新打开提醒页回读复选框，核对状态较切换前已翻转。"""
    core = _get_core(device_id)
    current = core.read_remind_state(checkbox_id)
    before_bool = _to_bool(before)
    passed = current is not None and current != before_bool
    return check_result(
        "check_remind_toggled",
        passed,
        f"复选框 {checkbox_id}：切换前={before_bool}，回读={current}",
        expected=f"状态 != {before_bool}",
        actual=current,
        data={"checkbox_id": checkbox_id, "before": before_bool, "current": current},
    )


def _to_bool(value: Any) -> bool:
    """宽松布尔转换（工作流变量可能传入字符串）。"""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "on", "是", "选中")
