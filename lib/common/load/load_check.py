# Copyright (C) 2026. All rights reserved.
"""load 域 Lib 入口：负载指标检查点。"""
from __future__ import annotations

from typing import Any

from lib.common.result_helper import check_result


def _to_float(value: Any) -> float:
    return float(value)


def check_load_success_rate(success_rate: Any, min_rate: float = 0.95):
    """检查负载成功率不低于阈值。"""
    try:
        actual = _to_float(success_rate)
        threshold = _to_float(min_rate)
    except (TypeError, ValueError):
        return check_result(
            "check_load_success_rate", False,
            f"成功率无法比较: {success_rate!r}",
            expected=f">={min_rate}", actual=success_rate,
        )
    passed = actual >= threshold
    return check_result(
        "check_load_success_rate", passed,
        f"成功率 {actual * 100:.1f}% {'>=' if passed else '<'} 阈值 {threshold * 100:.1f}%",
        expected=threshold, actual=actual,
    )


def check_load_percentile_ms(percentile_ms: Any, percentile: str = "p95",
                             max_ms: float = 2000):
    """检查指定分位延迟（毫秒）不超过阈值。"""
    try:
        actual = _to_float(percentile_ms)
        threshold = _to_float(max_ms)
    except (TypeError, ValueError):
        return check_result(
            "check_load_percentile_ms", False,
            f"{percentile} 延迟无法比较: {percentile_ms!r}",
            expected=f"{percentile}<={max_ms}ms", actual=percentile_ms,
        )
    passed = actual <= threshold
    return check_result(
        "check_load_percentile_ms", passed,
        f"{percentile} 延迟 {actual}ms {'<=' if passed else '>'} 阈值 {threshold}ms",
        expected=threshold, actual=actual,
    )


def check_load_rps(rps: Any, min_rps: float = 2.0):
    """检查实测吞吐量（请求/秒）不低于阈值。"""
    try:
        actual = _to_float(rps)
        threshold = _to_float(min_rps)
    except (TypeError, ValueError):
        return check_result(
            "check_load_rps", False,
            f"RPS 无法比较: {rps!r}",
            expected=f">={min_rps}", actual=rps,
        )
    passed = actual >= threshold
    return check_result(
        "check_load_rps", passed,
        f"RPS {actual} {' >=' if passed else ' <'} 阈值 {threshold}",
        expected=threshold, actual=actual,
    )


def check_load_no_server_error(server_errors: Any, max_count: int = 0):
    """检查 5xx 服务端错误数量不超过预算（默认必须为 0）。"""
    try:
        actual = int(server_errors)
        budget = int(max_count)
    except (TypeError, ValueError):
        return check_result(
            "check_load_no_server_error", False,
            f"5xx 计数无法比较: {server_errors!r}",
            expected=f"<={max_count}", actual=server_errors,
        )
    passed = actual <= budget
    return check_result(
        "check_load_no_server_error", passed,
        f"5xx 错误数 {actual} {'<=' if passed else '>'} 预算 {budget}",
        expected=budget, actual=actual,
    )


def check_load_all_completed(total_requests: Any, completed: Any):
    """检查所有请求均已完成（无挂起/漏发）。"""
    try:
        total = int(total_requests)
        done = int(completed)
    except (TypeError, ValueError):
        return check_result(
            "check_load_all_completed", False,
            f"完成数无法比较: total={total_requests!r}, completed={completed!r}",
            expected=total_requests, actual=completed,
        )
    passed = done == total
    return check_result(
        "check_load_all_completed", passed,
        f"完成请求 {done}/{total} {'全部完成' if passed else '存在缺失'}",
        expected=total, actual=done,
    )


def check_load_business_success_rate(business_total: Any, business_ok: Any,
                                     min_rate: float = 1.0):
    """检查 JSON 业务码成功率（business_total=0 时该端点无业务码，检查跳过并通过）。"""
    try:
        total = int(business_total)
        ok = int(business_ok)
        threshold = _to_float(min_rate)
    except (TypeError, ValueError):
        return check_result(
            "check_load_business_success_rate", False,
            f"业务码计数无法比较: total={business_total!r}, ok={business_ok!r}",
            expected=min_rate, actual=None,
        )
    if total == 0:
        return check_result(
            "check_load_business_success_rate", True,
            "该端点响应无业务码字段，业务码成功率检查跳过（N/A）",
            expected="N/A", actual="N/A",
        )
    actual = ok / total
    passed = actual >= threshold
    return check_result(
        "check_load_business_success_rate", passed,
        f"业务码 200 占比 {actual * 100:.1f}%（{ok}/{total}）"
        f"{'>=' if passed else '<'} 阈值 {threshold * 100:.1f}%",
        expected=threshold, actual=round(actual, 4),
    )
