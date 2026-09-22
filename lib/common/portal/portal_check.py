# Copyright (C) 2026. All rights reserved.
"""portal 域 Lib 入口：门户公共接口检查点。"""
from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List

from lib.common.result_helper import check_result

_CHECK = "check_portal"


def check_portal_http_status_equal(http_status: Any, expected: int = 200) -> Dict[str, Any]:
    """检查门户接口 HTTP 状态码。"""
    try:
        actual = int(http_status)
        expected_code = int(expected)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_http_status_equal", False,
            f"HTTP 状态码无法比较: {http_status!r}", expected=expected, actual=http_status,
        )
    passed = actual == expected_code
    return check_result(
        f"{_CHECK}_http_status_equal", passed,
        f"HTTP 状态码 {actual} {'等于' if passed else '不等于'} 期望 {expected_code}",
        expected=expected_code, actual=actual,
    )


def check_portal_business_status_equal(code: Any, expected: int = 200) -> Dict[str, Any]:
    """检查门户接口业务 status（门户接口成功返回 status=200）。"""
    try:
        actual = int(code)
        expected_code = int(expected)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_business_status_equal", False,
            f"业务 status 无法比较: {code!r}", expected=expected, actual=code,
        )
    passed = actual == expected_code
    return check_result(
        f"{_CHECK}_business_status_equal", passed,
        f"业务 status {actual} {'等于' if passed else '不等于'} 期望 {expected_code}",
        expected=expected_code, actual=actual,
    )


def check_portal_list_not_empty(items: Any) -> Dict[str, Any]:
    """检查列表非空。"""
    count = len(items) if isinstance(items, list) else 0
    passed = count > 0
    return check_result(
        f"{_CHECK}_list_not_empty", passed,
        f"列表{'非空' if passed else '为空'}，共 {count} 条",
        expected="至少 1 条", actual=f"{count} 条",
        data={"count": count},
    )


def check_portal_list_count_gte(items: Any, min_count: int = 1) -> Dict[str, Any]:
    """检查列表条数不少于期望值。"""
    count = len(items) if isinstance(items, list) else 0
    try:
        threshold = int(min_count)
    except (TypeError, ValueError):
        threshold = 1
    passed = count >= threshold
    return check_result(
        f"{_CHECK}_list_count_gte", passed,
        f"列表条数 {count} {'≥' if passed else '<'} 期望 {threshold}",
        expected=f">= {threshold}", actual=count,
        data={"count": count, "min_count": threshold},
    )


def check_portal_total_items_gte(total_items: Any, min_count: int = 1) -> Dict[str, Any]:
    """检查列表接口 total_items 不少于期望值。"""
    try:
        actual = int(total_items)
        threshold = int(min_count)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_total_items_gte", False,
            f"total_items 无法比较: {total_items!r}",
            expected=f">= {min_count}", actual=total_items,
        )
    passed = actual >= threshold
    return check_result(
        f"{_CHECK}_total_items_gte", passed,
        f"total_items {actual} {'≥' if passed else '<'} 期望 {threshold}",
        expected=f">= {threshold}", actual=actual,
    )


def check_portal_items_fields_complete(items: Any, required_fields: Any) -> Dict[str, Any]:
    """检查列表中每条记录都包含且非空指定字段。"""
    fields: List[str]
    if isinstance(required_fields, str):
        fields = [field.strip() for field in required_fields.split(",") if field.strip()]
    elif isinstance(required_fields, Iterable):
        fields = [str(field) for field in required_fields]
    else:
        fields = []
    if not isinstance(items, list) or not items:
        return check_result(
            f"{_CHECK}_items_fields_complete", False,
            "列表为空或不是列表，无法校验字段完整性",
            expected=fields, actual="空列表", data={"fields": fields},
        )
    missing = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            missing.append(f"第 {index + 1} 条不是对象")
            continue
        for field in fields:
            if field not in item or item[field] in (None, ""):
                missing.append(f"第 {index + 1} 条缺字段 {field}")
    passed = not missing
    preview = "；".join(missing[:5])
    return check_result(
        f"{_CHECK}_items_fields_complete", passed,
        f"{len(items)} 条记录字段 {fields} {'完整' if passed else '不完整: ' + preview}",
        expected=fields,
        actual="完整" if passed else f"缺失 {len(missing)} 处",
        data={"fields": fields, "checked": len(items), "missing": missing[:20]},
    )


def check_portal_body_field_exists(body: Any, field: str) -> Dict[str, Any]:
    """检查响应体对象包含指定字段且值非空。"""
    exists = isinstance(body, dict) and field in body and body[field] not in (None, "", [])
    value = body.get(field) if isinstance(body, dict) else None
    return check_result(
        f"{_CHECK}_body_field_exists", exists,
        f"响应体字段 {field!r} {'存在且非空' if exists else '缺失或为空'}",
        expected=f"包含非空字段 {field}", actual=value,
        data={"field": field},
    )


# ---- 功能测试检查（分页 / 去重 / 负向 / 一致性） ----
def check_portal_http_status_below(http_status: Any, limit: int = 500) -> Dict[str, Any]:
    """检查 HTTP 状态码低于上限（负向参数应被 4xx 优雅拒绝而非 5xx）。"""
    try:
        actual = int(http_status)
        threshold = int(limit)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_http_status_below", False,
            f"HTTP 状态码无法比较: {http_status!r}", expected=f"< {limit}", actual=http_status,
        )
    passed = actual < threshold
    return check_result(
        f"{_CHECK}_http_status_below", passed,
        f"HTTP {actual} {'低于' if passed else '不低于'}上限 {threshold}",
        expected=f"< {threshold}", actual=actual,
        data={"http_status": actual, "limit": threshold},
    )


