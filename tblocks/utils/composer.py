# Copyright (C) 2026. All rights reserved.
"""Step / Check 装饰器（原子节点标准化与注册）。

用法（参数必须是合法 Python：True/False/None，禁止 JSON 风格 true/false/null）：

    @composer_step(
        name="step_xxx",
        description="……",
        category="member",
        params={"phone": {"type": "str", "required": True}},
    )
    def step_xxx(phone):
        return lib_step(phone)

装饰器职责：

1. 把节点（含元数据与可调用对象）注册到全局 ``STEP_REGISTRY`` / ``CHECK_REGISTRY``；
2. 统一捕获异常并转换为标准失败结果（业务代码只需 raise）；
3. 归一化返回结构，补齐 step/check、timestamp 等必填字段。
"""
from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Optional

from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY
from lib.common.result_helper import now_timestamp


def composer_step(
    name: Optional[Any] = None,
    description: str = "",
    category: str = "",
    params: Optional[Dict[str, Any]] = None,
    pre_conditions: Optional[list] = None,
    post_conditions: Optional[list] = None,
):
    """注册并标准化一个 step 节点。"""

    def _decorate(func: Callable) -> Callable:
        node_id = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            try:
                result = func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - 装饰器是异常→失败结果的边界
                return _failed_result("step", node_id, exc)
            return _normalize_step(node_id, result)

        STEP_REGISTRY.register(
            node_id,
            {
                "id": node_id,
                "name": node_id,
                "description": description,
                "category": category,
                "params": dict(params or {}),
                "pre_conditions": list(pre_conditions or []),
                "post_conditions": list(post_conditions or []),
                "func": wrapper,
                "raw_func": func,
            },
        )
        return wrapper

    # 支持 @composer_step 不带括号的写法
    if callable(name):
        func = name
        name = None
        return _decorate(func)
    return _decorate


def composer_check(
    name: Optional[Any] = None,
    description: str = "",
    category: str = "",
    params: Optional[Dict[str, Any]] = None,
    pre_conditions: Optional[list] = None,
    post_conditions: Optional[list] = None,
):
    """注册并标准化一个 check 节点。"""

    def _decorate(func: Callable) -> Callable:
        node_id = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            try:
                result = func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001
                return _failed_result("check", node_id, exc)
            return _normalize_check(node_id, result)

        CHECK_REGISTRY.register(
            node_id,
            {
                "id": node_id,
                "name": node_id,
                "description": description,
                "category": category,
                "params": dict(params or {}),
                "pre_conditions": list(pre_conditions or []),
                "post_conditions": list(post_conditions or []),
                "func": wrapper,
                "raw_func": func,
            },
        )
        return wrapper

    if callable(name):
        func = name
        name = None
        return _decorate(func)
    return _decorate


# ---- 返回值归一化 ----
def _normalize_step(node_id: str, result: Any) -> Dict[str, Any]:
    envelope: Dict[str, Any]
    if isinstance(result, dict):
        envelope = dict(result)
    elif isinstance(result, bool):
        envelope = {"status": result}
    elif result is None:
        envelope = {"status": True, "message": "节点执行完成"}
    else:
        envelope = {"status": True, "message": "节点执行完成", "data": {"result": result}}

    envelope.setdefault("step", node_id)
    envelope.setdefault("status", True)
    envelope.setdefault("message", "")
    envelope.setdefault("data", {})
    envelope.setdefault("timestamp", now_timestamp())
    envelope["status"] = bool(envelope["status"])
    if not isinstance(envelope["data"], dict):
        envelope["data"] = {"result": envelope["data"]}
    return envelope


def _normalize_check(node_id: str, result: Any) -> Dict[str, Any]:
    envelope: Dict[str, Any]
    if isinstance(result, dict):
        envelope = dict(result)
    elif isinstance(result, bool):
        envelope = {"status": result}
    elif result is None:
        envelope = {"status": True, "message": "检查执行完成"}
    else:
        envelope = {"status": True, "data": {"result": result}}

    status = bool(envelope.get("status", envelope.get("result", True)))
    envelope.setdefault("check", node_id)
    envelope["status"] = status
    envelope["result"] = status
    envelope.setdefault("message", "")
    envelope.setdefault("expected", None)
    envelope.setdefault("actual", None)
    envelope.setdefault("data", {})
    envelope.setdefault("timestamp", now_timestamp())
    if not isinstance(envelope["data"], dict):
        envelope["data"] = {"result": envelope["data"]}
    return envelope


def _failed_result(kind: str, node_id: str, exc: Exception) -> Dict[str, Any]:
    error_text = f"{type(exc).__name__}: {exc}"
    if kind == "step":
        return {
            "step": node_id,
            "status": False,
            "message": f"节点执行异常: {error_text}",
            "data": {"error": error_text, "error_type": type(exc).__name__},
            "timestamp": now_timestamp(),
        }
    return {
        "check": node_id,
        "status": False,
        "result": False,
        "message": f"检查执行异常: {error_text}",
        "expected": "节点正常执行",
        "actual": f"异常: {error_text}",
        "data": {"error": error_text, "error_type": type(exc).__name__},
        "timestamp": now_timestamp(),
    }
