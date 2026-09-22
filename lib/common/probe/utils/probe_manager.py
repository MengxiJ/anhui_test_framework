# Copyright (C) 2026. All rights reserved.
"""通用 HTTP 探针（普通类，类内不做单例）。

面向冒烟连通性与接口级断言，对前台 8081 / 后台 8082 的任意端点发起
GET/POST，并把 ``requests.Response`` 归一化为：

    {
        "http_status": 200,
        "code": 200 / None,          # JSON 体中的 status/code 业务码
        "message": "OK" / None,      # JSON 体中的 description/message
        "content_type": "...",
        "body_length": 31319,
        "body_text": "...",          # 文本响应全文（UTF-8 容错解码）；二进制响应为乱码
        "elapsed_ms": 132,
        "final_url": "http://...",
        "body": {...} / str,
    }

探针不维护业务登录态（每次 ``ProbeManager`` 实例使用独立 requests.Session），
因此特别适合未登录鉴权拦截、公共接口连通性等场景；需要登录态的业务接口
请继续使用 account / backend_admin 域。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.core.base_request import BaseRequest
from lib.core.project_config import BACK_URL, BASE_URL

_SITE_BASE_URLS = {
    "front": BASE_URL,
    "back": BACK_URL,
}

# 说明：页面特征（如登录入口 common/member/login）可能出现在大体积壳页中后段，
# 因此 body_text 保留全文供 contains 断言；报告体积由截图等产物主导，文本可接受。


class ProbeManager:
    """站点级 HTTP 连通性探针。"""

    def __init__(self) -> None:
        self._clients: Dict[str, BaseRequest] = {}

    def _client(self, site: str) -> BaseRequest:
        alias = str(site or "front").strip().lower()
        if alias not in _SITE_BASE_URLS:
            raise ValueError(f"不支持的站点别名: {site!r}，可选: {sorted(_SITE_BASE_URLS)}")
        if alias not in self._clients:
            self._clients[alias] = BaseRequest(base_url=_SITE_BASE_URLS[alias])
        return self._clients[alias]

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
        try:
            body_text = response.content.decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            body_text = str(response.text)
        return {
            "http_status": response.status_code,
            "code": code,
            "message": message,
            "content_type": response.headers.get("Content-Type", ""),
            "body_length": len(response.content),
            "body_text": body_text,
            "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
            "final_url": response.url,
            "body": body,
        }

    def http_get(self, path: str, site: str = "front",
                 allow_redirects: bool = True) -> Dict[str, Any]:
        """GET 探针。path 需以 / 开头，如 ``/``、``/common/public/verifycode1/0.1``。"""
        response = self._client(site).get(
            path, allow_redirects=allow_redirects,
        )
        return self._normalize(response)

    def http_post(self, path: str, data: Optional[Dict[str, Any]] = None,
                  site: str = "front",
                  allow_redirects: bool = True) -> Dict[str, Any]:
        """POST 表单探针（``application/x-www-form-urlencoded``）。"""
        response = self._client(site).post(
            path, data=data or {}, allow_redirects=allow_redirects,
        )
        return self._normalize(response)
