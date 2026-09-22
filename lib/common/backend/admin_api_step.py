# Copyright (C) 2026. All rights reserved.
"""backend 域 Lib 入口：运营后台 HTTP 接口步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict

from lib.common.backend.utils.admin_manager import AdminManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_KEY = "backend_admin_api:default"


def _get_core() -> AdminManager:
    if not instance_manager.has_instance(_CORE_KEY):
        instance_manager.register_instance(_CORE_KEY, AdminManager())
    return instance_manager.get_instance(_CORE_KEY)


def clear_core() -> None:
    """释放 AdminManager（HTTP 会话随实例关闭）。"""
    instance_manager.clear_instance(_CORE_KEY)


def _wrap(step: str, info: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(info)
    data["result"] = info.get("code")
    message = f"接口 {step} 完成，业务码: {info.get('code')}，HTTP: {info.get('http_status')}"
    return step_result(step, True, message, data)


def step_backend_api_get_verifycode() -> Dict[str, Any]:
    """获取后台登录图形验证码。"""
    return _wrap("step_backend_api_get_verifycode", _get_core().get_verifycode())


def step_backend_api_login(username: str, password: str, valicode: str = "8888",
                           fetch_code: bool = True) -> Dict[str, Any]:
    """后台管理员 HTTP 登录校验（默认先拉图形验证码再提交）。"""
    return _wrap(
        "step_backend_api_login",
        _get_core().login(username, password, valicode=valicode, fetch_code=fetch_code),
    )
