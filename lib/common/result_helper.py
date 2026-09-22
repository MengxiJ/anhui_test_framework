# Copyright (C) 2026. All rights reserved.
"""Step / Check 标准返回结构构造工具。

数据契约（见《原子化step-check开发指南.md》）：

- Step: ``{step, status(bool), message, data{}, timestamp}``
- Check: ``{check, status, result(=status), message, expected, actual, data{}, timestamp}``

Lib 入口层与 TBlocks 包装层统一使用本模块构造返回值，保证字段口径一致；
异常不在本模块吞掉，由 ``tblocks.utils.composer`` 装饰器统一转换为失败结果。
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional


def now_timestamp() -> str:
    """统一时间戳字符串（``YYYY-mm-dd HH:MM:SS``）。"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def step_result(
    step: str,
    status: bool,
    message: str = "",
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构造标准 Step 返回值。"""
    return {
        "step": step,
        "status": bool(status),
        "message": message,
        "data": dict(data or {}),
        "timestamp": now_timestamp(),
    }


def check_result(
    check: str,
    status: bool,
    message: str = "",
    expected: Any = None,
    actual: Any = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构造标准 Check 返回值（``result`` 与 ``status`` 保持一致）。"""
    status = bool(status)
    return {
        "check": check,
        "status": status,
        "result": status,
        "message": message,
        "expected": expected,
        "actual": actual,
        "data": dict(data or {}),
        "timestamp": now_timestamp(),
    }
