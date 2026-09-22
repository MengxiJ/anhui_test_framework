# Copyright (C) 2026. All rights reserved.
"""HTTP 负载/并发压测核心类（普通类，类内不做单例）。

设计原则：

- **只打只读端点**：压测步骤面向首页、公共查询接口、登录接口等无数据副作用端点；
- **零重试**：压测必须暴露真实的失败率与延迟分布，不挂载 urllib3 Retry（区别于业务 ``BaseRequest``）；
- **一线程一会话**：每个并发 worker 独占 ``requests.Session`` 与连接池，无线程竞争；
- **只留聚合数据**：不保留任何响应体（仅字节数），避免高并发下内存膨胀。

归一化结果::

    {
        "method": "POST", "path": "...", "site": "front",
        "concurrency": 5, "total_requests": 30, "completed": 30,
        "success": 30, "failed": 0, "success_rate": 1.0,
        "server_errors": 0, "client_errors": 0,
        "business_ok": 30, "business_total": 30,
        "rps": 12.4, "elapsed_s": 2.42,
        "latency_avg_ms": 81.2, "latency_min_ms": 45, "latency_max_ms": 310,
        "p50_ms": 78, "p90_ms": 120, "p95_ms": 160, "p99_ms": 300,
        "status_dist": {"200": 30}, "error_dist": {}, "bytes_total": 123456,
    }
"""
from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter

from lib.core.project_config import BACK_URL, BASE_URL

_SITE_BASE_URLS = {
    "front": BASE_URL,
    "back": BACK_URL,
}


