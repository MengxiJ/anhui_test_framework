# Copyright (C) 2026. All rights reserved.
"""account 域 Lib 入口：资金账户接口步骤（无装饰器，纯实现）。

每个步骤返回的 ``data`` 中包含：``result``(=业务码 code)、``code``、
``http_status``、``message``、``body``，便于后续 check 节点引用。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.account.utils.account_manager import AccountManager
from lib.common.framework.step_singletons import current_device_id
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "account_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> AccountManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, AccountManager())
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 AccountManager（HTTP 会话随实例关闭）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


def _wrap(step: str, info: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(info)
    data["result"] = info.get("code")
    message = f"接口 {step} 完成，业务码: {info.get('code')}，HTTP: {info.get('http_status')}"
    return step_result(step, True, message, data)


# ---- 登录 / 注册 ----
def step_account_login(keywords: str, password: str) -> Dict[str, Any]:
    """调用会员登录接口。"""
    return _wrap("step_account_login", _get_core().login(keywords, password))


def step_account_is_login() -> Dict[str, Any]:
    """调用登录态校验接口。"""
    return _wrap("step_account_is_login", _get_core().is_login())


def step_account_send_sms(phone: str, img_verify_code: str, sms_type: str = "reg") -> Dict[str, Any]:
    """调用发送短信验证码接口。"""
    return _wrap(
        "step_account_send_sms",
        _get_core().send_sms(phone, img_verify_code, sms_type=sms_type),
    )


def step_account_get_verifycode() -> Dict[str, Any]:
    """获取注册图形验证码（同会话预热，后续提交注册时校验该会话内的验证码）。"""
    info = _get_core().get_verifycode()
    message = f"接口 step_account_get_verifycode 完成，HTTP: {info.get('http_status')}，字节: {info.get('body_length')}"
    data = dict(info)
    data["result"] = info.get("http_status")
    return step_result("step_account_get_verifycode", True, message, data)


def step_account_register(
    phone: str,
    password: str,
    verifycode: str = "8888",
    phone_code: str = "666666",
    dy_server: str = "on",
    invite_phone: Optional[str] = None,
) -> Dict[str, Any]:
    """调用会员注册接口。"""
    return _wrap(
        "step_account_register",
        _get_core().register(
            phone,
            password,
            verifycode,
            phone_code,
            dy_server=dy_server,
            invite_phone=invite_phone,
        ),
    )


# ---- 实名 / 开户 ----
def step_account_approve_realname(realname: str, card_id: str) -> Dict[str, Any]:
    """调用实名认证接口。"""
    return _wrap(
        "step_account_approve_realname",
        _get_core().approve_realname(realname, card_id),
    )


def step_account_get_approve() -> Dict[str, Any]:
    """调用获取认证信息接口。"""
    return _wrap("step_account_get_approve", _get_core().get_approve())


def step_account_trust_register() -> Dict[str, Any]:
    """调用第三方资金托管开户接口。"""
    return _wrap("step_account_trust_register", _get_core().trust_register())


# ---- 充值 / 投资 ----
def step_account_recharge(amount: str, valicode: str, payment_type: str = "chinapnrTrust") -> Dict[str, Any]:
    """调用充值接口。"""
    return _wrap(
        "step_account_recharge",
        _get_core().recharge(amount, valicode, payment_type=payment_type),
    )


def step_account_tender(
    amount,
    loan_id: int = 0,
    deposit_certificate: int = -1,
) -> Dict[str, Any]:
    """调用投资（投标）接口。"""
    return _wrap(
        "step_account_tender",
        _get_core().tender(amount, loan_id=loan_id, deposit_certificate=deposit_certificate),
    )
