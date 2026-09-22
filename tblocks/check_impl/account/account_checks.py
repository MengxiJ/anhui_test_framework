# Copyright (C) 2026. All rights reserved.
"""account 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.account import account_check as lib


@composer_check(
    name="check_account_business_code",
    description="检查接口业务码（成功 200 / 业务失败 100）",
    category="account",
    params={
        "code": {"name": "实际业务码", "type": "int", "required": True,
                 "default": "${step_account_login.data.code}", "description": "上游接口返回 code"},
        "expected": {"name": "期望业务码", "type": "int", "required": False,
                     "default": 200, "enum": [200, 100], "description": "期望业务码"},
    },
)
def check_account_business_code(code, expected=200):
    """业务码检查。"""
    return lib.check_account_business_code(code, expected)


@composer_check(
    name="check_account_http_status",
    description="检查接口 HTTP 状态码",
    category="account",
    params={
        "http_status": {"name": "HTTP 状态码", "type": "int", "required": True,
                        "default": "${step_account_login.data.http_status}",
                        "description": "上游接口 HTTP 状态"},
        "expected": {"name": "期望状态码", "type": "int", "required": False,
                     "default": 200, "description": "期望 HTTP 状态"},
    },
)
def check_account_http_status(http_status, expected=200):
    """HTTP 状态码检查。"""
    return lib.check_account_http_status(http_status, expected)


@composer_check(
    name="check_account_message_contains",
    description="检查接口业务消息包含期望片段",
    category="account",
    params={
        "message": {"name": "业务消息", "type": "str", "required": True,
                    "default": "${step_account_login.data.message}", "description": "上游接口消息"},
        "expected": {"name": "期望片段", "type": "str", "required": True, "description": "期望文本"},
    },
)
def check_account_message_contains(message, expected):
    """业务消息包含检查。"""
    return lib.check_account_message_contains(message, expected)
