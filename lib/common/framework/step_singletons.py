# Copyright (C) 2026. All rights reserved.
"""跨步骤共享实例的集中封装。

按框架规范，TBlocks 层禁止直接 ``register_instance/get_instance`` 拉业务实例，
统一通过本模块的 ``get_*`` / ``has_*`` / ``clear_*`` 访问：

- 浏览器（本项目的 “DUT”）：字符串 key ``browser:<device_id>``，默认 ``browser:default``；
- HTTP 客户端（本项目的 “第二通信通道”）：key ``api_client:<device_id>``。

``device_id`` 缺省时读取环境变量 ``TBLOCKS_DEVICE_ID``（由 workflow_runner /
tblocks_debugger 的 ``--device-id`` 注入），再缺省为 ``default``。
工作流结束时由执行器在 finally 中调用 ``reset_instances()`` 统一释放。
"""
from __future__ import annotations

import os
from typing import Optional

from lib.core import instance_manager

BROWSER_PREFIX = "browser"
API_CLIENT_PREFIX = "api_client"
DEFAULT_DEVICE_ID = "default"


def current_device_id() -> str:
    """当前逻辑设备 ID（多设备隔离用）。"""
    return os.getenv("TBLOCKS_DEVICE_ID", "").strip() or DEFAULT_DEVICE_ID


def browser_key(device_id: Optional[str] = None) -> str:
    """浏览器实例缓存 key。"""
    return f"{BROWSER_PREFIX}:{device_id or current_device_id()}"


def api_client_key(device_id: Optional[str] = None) -> str:
    """HTTP 客户端实例缓存 key。"""
    return f"{API_CLIENT_PREFIX}:{device_id or current_device_id()}"


def get_browser(device_id: Optional[str] = None, headless: Optional[bool] = None):
    """获取（懒创建）共享 Chrome WebDriver。

    Args:
        device_id: 逻辑设备 ID，缺省取 ``TBLOCKS_DEVICE_ID``。
        headless: 是否无头，None 时由工厂读 ``TBLOCKS_HEADLESS``。

    Returns:
        selenium.webdriver.Chrome 实例。
    """
    key = browser_key(device_id)
    if not instance_manager.has_instance(key):
        # 局部导入，避免无浏览器环境（如离线 demo、纯 collect）强依赖 selenium。
        from lib.core.browser_driver import create_chrome_driver

        instance_manager.register_instance(key, create_chrome_driver(headless=headless))
    return instance_manager.get_instance(key)


def has_browser(device_id: Optional[str] = None) -> bool:
    """浏览器实例是否已创建。"""
    return instance_manager.has_instance(browser_key(device_id))


def clear_browser(device_id: Optional[str] = None) -> None:
    """释放浏览器实例（会调用 driver.quit）。"""
    instance_manager.clear_instance(browser_key(device_id))


def get_api_client(device_id: Optional[str] = None, max_retries: int = 3, timeout: int = 30):
    """获取（懒创建）共享 HTTP 客户端（``api.base_request.BaseRequest``）。"""
    key = api_client_key(device_id)
    if not instance_manager.has_instance(key):
        from lib.core.http_client import create_api_client

        instance_manager.register_instance(
            key, create_api_client(max_retries=max_retries, timeout=timeout)
        )
    return instance_manager.get_instance(key)


def has_api_client(device_id: Optional[str] = None) -> bool:
    """HTTP 客户端实例是否已创建。"""
    return instance_manager.has_instance(api_client_key(device_id))


def clear_api_client(device_id: Optional[str] = None) -> None:
    """释放 HTTP 客户端实例。"""
    instance_manager.clear_instance(api_client_key(device_id))
