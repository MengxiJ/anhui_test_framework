# Copyright (C) 2026. All rights reserved.
"""参数类型转换。

转换规则对应《原子化step-check开发指南.md》「参数类型说明」：

| type      | 目标类型 | 空字符串默认 |
|-----------|----------|--------------|
| str/string| str      | None         |
| int       | int      | None         |
| float     | float    | None         |
| number    | float    | None         |
| bool      | bool     | None         |
| list      | list     | []           |
| dict      | dict     | {}           |

已是目标类型时跳过转换。
"""
from __future__ import annotations

import ast
import json
from typing import Any

_BOOL_TRUE = {"true", "1", "yes", "on"}


def cast_value(value: Any, type_name: str) -> Any:
    """按声明类型转换参数值。"""
    if type_name is None:
        return value
    key = str(type_name).strip().lower()

    if key in ("str", "string"):
        if isinstance(value, str) and value == "":
            return None
        return value if isinstance(value, str) else str(value)

    if key == "int":
        if value is None or value == "":
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return int(float(value))

    if key in ("float", "number"):
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return float(value)

    if key == "bool":
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in _BOOL_TRUE

    if key == "list":
        return _cast_list(value)

    if key == "dict":
        return _cast_dict(value)

    # 未声明/未知类型直通
    return value


def _cast_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value == "" or value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(text)
                if isinstance(parsed, list):
                    return parsed
            except Exception:  # noqa: BLE001
                continue
        return [part.strip() for part in text.split(",")]
    return [value]


def _cast_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if value == "" or value is None:
        return {}
    if isinstance(value, str):
        text = value.strip()
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(text)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:  # noqa: BLE001
                continue
    raise ValueError(f"无法将 {value!r} 转换为 dict")
