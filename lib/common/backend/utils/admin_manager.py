# Copyright (C) 2026. All rights reserved.
"""后台管理员 HTTP 接口核心类（普通类，类内不做单例）。

把 ``requests.Response`` 归一化为与 account 域一致的结构：

    {
        "http_status": 200,
        "code": 200 / 100 / None,
        "message": "OK" / "用户名/密码错误" / ...,
        "content_type": "application/json;charset=UTF-8",
        "body_length": 33,
        "body": {...} / str,
    }
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.backend.api.admin_api import AdminAPI


class AdminManager:
    """运营后台管理员登录相关 HTTP 接口。"""

    def __init__(self, api_client: Optional[AdminAPI] = None) -> None:
        self.api = api_client or AdminAPI()

    @staticmethod
    def _normalize(response: Any) -> Dict[str, Any]:
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - 非 JSON 响应退化为文本
            body = response.text
        code = message = None
        if isinstance(body, dict):
            code = body.get("code", body.get("status"))
            message = body.get("message", body.get("description"))
        return {
            "http_status": response.status_code,
            "code": code,
            "message": message,
            "content_type": response.headers.get("Content-Type", ""),
            "body_length": len(response.content),
            "body": body,
        }

    def get_verifycode(self) -> Dict[str, Any]:
        """获取后台登录图形验证码（图片响应，回传 HTTP 状态与字节数）。"""
        response = self.api.get_verifycode()
        return {
            "http_status": response.status_code,
            "code": None,
            "message": None,
            "content_type": response.headers.get("Content-Type", ""),
            "body_length": len(response.content),
            "body": "<admin verifycode image>",
        }

    def login(self, username: str, password: str, valicode: str = "8888",
              fetch_code: bool = True) -> Dict[str, Any]:
        """管理员登录。

        fetch_code=True 时先在同一会话拉取图形验证码（教学站固定 8888，
        但服务端要求会话中先存在验证码记录），再提交登录校验。
        """
        if fetch_code:
            self.api.get_verifycode()
        return self._normalize(
            self.api.verify_login(username, password, valicode=valicode)
        )