def check_portal_body_json_valid(is_json: Any) -> Dict[str, Any]:
    """检查响应体为合法 JSON（参数被容忍时应返回结构化 JSON 而非错误页）。"""
    passed = bool(is_json)
    return check_result(
        f"{_CHECK}_body_json_valid", passed,
        f"响应体{'为合法 JSON' if passed else '不是合法 JSON（可能返回了错误页）'}",
        expected="合法 JSON", actual="JSON" if passed else "非 JSON",
        data={"is_json": passed},
    )


def check_portal_list_count_range(items: Any, min_count: int = 1, max_count: int = 10) -> Dict[str, Any]:
    """检查本页列表条数在 [min_count, max_count] 区间内。"""
    count = len(items) if isinstance(items, list) else 0
    try:
        low, high = int(min_count), int(max_count)
    except (TypeError, ValueError):
        low, high = 1, 10
    passed = low <= count <= high
    return check_result(
        f"{_CHECK}_list_count_range", passed,
        f"列表条数 {count} {'在' if passed else '不在'}区间 [{low}, {high}]",
        expected=f"[{low}, {high}]", actual=count,
        data={"count": count, "min_count": low, "max_count": high},
    )


def check_portal_items_distinct(items: Any, field: str = "id") -> Dict[str, Any]:
    """检查列表内记录的指定字段无重复（同页数据不重复）。"""
    if not isinstance(items, list) or not items:
        return check_result(
            f"{_CHECK}_items_distinct", False,
            "列表为空或不是列表，无法校验唯一性",
            expected=f"字段 {field} 无重复", actual="空列表",
            data={"field": field},
        )
    values = [item.get(field) for item in items if isinstance(item, dict)]
    duplicates = sorted({v for v in values if values.count(v) > 1}, key=str)
    passed = not duplicates
    return check_result(
        f"{_CHECK}_items_distinct", passed,
        f"{len(items)} 条记录字段 {field} {'无重复' if passed else '存在重复: ' + str(duplicates[:5])}",
        expected=f"{field} 无重复", actual="无重复" if passed else f"重复值 {duplicates[:5]}",
        data={"field": field, "duplicates": duplicates[:10]},
    )


def check_portal_pagination_differs(items_page1: Any, items_page2: Any, field: str = "id") -> Dict[str, Any]:
    """检查两页列表的首条记录指定字段不同（分页确实翻页而非返回相同数据）。"""
    first1 = items_page1[0].get(field) if isinstance(items_page1, list) and items_page1 and isinstance(items_page1[0], dict) else None
    first2 = items_page2[0].get(field) if isinstance(items_page2, list) and items_page2 and isinstance(items_page2[0], dict) else None
    passed = first1 is not None and first2 is not None and first1 != first2
    return check_result(
        f"{_CHECK}_pagination_differs", passed,
        f"第 1 页首条 {field}={first1!r}，第 2 页首条 {field}={first2!r}，"
        f"{'翻页生效' if passed else '两页数据相同或缺失，翻页未生效'}",
        expected="两页首条记录不同", actual=f"{first1!r} vs {first2!r}",
        data={"first_page1": first1, "first_page2": first2, "field": field},
    )


def check_portal_total_items_equal(total_1: Any, total_2: Any) -> Dict[str, Any]:
    """检查两次查询的 total_items 一致（同一数据口径下翻页不改变总数）。"""
    try:
        left, right = int(total_1), int(total_2)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_total_items_equal", False,
            f"total_items 无法比较: {total_1!r} vs {total_2!r}",
            expected="两次相等", actual=f"{total_1!r} vs {total_2!r}",
        )
    passed = left == right
    return check_result(
        f"{_CHECK}_total_items_equal", passed,
        f"两次查询 total_items {left} / {right} {'一致' if passed else '不一致'}",
        expected=left, actual=right,
        data={"total_1": left, "total_2": right},
    )


def check_portal_total_pages_consistent(total_items: Any, total_pages: Any, page_size: int = 10) -> Dict[str, Any]:
    """检查 total_pages 与 total_items / page_size 的数学一致性（向上取整）。"""
    try:
        items, pages, size = int(total_items), int(total_pages), int(page_size)
    except (TypeError, ValueError):
        return check_result(
            f"{_CHECK}_total_pages_consistent", False,
            f"入参无法比较: total_items={total_items!r}, total_pages={total_pages!r}",
            expected="total_pages = ceil(total_items / page_size)",
            actual=f"{total_items!r}, {total_pages!r}",
        )
    if size <= 0:
        return check_result(
            f"{_CHECK}_total_pages_consistent", False,
            f"page_size 必须为正数，收到: {size}",
            expected="page_size > 0", actual=size,
        )
    expected_pages = math.ceil(items / size) if items > 0 else 0
    passed = pages == expected_pages
    return check_result(
        f"{_CHECK}_total_pages_consistent", passed,
        f"total_items={items}，page_size={size}，期望 {expected_pages} 页，实际 {pages} 页"
        f"{'，一致' if passed else '，不一致'}",
        expected=expected_pages, actual=pages,
        data={"total_items": items, "total_pages": pages, "page_size": size,
              "expected_pages": expected_pages},
    )
