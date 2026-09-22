# Copyright (C) 2026. All rights reserved.
"""资金账户接口核心类（普通类，类内不做单例）。

包装 ``LoginRegisterAPI``，把 requests.Response 归一化为结构化字典：

    {
        "http_status": 200,
        "code": 200 / 100 / None,      # 业务码（非 JSON 响应时为 None）
        "message": "……",               # 业务消息
        "body": {...} / str,           # 原始响应体
    }
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.account.utils.login_register_api import LoginRegisterAPI


class AccountManager:
    """会员 / 资金账户相关接口。"""

    def __init__(self, api_client: Optional[LoginRegisterAPI] = None) -> None:
        self.api = api_client or LoginRegisterAPI()

    @staticmethod
    def _normalize(response: Any) -> Dict[str, Any]:
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - 非 JSON 响应退化为文本
            body = response.text
        # 站点实际返回 {"status": 200/100, "description": "..."}，兼容 code/message 风格
        code = None
        message = None
        if isinstance(body, dict):
            code = body.get("code", body.get("status"))
            message = body.get("message", body.get("description"))
        return {
            "http_status": response.status_code,
            "code": code,
            "message": message,
            "body": body,
        }

    # ---- 登录 / 注册 ----
    def login(self, keywords: str, password: str) -> Dict[str, Any]:
        """会员登录接口。"""
        return self._normalize(self.api.login(keywords, password))

    def is_login(self) -> Dict[str, Any]:
        """登录态校验接口。"""
        return self._normalize(self.api.is_login())

    def get_verifycode(self, r: Optional[float] = None) -> Dict[str, Any]:
        """获取注册图形验证码（图片响应，只回传 HTTP 状态与图片字节数）。"""
        response = self.api.get_verifycode(r)
        return {"http_status": response.status_code, "code": None,
                "message": None,
                "content_type": response.headers.get("Content-Type", ""),
                "body_length": len(response.content),
                "body": "<verifycode image>"}

    def send_sms(self, phone: str, img_verify_code: str, sms_type: str = "reg") -> Dict[str, Any]:
        """发送短信验证码。"""
        return self._normalize(self.api.send_sms(phone, img_verify_code, type=sms_type))

    def register(
        self,
        phone: str,
        password: str,
        verifycode: str,
        phone_code: str,
        dy_server: str = "on",
        invite_phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """会员注册接口。"""
        return self._normalize(
            self.api.register(
                phone,
                password,
                verifycode,
                phone_code,
                dy_server=dy_server,
                invite_phone=invite_phone,
            )
        )

    # ---- 实名 / 开户 ----
    def approve_realname(self, realname: str, card_id: str) -> Dict[str, Any]:
        """实名认证接口。"""
        return self._normalize(self.api.approve_realname(realname, card_id))

    def get_approve(self) -> Dict[str, Any]:
        """获取实名/开户认证信息接口。"""
        return self._normalize(self.api.get_approve())

    def trust_register(self) -> Dict[str, Any]:
        """第三方资金托管开户接口。"""
        return self._normalize(self.api.trust_register())

    # ---- 充值 / 投资 ----
    def get_recharge_verifycode(self, r: Optional[float] = None) -> Dict[str, Any]:
        """获取充值图形验证码（图片响应，只回传 HTTP 状态与图片字节数）。"""
        response = self.api.get_recharge_verifycode(r)
        return {"http_status": response.status_code, "code": None,
                "message": None,
                "content_type": response.headers.get("Content-Type", ""),
                "body_length": len(response.content),
                "body": "<verifycode image>"}

    def recharge(
        self,
        amount: str,
        valicode: str,
        payment_type: str = "chinapnrTrust",
        form_str: str = "reForm",
    ) -> Dict[str, Any]:
        """充值接口。"""
        return self._normalize(
            self.api.recharge(
                payment_type=payment_type,
                amount=amount,
                form_str=form_str,
                valicode=valicode,
            )
        )

    def tender(self, amount, loan_id: int = 0, deposit_certificate: int = -1) -> Dict[str, Any]:
        """投资（投标）接口。"""
        return self._normalize(
            self.api.tender(
                loan_id=loan_id,
                deposit_certificate=deposit_certificate,
                amount=amount,
            )
        )
