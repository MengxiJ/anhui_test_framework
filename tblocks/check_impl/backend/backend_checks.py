# Copyright (C) 2026. All rights reserved.
"""backend 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.backend import admin_api_check as lib_api
from lib.common.backend import backend_check as lib


# ---- 后台 8082 HTTP 接口检查 ----
@composer_check(
    name="check_backend_api_business_code",
    description="检查后台接口业务码（200 成功 / 100 业务失败）",
    category="backend",
    params={
        "code": {"name": "实际业务码", "type": "int", "required": True,
                 "default": "${step_backend_api_login.data.code}",
                 "description": "上游后台接口返回 code"},
        "expected": {"name": "期望业务码", "type": "int", "required": False,
                     "default": 200, "enum": [200, 100], "description": "期望业务码"},
    },
)
def check_backend_api_business_code(code, expected=200):
    """后台接口业务码检查。"""
    return lib_api.check_backend_api_business_code(code, expected)


@composer_check(
    name="check_backend_api_http_status",
    description="检查后台接口 HTTP 状态码",
    category="backend",
    params={
        "http_status": {"name": "HTTP 状态码", "type": "int", "required": True,
                        "default": "${step_backend_api_login.data.http_status}",
                        "description": "上游后台接口 HTTP 状态"},
        "expected": {"name": "期望状态码", "type": "int", "required": False,
                     "default": 200, "description": "期望 HTTP 状态"},
    },
)
def check_backend_api_http_status(http_status, expected=200):
    """后台接口 HTTP 状态码检查。"""
    return lib_api.check_backend_api_http_status(http_status, expected)


@composer_check(
    name="check_backend_api_message_contains",
    description="检查后台接口业务消息包含期望片段",
    category="backend",
    params={
        "message": {"name": "业务消息", "type": "str", "required": True,
                    "default": "${step_backend_api_login.data.message}",
                    "description": "上游后台接口消息"},
        "expected": {"name": "期望片段", "type": "str", "required": True,
                     "description": "期望文本，如 OK、用户名/密码错误"},
    },
)
def check_backend_api_message_contains(message, expected):
    """后台接口业务消息包含检查。"""
    return lib_api.check_backend_api_message_contains(message, expected)


@composer_check(
    name="check_backend_api_verifycode_size",
    description="检查后台图形验证码响应字节数不小于阈值",
    category="backend",
    params={
        "body_length": {"name": "响应字节数", "type": "int", "required": True,
                        "default": "${step_backend_api_get_verifycode.data.body_length}",
                        "description": "验证码图片字节数"},
        "min_length": {"name": "最小字节数", "type": "int", "required": False,
                       "default": 1000, "description": "图片最小字节阈值"},
    },
)
def check_backend_api_verifycode_size(body_length, min_length=1000):
    """后台图形验证码字节数检查。"""
    return lib_api.check_backend_api_verifycode_size(body_length, min_length)


@composer_check(
    name="check_backend_login_result_contains",
    description="检查后台登录结果文本包含期望内容（如“欢迎光临”）",
    category="backend",
    params={"expected": {"name": "期望文本", "type": "str", "required": True,
                         "default": "欢迎光临", "description": "登录成功标识"}},
)
def check_backend_login_result_contains(expected="欢迎光临"):
    """后台登录结果检查。"""
    return lib.check_backend_login_result_contains(expected)


@composer_check(
    name="check_loan_review_status",
    description="检查额度审核记录状态文本精确等于期望值",
    category="backend",
    params={"expected": {"name": "期望状态", "type": "str", "required": False,
                         "default": "通过", "description": "审核状态"}},
)
def check_loan_review_status(expected="通过"):
    """额度审核状态精确检查。"""
    return lib.check_loan_review_status(expected)


@composer_check(
    name="check_loan_review_status_contains",
    description="检查额度审核状态文本包含期望内容",
    category="backend",
    params={"expected": {"name": "期望文本", "type": "str", "required": False,
                         "default": "通过", "description": "审核状态片段"}},
)
def check_loan_review_status_contains(expected="通过"):
    """额度审核状态包含检查。"""
    return lib.check_loan_review_status_contains(expected)
