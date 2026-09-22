# Copyright (C) 2026. All rights reserved.
"""load 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.load import load_check as lib


@composer_check(
    name="check_load_success_rate",
    description="检查负载成功率不低于阈值",
    category="load",
    params={
        "success_rate": {"name": "成功率", "type": "float", "required": True,
                         "default": "${step_load_http.data.success_rate}",
                         "description": "上游负载节点 success_rate（0~1）"},
        "min_rate": {"name": "最低成功率", "type": "float", "required": False,
                     "default": 0.95, "description": "成功率下限"},
    },
)
def check_load_success_rate(success_rate, min_rate=0.95):
    """成功率检查。"""
    return lib.check_load_success_rate(success_rate, min_rate)


@composer_check(
    name="check_load_percentile_ms",
    description="检查指定分位延迟（p50/p90/p95/p99）不超过毫秒阈值",
    category="load",
    params={
        "percentile_ms": {"name": "分位延迟", "type": "float", "required": True,
                          "default": "${step_load_http.data.p95_ms}",
                          "description": "上游负载节点的 pXX_ms 值"},
        "percentile": {"name": "分位名称", "type": "str", "required": False,
                       "default": "p95", "enum": ["p50", "p90", "p95", "p99"],
                       "description": "仅用于报告展示"},
        "max_ms": {"name": "延迟上限毫秒", "type": "float", "required": False,
                   "default": 2000, "description": "分位延迟上限"},
    },
)
def check_load_percentile_ms(percentile_ms, percentile="p95", max_ms=2000):
    """分位延迟检查。"""
    return lib.check_load_percentile_ms(percentile_ms, percentile, max_ms)


@composer_check(
    name="check_load_rps",
    description="检查实测吞吐量 RPS 不低于阈值",
    category="load",
    params={
        "rps": {"name": "RPS", "type": "float", "required": True,
                "default": "${step_load_http.data.rps}",
                "description": "上游负载节点 rps"},
        "min_rps": {"name": "最低RPS", "type": "float", "required": False,
                    "default": 2.0, "description": "吞吐量下限（请求/秒）"},
    },
)
def check_load_rps(rps, min_rps=2.0):
    """RPS 检查。"""
    return lib.check_load_rps(rps, min_rps)


@composer_check(
    name="check_load_no_server_error",
    description="检查 5xx 服务端错误数不超过预算（默认 0）",
    category="load",
    params={
        "server_errors": {"name": "5xx数量", "type": "int", "required": True,
                          "default": "${step_load_http.data.server_errors}",
                          "description": "上游负载节点 server_errors"},
        "max_count": {"name": "错误预算", "type": "int", "required": False,
                      "default": 0, "description": "允许的 5xx 上限"},
    },
)
def check_load_no_server_error(server_errors, max_count=0):
    """5xx 预算检查。"""
    return lib.check_load_no_server_error(server_errors, max_count)


@composer_check(
    name="check_load_all_completed",
    description="检查全部请求均已完成（completed == total_requests）",
    category="load",
    params={
        "total_requests": {"name": "总请求数", "type": "int", "required": True,
                           "default": "${step_load_http.data.total_requests}",
                           "description": "上游负载节点 total_requests"},
        "completed": {"name": "已完成数", "type": "int", "required": True,
                      "default": "${step_load_http.data.completed}",
                      "description": "上游负载节点 completed"},
    },
)
def check_load_all_completed(total_requests, completed):
    """全部完成检查。"""
    return lib.check_load_all_completed(total_requests, completed)


@composer_check(
    name="check_load_business_success_rate",
    description="检查 JSON 业务码 200 占比不低于阈值（无业务码字段的端点自动跳过）",
    category="load",
    params={
        "business_total": {"name": "业务响应总数", "type": "int", "required": True,
                           "default": "${step_load_http.data.business_total}",
                           "description": "上游负载节点 business_total"},
        "business_ok": {"name": "业务码200数", "type": "int", "required": True,
                        "default": "${step_load_http.data.business_ok}",
                        "description": "上游负载节点 business_ok"},
        "min_rate": {"name": "最低成功率", "type": "float", "required": False,
                     "default": 1.0, "description": "业务码成功率下限"},
    },
)
def check_load_business_success_rate(business_total, business_ok, min_rate=1.0):
    """业务码成功率检查。"""
    return lib.check_load_business_success_rate(business_total, business_ok, min_rate)
