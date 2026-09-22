# Copyright (C) 2026. All rights reserved.
"""load 域 step 原子节点（薄封装，仅调用 lib 入口）。

仅面向**只读/无数据副作用**端点（首页、公共查询接口、登录接口）；
返回 data 为完整负载指标：success_rate / p50/p90/p95/p99_ms / rps /
status_dist / error_dist / server_errors / business_success_rate 等。
"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.load import load_step as lib


@composer_step(
    name="step_load_http",
    description="HTTP 并发负载：对单个只读端点发起并发请求，聚合成功率/分位延迟/RPS/状态分布",
    category="load",
    params={
        "path": {"name": "请求路径", "type": "str", "required": True,
                 "description": "以 / 开头，如 / 或 /loan/loan/listtender（仅只读端点）"},
        "method": {"name": "HTTP 方法", "type": "str", "required": False,
                   "default": "GET", "enum": ["GET", "POST"], "description": "GET 或 POST"},
        "data": {"name": "表单参数", "type": "dict", "required": False,
                 "default": {}, "description": "POST 表单键值（GET 忽略）"},
        "site": {"name": "目标站点", "type": "str", "required": False,
                 "default": "front", "enum": ["front", "back"],
                 "description": "front=前台8081，back=后台8082"},
        "concurrency": {"name": "并发数", "type": "int", "required": False,
                        "default": 5, "description": "并发 worker 数（教学环境建议 5~10）"},
        "total_requests": {"name": "总请求数", "type": "int", "required": False,
                           "default": 30, "description": "总请求次数"},
        "expected_status": {"name": "期望状态码", "type": "int", "required": False,
                            "default": 200, "description": "成功判定状态码；传 null 表示 <400 即成功"},
        "ramp_up": {"name": "爬坡秒数", "type": "float", "required": False,
                    "default": 0.0, "description": "渐进加压秒数，0=瞬时加压"},
    },
)
def step_load_http(path, method="GET", data=None, site="front",
                   concurrency=5, total_requests=30, expected_status=200, ramp_up=0.0):
    """HTTP 并发负载。"""
    return lib.step_load_http(
        path, method=method, data=data, site=site,
        concurrency=concurrency, total_requests=total_requests,
        expected_status=expected_status, ramp_up=ramp_up,
    )
