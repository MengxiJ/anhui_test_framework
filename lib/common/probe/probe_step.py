# Copyright (C) 2026. All rights reserved.
"""probe 域 Lib 入口：通用 HTTP 探针步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.probe.utils.probe_manager import ProbeManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_KEY = "probe_core:default"


def _get_core() -> ProbeManager:
    if not instance_manager.has_instance(_CORE_KEY):
        instance_manager.register_instance(_CORE_KEY, ProbeManager())
    return instance_manager.get_instance(_CORE_KEY)


def clear_core() -> None:
    """释放 ProbeManager（HTTP 会话随实例关闭）。"""
    instance_manager.clear_instance(_CORE_KEY)


def _wrap(step: str, site: str, path: str, info: Dict[str, Any]) -> Dict[str, Any]:
    message = (
        f"探针 {step} {site.upper()} {path} -> HTTP {info.get('http_status')}，"
        f"字节 {info.get('body_length')}，耗时 {info.get('elapsed_ms')}ms"
    )
    return step_result(step, True, message, dict(info))


def step_probe_http_get(path: str, site: str = "front",
                        allow_redirects: bool = True) -> Dict[str, Any]:
    """对指定站点发起 GET 连通性探针。"""
    info = _get_core().http_get(
        path, site=site, allow_redirects=allow_redirects,
    )
    return _wrap("step_probe_http_get", site, path, info)


def step_probe_http_post(path: str, data: Optional[Dict[str, Any]] = None,
                         site: str = "front",
                         allow_redirects: bool = True) -> Dict[str, Any]:
    """对指定站点发起 POST 表单探针。"""
    info = _get_core().http_post(path, data=data, site=site,
                                 allow_redirects=allow_redirects)
    return _wrap("step_probe_http_post", site, path, info)
