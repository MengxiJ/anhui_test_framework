# Copyright (C) 2026. All rights reserved.
"""HTTP 客户端工厂。

基于原子化项目自包含的 ``lib.core.base_request.BaseRequest``
（Session + 5xx 重试 + 超时）创建统一请求客户端。
"""
from __future__ import annotations

from lib.core.base_request import BaseRequest


def create_api_client(max_retries: int = 3, timeout: int = 30) -> BaseRequest:
    """创建带重试与超时配置的 API 客户端。

    Args:
        max_retries: 5xx 状态码最大重试次数。
        timeout: 请求超时秒数。

    Returns:
        BaseRequest 实例。
    """
    return BaseRequest(max_retries=max_retries, timeout=timeout)
