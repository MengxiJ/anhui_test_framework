# Copyright (C) 2026. All rights reserved.
"""probe 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.probe import probe_check as lib


@composer_check(
    name="check_probe_http_status",
    description="检查探针响应 HTTP 状态码",
    category="probe",
    params={
        "http_status": {"name": "HTTP 状态码", "type": "int", "required": True,
                        "default": "${step_probe_http_get.data.http_status}",
                        "description": "上游探针节点的 http_status"},
        "expected": {"name": "期望状态码", "type": "int", "required": False,
                     "default": 200, "description": "期望 HTTP 状态"},
    },
)
def check_probe_http_status(http_status, expected=200):
    """HTTP 状态码检查。"""
    return lib.check_probe_http_status(http_status, expected)


@composer_check(
    name="check_probe_content_contains",
    description="检查探针响应体包含期望文本（页面/接口特征断言）",
    category="probe",
    params={
        "body_text": {"name": "响应体文本", "type": "str", "required": True,
                      "default": "${step_probe_http_get.data.body_text}",
                      "description": "上游探针节点的 body_text"},
        "expected": {"name": "期望片段", "type": "str", "required": True,
                     "description": "期望出现的文本，如 ng-app、common/member/login"},
    },
)
def check_probe_content_contains(body_text, expected):
    """响应体包含检查。"""
    return lib.check_probe_content_contains(body_text, expected)


@composer_check(
    name="check_probe_content_type_contains",
    description="检查探针响应 Content-Type 包含期望片段",
    category="probe",
    params={
        "content_type": {"name": "Content-Type", "type": "str", "required": True,
                         "default": "${step_probe_http_get.data.content_type}",
                         "description": "上游探针节点的 content_type"},
        "expected": {"name": "期望片段", "type": "str", "required": False,
                     "default": "text/html",
                     "enum": ["text/html", "application/json", "image", "text/plain"],
                     "description": "Content-Type 期望片段"},
    },
)
def check_probe_content_type_contains(content_type, expected="text/html"):
    """Content-Type 包含检查。"""
    return lib.check_probe_content_type_contains(content_type, expected)


@composer_check(
    name="check_probe_body_length_min",
    description="检查探针响应体字节数不小于阈值",
    category="probe",
    params={
        "body_length": {"name": "响应字节数", "type": "int", "required": True,
                        "default": "${step_probe_http_get.data.body_length}",
                        "description": "上游探针节点的 body_length"},
        "min_length": {"name": "最小字节数", "type": "int", "required": False,
                       "default": 1000, "description": "响应体最小字节阈值"},
    },
)
def check_probe_body_length_min(body_length, min_length=1000):
    """响应体字节数下限检查。"""
    return lib.check_probe_body_length_min(body_length, min_length)


@composer_check(
    name="check_probe_content_not_contains",
    description="检查响应体不包含禁止片段（载荷不回显/敏感内容不泄露）",
    category="probe",
    params={
        "body_text": {"name": "响应体文本", "type": "str", "required": True,
                      "default": "${step_probe_http_get.data.body_text}",
                      "description": "上游探针节点的 body_text"},
        "forbidden": {"name": "禁止片段", "type": "str", "required": True,
                      "description": "响应中不允许出现的文本"},
    },
)
def check_probe_content_not_contains(body_text, forbidden):
    """响应体反向包含检查。"""
    return lib.check_probe_content_not_contains(body_text, forbidden)


@composer_check(
    name="check_probe_http_status_in",
    description="检查 HTTP 状态码在白名单内（允许 200/302/400/403/404 等，禁止 500）",
    category="probe",
    params={
        "http_status": {"name": "HTTP 状态码", "type": "int", "required": True,
                        "default": "${step_probe_http_get.data.http_status}",
                        "description": "上游探针节点的 http_status"},
        "allowed": {"name": "状态码白名单", "type": "list", "required": True,
                    "description": "允许的 HTTP 状态码列表，如 [200, 302, 400, 403, 404]"},
    },
)
def check_probe_http_status_in(http_status, allowed):
    """HTTP 状态码白名单检查。"""
    return lib.check_probe_http_status_in(http_status, allowed)


@composer_check(
    name="check_probe_no_db_error",
    description="检查响应体不包含 SQL/数据库错误指纹（SQL 注入未穿透数据层）",
    category="probe",
    params={
        "body_text": {"name": "响应体文本", "type": "str", "required": True,
                      "default": "${step_probe_http_get.data.body_text}",
                      "description": "上游探针节点的 body_text"},
    },
)
def check_probe_no_db_error(body_text):
    """数据库错误指纹检查。"""
    return lib.check_probe_no_db_error(body_text)


@composer_check(
    name="check_probe_no_traversal",
    description="检查响应体不包含系统文件指纹（路径穿越未读到 /etc/passwd、win.ini）",
    category="probe",
    params={
        "body_text": {"name": "响应体文本", "type": "str", "required": True,
                      "default": "${step_probe_http_get.data.body_text}",
                      "description": "上游探针节点的 body_text"},
    },
)
def check_probe_no_traversal(body_text):
    """路径穿越文件指纹检查。"""
    return lib.check_probe_no_traversal(body_text)
