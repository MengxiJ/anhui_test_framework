# Copyright (C) 2026. All rights reserved.
"""load 域 Lib 入口：HTTP 负载步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.load.utils.load_manager import LoadTestManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_KEY = "load_core:default"


def _get_core() -> LoadTestManager:
    if not instance_manager.has_instance(_CORE_KEY):
        instance_manager.register_instance(_CORE_KEY, LoadTestManager())
    return instance_manager.get_instance(_CORE_KEY)


def clear_core() -> None:
    """释放 LoadTestManager。"""
    instance_manager.clear_instance(_CORE_KEY)


def step_load_http(
    path: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    site: str = "front",
    concurrency: int = 5,
    total_requests: int = 30,
    expected_status: Optional[int] = 200,
    ramp_up: float = 0.0,
) -> Dict[str, Any]:
    """对单个端点发起并发负载，回传成功率/分位延迟/RPS/状态分布等聚合指标。"""
    stats = _get_core().run_load(
        method=method,
        path=path,
        site=site,
        data=data,
        concurrency=concurrency,
        total_requests=total_requests,
        expected_status=expected_status,
        ramp_up=ramp_up,
    )
    message = (
        f"负载 {method} {stats['site'].upper()} {path}：并发 {concurrency} / 共 {total_requests}，"
        f"成功率 {stats['success_rate'] * 100:.1f}%，RPS {stats['rps']}，"
        f"p95 {stats['p95_ms']}ms，5xx {stats['server_errors']}，"
        f"耗时 {stats['elapsed_s']}s"
    )
    return step_result("step_load_http", True, message, stats)
