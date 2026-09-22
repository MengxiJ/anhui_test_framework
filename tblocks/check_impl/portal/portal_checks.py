# Copyright (C) 2026. All rights reserved.
"""portal 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.portal import portal_check as lib


@composer_check(
    name="check_portal_http_status_equal",
    description="检查门户接口 HTTP 状态码",
    category="portal",
    params={
        "http_status": {"name": "HTTP 状态", "type": "int", "required": True,
                        "default": "${step_query_loan_list.data.http_status}",
                        "description": "上游步骤 data.http_status"},
        "expected": {"name": "期望状态码", "type": "int", "required": False,
                     "default": 200, "description": "期望 HTTP 状态"},
    },
)
def check_portal_http_status_equal(http_status, expected=200):
    """HTTP 状态码检查。"""
    return lib.check_portal_http_status_equal(http_status, expected)


@composer_check(
    name="check_portal_business_status_equal",
    description="检查门户接口业务 status（成功 200）",
    category="portal",
    params={
        "code": {"name": "业务 status", "type": "int", "required": True,
                 "default": "${step_query_loan_total_stats.data.code}",
                 "description": "上游步骤 data.code"},
        "expected": {"name": "期望业务 status", "type": "int", "required": False,
                     "default": 200, "enum": [200, 100], "description": "期望业务码"},
    },
)
def check_portal_business_status_equal(code, expected=200):
    """业务 status 检查。"""
    return lib.check_portal_business_status_equal(code, expected)


@composer_check(
    name="check_portal_list_not_empty",
    description="检查列表非空（引用上游 data.items）",
    category="portal",
    params={
        "items": {"name": "列表", "type": "list", "required": True,
                  "default": "${step_query_loan_list.data.items}",
                  "description": "上游步骤 data.items"},
    },
)
def check_portal_list_not_empty(items):
    """列表非空检查。"""
    return lib.check_portal_list_not_empty(items)


@composer_check(
    name="check_portal_list_count_gte",
    description="检查本页列表条数不少于期望值",
    category="portal",
    params={
        "items": {"name": "列表", "type": "list", "required": True,
                  "default": "${step_query_loan_list.data.items}",
                  "description": "上游步骤 data.items"},
        "min_count": {"name": "最少条数", "type": "int", "required": False,
                      "default": 1, "min": 0, "description": "最少条数"},
    },
)
def check_portal_list_count_gte(items, min_count=1):
    """列表条数下限检查。"""
    return lib.check_portal_list_count_gte(items, min_count)


@composer_check(
    name="check_portal_total_items_gte",
    description="检查列表接口 total_items 不少于期望值",
    category="portal",
    params={
        "total_items": {"name": "总条数", "type": "int", "required": True,
                        "default": "${step_query_loan_list.data.total_items}",
                        "description": "上游步骤 data.total_items"},
        "min_count": {"name": "最少总数", "type": "int", "required": False,
                      "default": 1, "min": 0, "description": "最少总条数"},
    },
)
def check_portal_total_items_gte(total_items, min_count=1):
    """总条数下限检查。"""
    return lib.check_portal_total_items_gte(total_items, min_count)


@composer_check(
    name="check_portal_items_fields_complete",
    description="检查列表每条记录包含且非空指定字段",
    category="portal",
    params={
        "items": {"name": "列表", "type": "list", "required": True,
                  "default": "${step_query_loan_list.data.items}",
                  "description": "上游步骤 data.items"},
        "required_fields": {"name": "必填字段", "type": "list", "required": False,
                            "default": ["id", "name", "apr", "period", "amount"],
                            "description": "字段名数组"},
    },
)
def check_portal_items_fields_complete(items, required_fields=None):
    """记录字段完整性检查。"""
    if required_fields is None:
        required_fields = ["id", "name", "apr", "period", "amount"]
    return lib.check_portal_items_fields_complete(items, required_fields)


@composer_check(
    name="check_portal_body_field_exists",
    description="检查响应体包含指定字段且非空（0 视为有效值）",
    category="portal",
    params={
        "body": {"name": "响应体", "type": "dict", "required": True,
                 "default": "${step_query_loan_total_stats.data.body}",
                 "description": "上游步骤 data.body"},
        "field": {"name": "字段名", "type": "str", "required": True,
                  "default": "tenderTotal", "description": "期望存在的字段"},
    },
)
def check_portal_body_field_exists(body, field):
    """响应体字段存在性检查。"""
    return lib.check_portal_body_field_exists(body, field)


@composer_check(
    name="check_portal_http_status_below",
    description="检查 HTTP 状态码低于上限（负向参数应 4xx 优雅拒绝而非 5xx）",
    category="portal",
    params={
        "http_status": {"name": "HTTP 状态", "type": "int", "required": True,
                        "description": "上游探针 data.http_status"},
        "limit": {"name": "状态码上限", "type": "int", "required": False,
                  "default": 500, "min": 100, "max": 599, "description": "默认 500（不允许服务端错误）"},
    },
)
def check_portal_http_status_below(http_status, limit=500):
    """HTTP 状态码上限检查。"""
    return lib.check_portal_http_status_below(http_status, limit)


@composer_check(
    name="check_portal_body_json_valid",
    description="检查响应体为合法 JSON（参数被容忍时应返回结构化 JSON）",
    category="portal",
    params={
        "is_json": {"name": "是否 JSON", "type": "bool", "required": True,
                    "description": "上游探针 data.is_json"},
    },
)
def check_portal_body_json_valid(is_json):
    """响应体 JSON 合法性检查。"""
    return lib.check_portal_body_json_valid(is_json)


@composer_check(
    name="check_portal_list_count_range",
    description="检查本页列表条数在 [min_count, max_count] 区间内",
    category="portal",
    params={
        "items": {"name": "列表", "type": "list", "required": True,
                  "description": "上游步骤 data.items"},
        "min_count": {"name": "最少条数", "type": "int", "required": False,
                      "default": 1, "min": 0, "description": "区间下限"},
        "max_count": {"name": "最多条数", "type": "int", "required": False,
                      "default": 10, "min": 1, "description": "区间上限"},
    },
)
def check_portal_list_count_range(items, min_count=1, max_count=10):
    """列表条数区间检查。"""
    return lib.check_portal_list_count_range(items, min_count, max_count)


@composer_check(
    name="check_portal_items_distinct",
    description="检查列表内记录的指定字段无重复（同页数据不重复）",
    category="portal",
    params={
        "items": {"name": "列表", "type": "list", "required": True,
                  "description": "上游步骤 data.items"},
        "field": {"name": "字段名", "type": "str", "required": False,
                  "default": "id", "description": "用于判重的字段"},
    },
)
def check_portal_items_distinct(items, field="id"):
    """同页记录唯一性检查。"""
    return lib.check_portal_items_distinct(items, field)


@composer_check(
    name="check_portal_pagination_differs",
    description="检查两页列表首条记录不同（翻页生效）",
    category="portal",
    params={
        "items_page1": {"name": "第 1 页列表", "type": "list", "required": True,
                        "description": "第 1 页步骤 data.items"},
        "items_page2": {"name": "第 2 页列表", "type": "list", "required": True,
                        "description": "第 2 页步骤 data.items"},
        "field": {"name": "字段名", "type": "str", "required": False,
                  "default": "id", "description": "用于对比的字段"},
    },
)
def check_portal_pagination_differs(items_page1, items_page2, field="id"):
    """翻页生效检查。"""
    return lib.check_portal_pagination_differs(items_page1, items_page2, field)


@composer_check(
    name="check_portal_total_items_equal",
    description="检查两次查询的 total_items 一致（翻页不改变总数）",
    category="portal",
    params={
        "total_1": {"name": "第一次总数", "type": "int", "required": True,
                    "description": "第 1 页步骤 data.total_items"},
        "total_2": {"name": "第二次总数", "type": "int", "required": True,
                    "description": "第 2 页步骤 data.total_items"},
    },
)
def check_portal_total_items_equal(total_1, total_2):
    """两次查询总数一致性检查。"""
    return lib.check_portal_total_items_equal(total_1, total_2)


@composer_check(
    name="check_portal_total_pages_consistent",
    description="检查 total_pages 与 total_items / page_size 数学一致（向上取整）",
    category="portal",
    params={
        "total_items": {"name": "总条数", "type": "int", "required": True,
                        "description": "上游步骤 data.total_items"},
        "total_pages": {"name": "总页数", "type": "int", "required": True,
                        "description": "上游步骤 data.total_pages"},
        "page_size": {"name": "每页条数", "type": "int", "required": False,
                      "default": 10, "min": 1, "description": "服务端每页条数"},
    },
)
def check_portal_total_pages_consistent(total_items, total_pages, page_size=10):
    """总页数数学一致性检查。"""
    return lib.check_portal_total_pages_consistent(total_items, total_pages, page_size)
