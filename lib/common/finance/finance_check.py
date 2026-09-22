# Copyright (C) 2026. All rights reserved.
"""finance 域 Lib 入口：资金相关检查点。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from lib.common.finance.finance_step import _get_core
from lib.common.finance.utils.record_matcher import (
    EMPTY_STATE_HINTS,
    TYPE_HEADERS,
    find_column_index,
)
from lib.common.result_helper import check_result


def check_finance_balance_increased_at_least(
    previous_balance: float,
    min_increase: float = 0.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查当前余额较前值增加不少于 N（打开会员中心实时读取）。"""
    info = _get_core(device_id).get_balance()
    current = info["balance"]
    previous = float(previous_balance)
    increase = current - previous
    passed = increase >= float(min_increase) - 0.001
    return check_result(
        "check_finance_balance_increased_at_least",
        passed,
        f"余额 {previous} → {current}，增量 {increase:.2f} "
        f"{'不少于' if passed else '小于'} {min_increase}",
        expected=f"余额增量 >= {min_increase}",
        actual=f"增量 {increase:.2f}（{previous} → {current}）",
        data={
            "previous_balance": previous,
            "current_balance": current,
            "increase": increase,
            "min_increase": float(min_increase),
            "balance_text": info["balance_text"],
        },
    )


def check_finance_recharge_record_exists(
    amount: str,
    status_contains: str = "充值成功",
    time_window: float = 900.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查充值记录中存在「金额相等 + 时间窗口内 + 状态关键字」的记录行。"""
    match = _get_core(device_id).match_recharge_record(
        amount, status_contains=status_contains, time_window=time_window
    )
    return _match_check_result("check_finance_recharge_record_exists", match, amount, time_window)


def check_finance_account_log_exists(
    amount: str,
    type_contains: str = "",
    time_window: float = 900.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查交易明细中存在「金额相等 + 时间窗口内（+ 类型关键字）」的流水行。"""
    match = _get_core(device_id).match_account_log(
        amount, type_contains=type_contains or None, time_window=time_window
    )
    return _match_check_result("check_finance_account_log_exists", match, amount, time_window)


def check_finance_account_log_filter_consistent(
    expected_type: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查当前（已筛选）交易明细的类型列与筛选条件一致；空结果时校验空态文案。"""
    core = _get_core(device_id)
    table = core.get_current_records_table()
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    type_idx = find_column_index(headers, TYPE_HEADERS)
    if type_idx is None:
        return check_result(
            "check_finance_account_log_filter_consistent",
            False,
            f"表头中未找到类型列，实际表头: {headers}",
            expected=f"类型列（{list(TYPE_HEADERS)}）存在且值包含 {expected_type!r}",
            actual=f"表头 {headers}",
            data={"headers": headers, "row_count": len(rows)},
        )
    if not rows:
        page_text = core.get_current_page_text()
        empty_state = any(hint in page_text for hint in EMPTY_STATE_HINTS)
        return check_result(
            "check_finance_account_log_filter_consistent",
            empty_state,
            f"筛选 {expected_type!r} 结果为空，"
            + ("页面存在空态文案" if empty_state else "未检测到空态文案"),
            expected=f"类型列均为 {expected_type!r} 或存在空态文案",
            actual="空结果" + ("（空态文案存在）" if empty_state else "（无空态文案）"),
            data={"row_count": 0, "empty_state": empty_state, "headers": headers},
        )
    mismatched = [
        row[type_idx]
        for row in rows
        if type_idx < len(row) and str(expected_type) not in str(row[type_idx])
    ]
    passed = not mismatched
    return check_result(
        "check_finance_account_log_filter_consistent",
        passed,
        f"筛选 {expected_type!r} 后 {len(rows)} 行类型列"
        + ("全部一致" if passed else f"存在不一致: {mismatched[:5]}"),
        expected=f"类型列均包含 {expected_type!r}",
        actual="全部一致" if passed else f"{len(mismatched)} 行不一致: {mismatched[:5]}",
        data={"row_count": len(rows), "mismatched": mismatched[:10], "headers": headers},
    )


def check_finance_withdraw_intercepted(device_id: Optional[str] = None) -> Dict[str, Any]:
    """检查提现入口的前置拦截（双态兼容）。

    - 未绑卡：重定向到银行卡页 → 拦截校验通过；
    - 已绑卡：提现页直达 → 降级为「页面可达」通过并在报告中说明；
    - 其他：失败。
    """
    entry = _get_core(device_id).open_withdraw_entry()
    final_url = entry["url"]
    if "/member/funds/bank" in final_url:
        return check_result(
            "check_finance_withdraw_intercepted",
            True,
            f"未绑卡拦截生效：提现入口重定向到银行卡页（{final_url}）",
            expected="重定向到 /member/funds/bank（未绑卡拦截）",
            actual=final_url,
            data={**entry, "mode": "intercepted"},
        )
    if "/finance/withdraw" in final_url:
        return check_result(
            "check_finance_withdraw_intercepted",
            True,
            f"账号已绑卡，提现页直达，拦截校验不适用（降级为页面可达）: {final_url}",
            expected="重定向到 /member/funds/bank 或（已绑卡）提现页可达",
            actual=final_url,
            data={**entry, "mode": "degraded"},
        )
    return check_result(
        "check_finance_withdraw_intercepted",
        False,
        f"提现入口跳转到未知页面: {final_url}",
        expected="重定向到 /member/funds/bank 或 /finance/withdraw",
        actual=final_url,
        data={**entry, "mode": "unknown"},
    )


def check_finance_trust_page_blocks_visible(
    blocks: Optional[Sequence[str]] = None,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """检查我的支付账户页关键区块可见（默认「账户托管」「授权设置」）。"""
    expected_blocks = [str(b).strip() for b in (blocks or ["账户托管", "授权设置"]) if str(b).strip()]
    core = _get_core(device_id)
    url = core.open_trust_page()
    text = core.get_current_page_text()
    missing = [block for block in expected_blocks if block not in text]
    passed = not missing
    return check_result(
        "check_finance_trust_page_blocks_visible",
        passed,
        "我的支付账户页区块" + (f"全部可见: {expected_blocks}" if passed else f"缺失: {missing}"),
        expected=f"页面包含区块 {expected_blocks}",
        actual="全部可见" if passed else f"缺失 {missing}",
        data={"blocks": expected_blocks, "missing": missing, "url": url},
    )


def check_finance_bounty_page_loaded(device_id: Optional[str] = None) -> Dict[str, Any]:
    """检查我的红包页可达且含红包相关内容。"""
    core = _get_core(device_id)
    url = core.open_bounty_page()
    text = core.get_current_page_text()
    url_ok = "newBounty" in url
    content_ok = "红包" in text
    passed = url_ok and content_ok
    return check_result(
        "check_finance_bounty_page_loaded",
        passed,
        "我的红包页" + ("可达且包含红包内容" if passed else f"校验未过（URL 匹配={url_ok}, 含'红包'文案={content_ok}）"),
        expected="URL 含 newBounty 且页面含“红包”",
        actual=f"URL 匹配={url_ok}, 红包文案={content_ok}",
        data={"url": url, "url_ok": url_ok, "content_ok": content_ok},
    )


# ---- 内部工具 ----
def _match_check_result(
    check: str,
    match: Dict[str, Any],
    amount: Any,
    time_window: float,
) -> Dict[str, Any]:
    """构造记录匹配类 check 的统一返回值（含命中行证据）。"""
    passed = bool(match.get("matched"))
    return check_result(
        check,
        passed,
        f"{'命中记录行' if passed else '未命中'}: {match.get('reason', '')}",
        expected=f"存在金额 {amount} 且时间窗口 {time_window}s 内的记录",
        actual=match.get("reason", ""),
        data={
            "matched": passed,
            "matched_row": match.get("row"),
            "reason": match.get("reason", ""),
            "table_headers": match.get("table_headers", []),
            "row_count": match.get("row_count", 0),
        },
    )
