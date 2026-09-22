# Copyright (C) 2026. All rights reserved.
"""account 域 step 原子节点（薄封装，仅调用 lib 入口）。

接口步骤返回的 data 中含 ``result``(=业务码 code)、``code``、``http_status``、
``message``、``body``，workflow 中可用 ``${节点.data.code}`` 引用。
"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.account import account_step as lib


@composer_step(
    name="step_account_login",
    description="调用会员登录接口 POST /member/public/login",
    category="account",
    params={
        "keywords": {"name": "手机号", "type": "str", "required": True,
                     "default": "${custom_params.user_phone}", "description": "登录手机号"},
        "password": {"name": "密码", "type": "str", "required": True,
                     "default": "${custom_params.user_password}", "description": "登录密码"},
    },
)
def step_account_login(keywords, password):
    """会员登录接口。"""
    return lib.step_account_login(keywords, password)


@composer_step(
    name="step_account_is_login",
    description="调用登录态校验接口 POST /member/public/isLogin",
    category="account",
)
def step_account_is_login():
    """登录态校验接口。"""
    return lib.step_account_is_login()


@composer_step(
    name="step_account_send_sms",
    description="调用发送短信验证码接口 POST /member/public/sendSms",
    category="account",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True, "description": "接收短信手机号"},
        "img_verify_code": {"name": "图形验证码", "type": "str", "required": False,
                            "default": "8888", "description": "图形验证码"},
        "sms_type": {"name": "短信类型", "type": "str", "required": False,
                     "default": "reg", "description": "reg 注册类短信"},
    },
)
def step_account_send_sms(phone, img_verify_code="8888", sms_type="reg"):
    """发送短信验证码。"""
    return lib.step_account_send_sms(phone, img_verify_code, sms_type=sms_type)


@composer_step(
    name="step_account_get_verifycode",
    description="获取注册图形验证码 GET /common/public/verifycode1/{r}（会话级预热，必须与注册提交同会话）",
    category="account",
)
def step_account_get_verifycode():
    """获取注册图形验证码。"""
    return lib.step_account_get_verifycode()


@composer_step(
    name="step_account_register",
    description="调用会员注册接口 POST /member/public/reg",
    category="account",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True, "description": "注册手机号"},
        "password": {"name": "密码", "type": "str", "required": True, "description": "登录密码"},
        "verifycode": {"name": "图形验证码", "type": "str", "required": False,
                       "default": "8888", "description": "图形验证码"},
        "phone_code": {"name": "短信验证码", "type": "str", "required": False,
                       "default": "666666", "description": "短信验证码"},
        "dy_server": {"name": "协议", "type": "str", "required": False,
                      "default": "on", "description": "是否同意协议"},
        "invite_phone": {"name": "邀请人", "type": "str", "required": False,
                         "default": None, "description": "邀请人手机号，可空"},
    },
)
def step_account_register(phone, password, verifycode="8888", phone_code="666666",
                          dy_server="on", invite_phone=None):
    """会员注册接口。"""
    return lib.step_account_register(
        phone, password, verifycode, phone_code,
        dy_server=dy_server, invite_phone=invite_phone,
    )


@composer_step(
    name="step_account_approve_realname",
    description="调用实名认证接口 POST /member/realname/approverealname",
    category="account",
    params={
        "realname": {"name": "真实姓名", "type": "str", "required": True,
                     "default": "${custom_params.test_name}", "description": "实名"},
        "card_id": {"name": "身份证号", "type": "str", "required": True,
                    "default": "${custom_params.test_id_card}", "description": "身份证号"},
    },
)
def step_account_approve_realname(realname, card_id):
    """实名认证接口。"""
    return lib.step_account_approve_realname(realname, card_id)


@composer_step(
    name="step_account_get_approve",
    description="调用获取认证信息接口 POST /member/member/getapprove",
    category="account",
)
def step_account_get_approve():
    """获取认证信息。"""
    return lib.step_account_get_approve()


@composer_step(
    name="step_account_trust_register",
    description="调用第三方资金托管开户接口 POST /trust/trust/register",
    category="account",
)
def step_account_trust_register():
    """托管开户接口。"""
    return lib.step_account_trust_register()


@composer_step(
    name="step_account_recharge",
    description="调用充值接口 POST /trust/trust/recharge",
    category="account",
    params={
        "amount": {"name": "金额", "type": "str", "required": True, "description": "充值金额"},
        "valicode": {"name": "验证码", "type": "str", "required": False,
                     "default": "8888", "description": "充值图形验证码"},
        "payment_type": {"name": "支付类型", "type": "str", "required": False,
                         "default": "chinapnrTrust", "description": "支付通道"},
    },
)
def step_account_recharge(amount, valicode="8888", payment_type="chinapnrTrust"):
    """充值接口。"""
    return lib.step_account_recharge(amount, valicode, payment_type=payment_type)


@composer_step(
    name="step_account_tender",
    description="调用投资（投标）接口 POST /trust/trust/tender",
    category="account",
    params={
        "amount": {"name": "金额", "type": "str", "required": True, "description": "投资金额"},
        "loan_id": {"name": "产品ID", "type": "int", "required": False,
                    "default": 0, "description": "标的 ID，默认 0"},
        "deposit_certificate": {"name": "存单标识", "type": "int", "required": False,
                                "default": -1, "description": "默认 -1"},
    },
)
def step_account_tender(amount, loan_id=0, deposit_certificate=-1):
    """投资接口。"""
    return lib.step_account_tender(amount, loan_id=loan_id,
                                   deposit_certificate=deposit_certificate)
