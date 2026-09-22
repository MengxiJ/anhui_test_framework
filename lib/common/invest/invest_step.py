# Copyright (C) 2026. All rights reserved.
"""invest 域 Lib 入口：理财步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.invest.utils.invest_manager import InvestManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "invest_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> InvestManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, InvestManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 InvestManager（浏览器由 reset_instances 统一退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


# ---- 风险测评 ----
def step_get_risk_level(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取会员中心风险测评等级（``data.level_text`` / ``data.assessed``）。"""
    info = _get_core(device_id).get_risk_level()
    return step_result(
        "step_get_risk_level",
        True,
        f"风险测评等级: {info['level_text'] or '（空）'}，assessed={info['assessed']}",
        {
            "result": info["level_text"],
            "level_text": info["level_text"],
            "assessed": info["assessed"],
        },
    )


def step_submit_risk_quiz(
    answers: Optional[List[int]] = None,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """完成一次风险测评（开页→关模态框→答题→提交→跳转 introduce）。

    ``answers`` 为每题选项索引（0 起）；None 时每题选第一项。
    """
    info = _get_core(device_id).submit_risk_quiz(answers)
    message = (
        f"已作答 {len(info['answered'])} 题（缺答 {info['missing']}），"
        f"提交后 URL: {info['final_url']}，"
        f"{'已跳转测评结果页' if info['submitted'] else '未跳转到结果页（可能提交被拒）'}"
    )
    return step_result("step_submit_risk_quiz", True, message, info)


# ---- 投资列表 ----
def step_get_invest_list(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开投资列表解析标的卡片（``data.loans`` / ``data.count``）。"""
    listing = _get_core(device_id).list_loans()
    loans = listing["loans"]
    preview = [
        f"{loan['name']}(id={loan['loan_id']}, 可投={loan['available_text']}元)" for loan in loans[:5]
    ]
    message = f"投资列表解析 {len(loans)} 个标的，前 5: {'; '.join(preview)}"
    return step_result(
        "step_get_invest_list",
        True,
        message,
        {"result": len(loans), "loans": loans, "count": len(loans)},
    )


def step_filter_invest_list(
    tag_text: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """按筛选标签筛选投资列表后重新读取（``data.filter_tag`` / ``data.loans``）。"""
    result = _get_core(device_id).filter_invest_list(tag_text)
    message = (
        f"筛选标签「{tag_text}」{'已应用' if result['applied'] else '未找到'}，"
        f"筛后解析 {result['count']} 个标的"
    )
    return step_result("step_filter_invest_list", True, message, result)


# ---- 选标与投标 ----
def step_open_loan_detail(
    min_available: float = 0.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """从投资列表动态选标并进入详情页（窗口期读取详情信息）。

    选标策略完全由运行时数据决定（可投金额 ≥ min_available 中取最大），
    详情页被站点重定向时 ``detail_available=False`` / ``redirected=True``。
    """
    chosen = _get_core(device_id).choose_loan_and_open_detail(min_available)
    state = "详情就绪" if chosen["detail_available"] else (
        f"被站点重定向（{chosen.get('reason') or '窗口期内未就绪'}）"
    )
    message = (
        f"选中标的「{chosen['loan_name']}」(id={chosen['loan_id']}，"
        f"可投 {chosen['available_amount']} 元)，{state}"
    )
    return step_result("step_open_loan_detail", True, message, chosen)


def step_submit_tender(
    amount: str,
    min_available: float = 0.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """完整投标：动态选标 → 详情页输金额 → 提交（捕获拦截/提交证据）。

    业务成败不由本节点判定：由后续我的投资/拦截 check 核对。
    """
    result = _get_core(device_id).tender(amount, min_available=min_available)
    if result["detail_available"]:
        message = (
            f"标的「{result['loan_name']}」(id={result['loan_id']}) 输入金额 "
            f"{result['amount']} 元：输入={'成功' if result['amount_input'] else '失败'}，"
            f"外层确认={'已点击' if result['submit_clicked'] else '未点击'}，"
            f"iframe 弹窗={'已出现' if result['confirm_modal_opened'] else '未出现'}，"
            f"马上投标={'已点击' if result['modal_confirmed'] else '未点击'}，"
            f"最终 URL: {result['final_url']}"
        )
    else:
        message = (
            f"标的详情页不可用（站点窗口期重定向），投标未执行；"
            f"选中标的「{result['loan_name']}」(id={result['loan_id']})"
        )
    return step_result("step_submit_tender", True, message, result)


# ---- 我的投资 ----
def step_get_my_tenders(
    tab: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """打开我的投资（可指定 tab）读取记录表格。"""
    table = _get_core(device_id).get_my_tender_records(tab or None)
    return _table_step_result("step_get_my_tenders", table, f"我的投资[{table['current_tab'] or '默认'}]")


def step_get_my_tender_all_tabs(device_id: Optional[str] = None) -> Dict[str, Any]:
    """逐 tab 读取我的投资全部记录。"""
    all_tabs = _get_core(device_id).get_my_tender_all_tabs()
    summary = {tab: info["row_count"] for tab, info in all_tabs.items()}
    message = "我的投资全部 tab: " + ", ".join(f"{k}={v}行" for k, v in summary.items())
    return step_result(
        "step_get_my_tender_all_tabs",
        True,
        message,
        {"result": all_tabs, "tabs": summary, "all_tabs": all_tabs},
    )


# ---- 理财巡检 ----
def step_get_receive_plan(
    start_date: str = "",
    end_date: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """打开收款计划页（可选日期筛选）读取表格。"""
    table = _get_core(device_id).get_receive_plan(start_date or "", end_date or "")
    filtered = table.get("filtered", {})
    suffix = f"（筛选 {filtered}）" if any(filtered.values()) else ""
    result = _table_step_result("step_get_receive_plan", table, f"收款计划{suffix}")
    result["data"]["filtered"] = filtered
    return result


def step_get_debt_transfer_list(
    status: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """打开债权转让页（可选状态筛选）读取表格与筛选项。"""
    info = _get_core(device_id).get_debt_transfer(status or "")
    message = (
        f"债权转让页 {info['table_count']} 张表 / {info['total_rows']} 行，"
        f"筛选项 {info['filter_options']}"
        + (f"，已筛选「{info['applied_filter']}」" if info["applied_filter"] else "")
    )
    return step_result("step_get_debt_transfer_list", True, message, info)


def step_open_auto_tender_entry(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开自动投标入口并捕获重定向（未开通托管时跳托管页）。"""
    entry = _get_core(device_id).open_auto_tender_entry()
    suffix = "（发生重定向）" if entry["redirected"] else ""
    return step_result(
        "step_open_auto_tender_entry",
        True,
        f"已打开自动投标入口，最终 URL: {entry['url']}{suffix}",
        {"result": entry["url"], "url": entry["url"], "redirected": entry["redirected"]},
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
            "empty_state": table.get("empty_state", False),
            "tabs": table.get("tabs", []),
            "current_tab": table.get("current_tab"),
        },
    )