class LoadTestManager:
    """线程池驱动的 HTTP 负载发生器。"""

    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout
        self._tls = threading.local()

    # ---- 会话管理 ----
    def _session(self, pool_size: int) -> requests.Session:
        session = getattr(self._tls, "session", None)
        if session is None:
            session = requests.Session()
            # 压测零重试：真实失败必须计入 failed，不能被重试掩盖
            adapter = HTTPAdapter(max_retries=0, pool_connections=pool_size,
                                  pool_maxsize=pool_size, pool_block=True)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self._tls.session = session
        return session

    @staticmethod
    def _percentile(sorted_values: List[float], pct: float) -> Optional[float]:
        """最近秩百分位（nearest-rank），无样本返回 None。"""
        if not sorted_values:
            return None
        if pct <= 0:
            return sorted_values[0]
        if pct >= 100:
            return sorted_values[-1]
        rank = int(-(-pct * len(sorted_values) // 100))  # ceil(pct*n/100)
        rank = max(1, min(rank, len(sorted_values)))
        return sorted_values[rank - 1]

    def run_load(
        self,
        method: str,
        path: str,
        site: str = "front",
        data: Optional[Dict[str, Any]] = None,
        concurrency: int = 5,
        total_requests: int = 30,
        expected_status: Optional[int] = 200,
        ramp_up: float = 0.0,
    ) -> Dict[str, Any]:
        """对单个端点发起 ``total_requests`` 个请求、并发度 ``concurrency`` 的负载。

        Args:
            method: GET / POST。
            path: 以 / 开头的路径。
            site: front=8081 / back=8082。
            data: POST 表单（x-www-form-urlencoded）。
            concurrency: 并发 worker 数。
            total_requests: 总请求数（在 worker 间分摊）。
            expected_status: 期望 HTTP 状态码；None 时以 <400 为成功。
            ramp_up: 爬坡秒数，worker i 首请求前延迟 i*ramp_up/concurrency。
        """
        alias = str(site or "front").strip().lower()
        if alias not in _SITE_BASE_URLS:
            raise ValueError(f"不支持的站点别名: {site!r}，可选: {sorted(_SITE_BASE_URLS)}")
        method = method.upper()
        if method not in ("GET", "POST"):
            raise ValueError(f"压测仅支持 GET/POST，收到: {method}")
        concurrency = max(1, int(concurrency))
        total_requests = max(1, int(total_requests))
        url = _SITE_BASE_URLS[alias].rstrip("/") + path
        form = dict(data or {})

        # 把请求数分摊到 worker
        plan: List[int] = [total_requests // concurrency] * concurrency
        for i in range(total_requests % concurrency):
            plan[i] += 1

        latencies: List[float] = []
        status_dist: Dict[str, int] = {}
        error_dist: Dict[str, int] = {}
        counters = {"completed": 0, "success": 0, "failed": 0,
                    "server_errors": 0, "client_errors": 0,
                    "business_ok": 0, "business_total": 0, "bytes_total": 0}
        lock = threading.Lock()

        def worker(index: int, count: int) -> None:
            session = self._session(concurrency)
            if ramp_up > 0:
                time.sleep(index * ramp_up / concurrency)
            for _ in range(count):
                started = time.perf_counter()
                try:
                    response = session.request(
                        method, url, data=form if method == "POST" else None,
                        timeout=self._timeout,
                    )
                    latency_ms = (time.perf_counter() - started) * 1000
                    self._record_response(response, latency_ms, expected_status,
                                          counters, latencies, status_dist, lock)
                except Exception as exc:  # noqa: BLE001 - 压测需统计全部异常类型
                    err_name = type(exc).__name__
                    with lock:
                        counters["completed"] += 1
                        counters["failed"] += 1
                        error_dist[err_name] = error_dist.get(err_name, 0) + 1

        wall_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(worker, i, n) for i, n in enumerate(plan) if n > 0]
            for future in as_completed(futures):
                future.result()  # worker 内部已吞异常，这里仅传播编程错误
        elapsed = max(time.perf_counter() - wall_start, 0.001)

        ordered = sorted(latencies)
        completed = counters["completed"]
        return {
            "method": method,
            "path": path,
            "site": alias,
            "concurrency": concurrency,
            "total_requests": total_requests,
            "completed": completed,
            "success": counters["success"],
            "failed": counters["failed"],
            "success_rate": round(counters["success"] / total_requests, 4),
            "server_errors": counters["server_errors"],
            "client_errors": counters["client_errors"],
            "business_ok": counters["business_ok"],
            "business_total": counters["business_total"],
            "business_success_rate": (
                round(counters["business_ok"] / counters["business_total"], 4)
                if counters["business_total"] else None
            ),
            "rps": round(completed / elapsed, 2),
            "elapsed_s": round(elapsed, 3),
            "latency_avg_ms": round(sum(ordered) / len(ordered), 1) if ordered else None,
            "latency_min_ms": round(ordered[0], 1) if ordered else None,
            "latency_max_ms": round(ordered[-1], 1) if ordered else None,
            "p50_ms": round(self._percentile(ordered, 50), 1) if ordered else None,
            "p90_ms": round(self._percentile(ordered, 90), 1) if ordered else None,
            "p95_ms": round(self._percentile(ordered, 95), 1) if ordered else None,
            "p99_ms": round(self._percentile(ordered, 99), 1) if ordered else None,
            "status_dist": status_dist,
            "error_dist": error_dist,
            "bytes_total": counters["bytes_total"],
        }

    @staticmethod
    def _record_response(response, latency_ms, expected_status,
                         counters, latencies, status_dist, lock) -> None:
        with lock:
            counters["completed"] += 1
            latencies.append(latency_ms)
            status_key = str(response.status_code)
            status_dist[status_key] = status_dist.get(status_key, 0) + 1
            counters["bytes_total"] += len(response.content)
            if response.status_code >= 500:
                counters["server_errors"] += 1
            elif response.status_code >= 400:
                counters["client_errors"] += 1
            if expected_status is None:
                ok = response.status_code < 400
            else:
                ok = response.status_code == int(expected_status)
            if ok:
                counters["success"] += 1
            else:
                counters["failed"] += 1
            # 业务码统计（仅当响应是 JSON 且含 status/code 字段）
            try:
                body = response.json()
            except Exception:  # noqa: BLE001 - 非 JSON 不参与业务码统计
                body = None
            if isinstance(body, dict):
                biz_code = body.get("code", body.get("status"))
                if biz_code is not None:
                    counters["business_total"] += 1
                    try:
                        if int(biz_code) == 200:
                            counters["business_ok"] += 1
                    except (TypeError, ValueError):
                        pass
