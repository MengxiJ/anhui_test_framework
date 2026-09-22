# Copyright (C) 2026. All rights reserved.
"""probe 域 Lib 入口：通用 HTTP 探针检查点。"""
from __future__ import annotations

from typing import Any, Dict

from lib.common.result_helper import check_result


def check_probe_http_status(http_status: Any, expected: int = 200) -> Dict[str, Any]:
    """检查探针响应 HTTP 状态码。"""
    try:
        actual = int(http_status)
        wanted = int(expected)
    except (TypeError, ValueError):
        return check_result(
            "check_probe_http_status", False,
            f"HTTP 状态码无法比较: {http_status!r}",
            expected=expected, actual=http_status,
        )
    passed = actual == wanted
    return check_result(
        "check_probe_http_status", passed,
        f"HTTP 状态码 {actual} {'等于' if passed else '不等于'} 期望 {wanted}",
        expected=wanted, actual=actual,
    )


def check_probe_content_contains(body_text: Any, expected: str) -> Dict[str, Any]:
    """检查响应体文本包含期望片段（页面特征断言）。"""
    text = "" if body_text is None else str(body_text)
    passed = str(expected) in text
    return check_result(
        "check_probe_content_contains", passed,
        f"响应体{'包含' if passed else '不包含'} {expected!r}",
        expected=expected, actual=text[:300],
    )


def check_probe_content_type_contains(content_type: Any, expected: str) -> Dict[str, Any]:
    """检查 Content-Type 包含期望片段（如 text/html、application/json、image）。"""
    text = "" if content_type is None else str(content_type).lower()
    passed = str(expected).lower() in text
    return check_result(
        "check_probe_content_type_contains", passed,
        f"Content-Type={text!r} {'包含' if passed else '不包含'} {expected!r}",
        expected=expected, actual=content_type,
    )


def check_probe_body_length_min(body_length: Any, min_length: int = 1) -> Dict[str, Any]:
    """检查响应体字节数不小于阈值（验证码图片/页面非空断言）。"""
    try:
        actual = int(body_length)
        threshold = int(min_length)
    except (TypeError, ValueError):
        return check_result(
            "check_probe_body_length_min", False,
            f"响应字节数无法比较: {body_length!r}",
            expected=f">={min_length}", actual=body_length,
        )
    passed = actual >= threshold
    return check_result(
        "check_probe_body_length_min", passed,
        f"响应体 {actual} 字节 {'>=' if passed else '<'} 阈值 {threshold}",
        expected=f">={threshold}", actual=actual,
    )


def check_probe_content_not_contains(body_text: Any, forbidden: str) -> Dict[str, Any]:
    """检查响应体文本不包含禁止片段（安全断言：载荷不回显/不泄露敏感内容）。"""
    text = "" if body_text is None else str(body_text)
    passed = str(forbidden) not in text
    return check_result(
        "check_probe_content_not_contains", passed,
        f"响应体{'不包含' if passed else '泄露了禁止片段'} {forbidden!r}",
        expected=f"not contains {forbidden!r}",
        actual=forbidden if not passed else "",
    )


def check_probe_http_status_in(http_status: Any, allowed: list) -> Dict[str, Any]:
    """检查 HTTP 状态码落在白名单内（如安全场景允许 200/302/400/403/404，但禁止 500）。"""
    wanted = sorted({int(item) for item in allowed})
    try:
        actual = int(http_status)
    except (TypeError, ValueError):
        return check_result(
            "check_probe_http_status_in", False,
            f"HTTP 状态码无法比较: {http_status!r}",
            expected=wanted, actual=http_status,
        )
    passed = actual in wanted
    return check_result(
        "check_probe_http_status_in", passed,
        f"HTTP 状态码 {actual} {'在' if passed else '不在'}白名单 {wanted}",
        expected=wanted, actual=actual,
    )


# 常见数据库/ORM 错误指纹（大小写不敏感匹配；命中即说明输入穿透到了数据层）
_DB_ERROR_FINGERPRINTS = (
    "sql syntax", "you have an error in your sql", "mysql_fetch", "warning: mysql",
    "mysqli", "sqlstate", "ora-0", "odbc sql server", "sqlite3", "sqlite_error",
    "psycopg2", "pg::", "org.postgresql", "jdbc:", "mybatis", "org.hibernate",
    "unterminated quoted string", "syntax error at or near",
    "microsoft ole db provider for sql server", "valid mysql result",
    "pg_query", "sqlserverjdbc",
)

# 路径穿越成功读取系统文件的指纹
_TRAVERSAL_FINGERPRINTS = (
    "root:x:0:", "root:*:0:", "[extensions]", "[boot loader]", "[fonts]",
    "for 16-bit app support", "boot loader", "/bin/bash", "/bin/sh",
)


def _match_fingerprints(body_text: Any, fingerprints: tuple) -> list:
    text = ("" if body_text is None else str(body_text)).lower()
    return [fp for fp in fingerprints if fp in text]


def check_probe_no_db_error(body_text: Any) -> Dict[str, Any]:
    """检查响应体不包含任何数据库/SQL 错误指纹（SQL 注入未穿透到数据层）。"""
    hits = _match_fingerprints(body_text, _DB_ERROR_FINGERPRINTS)
    passed = not hits
    return check_result(
        "check_probe_no_db_error", passed,
        "响应体未泄露数据库错误指纹" if passed else f"响应体命中数据库错误指纹: {hits}",
        expected="无 SQL/DB 错误指纹", actual=hits,
    )


def check_probe_no_traversal(body_text: Any) -> Dict[str, Any]:
    """检查响应体不包含系统文件指纹（路径穿越未读到 /etc/passwd、win.ini 等）。"""
    hits = _match_fingerprints(body_text, _TRAVERSAL_FINGERPRINTS)
    passed = not hits
    return check_result(
        "check_probe_no_traversal", passed,
        "响应体未包含系统文件指纹" if passed else f"响应体命中路径穿越文件指纹: {hits}",
        expected="无系统文件指纹", actual=hits,
    )
