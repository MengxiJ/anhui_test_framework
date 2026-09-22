# Copyright (C) 2026. All rights reserved.
"""finance 域 Lib 入口：资金步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.finance.utils.finance_manager import FinanceManager
from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "finance_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> FinanceManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, FinanceManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 FinanceManager（浏览器由 reset_instances 统一退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


# ---- 充值 ----
def step_open_finance_recharge_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开充值页。"""
    url = _get_core(device_id).open_recharge_page()
    return step_result(
        "step_open_finance_recharge_page", True, "已打开充值页", {"result": url, "url": url}
    )


def step_submit_finance_recharge(
    amount: str,
    valicode: str = "8888",
    payment_type: str = "chinapnrTrust",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """提交一笔充值（选通道/输金额/输验证码/提交），捕获提交后交互证据。

    业务成败不由本节点判定，由后续充值记录/余额 check 核对。
    """
    info = _get_core(device_id).recharge(amount, valicode=valicode, payment_type=payment_type)
    message = (
        f"已提交充值 {info['amount']} 元（通道 {info['payment_type']}），"
        f"alert={'有:' + info['alert_text'] if info['alert_present'] else '无'}，"
        f"新窗口={info['new_window']}，最终 URL: {info['final_url']}"
    )
    return step_result("step_submit_finance_recharge", True, message, info)


# ---- 余额 ----
def step_get_finance_balance(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开会员中心读取账户余额，数值放入 ``data.balance``。"""
    info = _get_core(device_id).get_balance()
    return step_result(
        "step_get_finance_balance",
        True,
        f"当前账户余额: {info['balance']}（原文: {info['balance_text']}）",
        {
            "result": info["balance"],
            "balance": info["balance"],
            "balance_text": info["balance_text"],
        },
    )


# ---- 充值记录 ----
def step_get_finance_recharge_records(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开充值记录页读取表格，结果放入 ``data.headers`` / ``data.rows``。"""
    table = _get_core(device_id).get_recharge_records()
    return _table_step_result("step_get_finance_recharge_records", table, "充值记录")


# ---- 交易明细 ----
def step_get_finance_account_logs(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开交易明细页读取全部流水表格。"""
    table = _get_core(device_id).get_account_logs()
    return _table_step_result("step_get_finance_account_logs", table, "交易明细")


def step_filter_finance_account_logs(
    log_type: str = "",
    start_date: str = "",
    end_date: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """交易明细按类型/日期区间筛选后读取表格（空参数跳过对应筛选）。"""
    table = _get_core(device_id).filter_account_logs(
        log_type=log_type or None,
        start_date=start_date or None,
        end_date=end_date or None,
    )
    applied = table.get("applied_filter", {})
    result = _table_step_result("step_filter_finance_account_logs", table, "交易明细筛选结果")
    result["data"]["applied_filter"] = applied
    result["message"] = f"已按 {applied} 筛选交易明细，读取 {table.get('row_count', 0)} 行"
    return result


# ---- 资金管理巡检入口 ----
def step_open_finance_withdraw_entry(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开提现入口并等待重定向稳定，最终 URL 放入 ``data.url``。"""
    entry = _get_core(device_id).open_withdraw_entry()
    suffix = "（发生重定向）" if entry["redirected"] else ""
    return step_result(
        "step_open_finance_withdraw_entry",
        True,
        f"已打开提现入口，最终 URL: {entry['url']}{suffix}",
        {"result": entry["url"], "url": entry["url"], "redirected": entry["redirected"]},
    )


def step_open_finance_trust_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开我的支付账户页（托管状态页）。"""
    url = _get_core(device_id).open_trust_page()
    return step_result(
        "step_open_finance_trust_page", True, f"已打开我的支付账户页: {url}", {"result": url, "url": url}
    )


def step_open_finance_bounty_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开我的红包页。"""
    url = _get_core(device_id).open_bounty_page()
    return step_result(
        "step_open_finance_bounty_page", True, f"已打开我的红包页: {url}", {"result": url, "url": url}
    )


# ---- 内部工具 ----
def _table_step_result(step: str, table: Dict[str, Any], label: str) -> Dict[str, Any]:
    """构造表格读取类步骤的统一返回值。"""
    return step_result(
        step,
        True,
        f"读取{label}: {table.get('row_count', 0)} 行，表头: {table.get('headers', [])}",
        {
            "result": table.get("row_count", 0),
            "headers": table.get("headers", []),
            "rows": table.get("rows", []),
            "row_count": table.get("row_count", 0),
        },
    )
