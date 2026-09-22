# Copyright (C) 2026. All rights reserved.
"""资金记录匹配纯函数（无浏览器依赖）。

匹配契约（FR-2）：「金额相等 + 时间窗口」，可选关键字列约束；
表头缺列或时间无法解析时在 reason 中明确说明，不静默通过。
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from lib.common.core.utils.text_number import parse_number_text

_TIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M")
_TIME_RE = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?")

# 通用列名候选（充值记录 / 交易明细等表格共用，命中任一候选即可）
AMOUNT_HEADERS: Tuple[str, ...] = ("充值金额", "存入", "投资金额", "应收总额", "收入", "金额")
TIME_HEADERS: Tuple[str, ...] = ("充值时间", "交易时间", "应收日期", "创建时间", "时间")
STATUS_HEADERS: Tuple[str, ...] = ("状态",)
TYPE_HEADERS: Tuple[str, ...] = ("交易类型", "交易分类", "类型", "摘要")

# 空态文案提示词（筛选结果为空时校验）
EMPTY_STATE_HINTS: Tuple[str, ...] = ("暂无", "没有", "无记录", "未找到", "无数据")


def find_column_index(headers: Optional[Sequence[Any]], candidates: Sequence[str]) -> Optional[int]:
    """按候选列名在表头中查找列下标（双向包含匹配，找不到返回 None）。"""
    normalized = [str(h).strip() for h in (headers or [])]
    for candidate in candidates:
        candidate = str(candidate).strip()
        if not candidate:
            continue
        for index, header in enumerate(normalized):
            if not header:
                continue
            if candidate in header or header in candidate:
                return index
    return None


def parse_row_time(text: Any) -> Optional[datetime]:
    """解析行内时间文本为 datetime；先整串解析，再正则提取子串，失败返回 None。"""
    raw = "" if text is None else str(text).strip()
    if not raw:
        return None
    for fmt in _TIME_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    match = _TIME_RE.search(raw)
    if match:
        for fmt in _TIME_FORMATS:
            try:
                return datetime.strptime(match.group(), fmt)
            except ValueError:
                continue
    return None


def match_table_record(
    table: Optional[Dict[str, Any]],
    amount: Any,
    time_window: float = 900.0,
    amount_headers: Sequence[str] = AMOUNT_HEADERS,
    time_headers: Sequence[str] = TIME_HEADERS,
    keyword_rules: Optional[List[Tuple[Sequence[str], str]]] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """在 ``{headers, rows}`` 表格数据中匹配一行记录。

    Args:
        table: ``get_table_data`` 返回的结构（headers / rows）。
        amount: 期望金额（行金额与解析值差 ≤ 0.01 视为相等）。
        time_window: 行时间与基准时间允许的最大偏差秒数（双向）。
        amount_headers: 金额列名候选。
        time_headers: 时间列名候选。
        keyword_rules: ``[(列名候选, 期望子串), ...]``，如 ``[(STATUS_HEADERS, "充值成功")]``。
        now: 时间窗口基准，缺省当前时间。

    Returns:
        ``{"matched": bool, "row": 行|None, "reason": str}``。
    """
    headers = [str(h).strip() for h in (table or {}).get("headers", [])]
    rows = (table or {}).get("rows", []) or []
    amount_idx = find_column_index(headers, amount_headers)
    time_idx = find_column_index(headers, time_headers)

    if amount_idx is None:
        return {
            "matched": False,
            "row": None,
            "reason": f"表头中未找到金额列 {list(amount_headers)}，实际表头: {headers}",
        }
    expected_amount = float(parse_number_text(amount))
    ref_time = now or datetime.now()

    rules: List[Tuple[Optional[int], str, str]] = []
    for candidates, expected in (keyword_rules or []):
        rules.append((find_column_index(headers, candidates), str(candidates[0]), str(expected)))

    for row in rows:
        if amount_idx >= len(row):
            continue
        try:
            row_amount = parse_number_text(row[amount_idx])
        except ValueError:
            continue
        if abs(row_amount - expected_amount) > 0.01:
            continue
        if time_idx is not None and time_idx < len(row):
            row_time = parse_row_time(row[time_idx])
            if row_time is None:
                continue
            if abs((ref_time - row_time).total_seconds()) > float(time_window):
                continue
        row_matched = True
        for idx, name, expected in rules:
            if idx is None:
                return {
                    "matched": False,
                    "row": None,
                    "reason": f"表头中未找到列 {name!r}，实际表头: {headers}",
                }
            if idx >= len(row) or expected not in str(row[idx]):
                row_matched = False
                break
        if row_matched:
            return {"matched": True, "row": row, "reason": "金额/时间窗口/关键字全部匹配"}
    return {
        "matched": False,
        "row": None,
        "reason": f"共 {len(rows)} 行记录中未找到金额 {expected_amount} 且时间窗口 {time_window}s 内的记录",
    }
