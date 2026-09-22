# Copyright (C) 2026. All rights reserved.
"""TBlocks 层实例管理（委托至 ``lib.core.instance_manager``，全局一份缓存）。

工作流执行器与 TBlocks 节点统一从本模块导入实例生命周期函数：

    from tblocks.utils.instance_manager import (
        initialize_instances, reset_instances, get_instance, clear_instance
    )

本项目无 ADB/物理设备，多设备概念映射为：

- DUT 设备       → Chrome WebDriver（``browser:<device_id>``）
- Controller 通道 → HTTP 客户端 BaseRequest（``api_client:<device_id>``）
"""
from __future__ import annotations

from typing import Any, Optional

from lib.core.instance_manager import (
    clear_instance,
    get_instance,
    has_instance,
    initialize_instances,
    register_instance,
    reset_instances,
)

__all__ = [
    "clear_instance",
    "get_instance",
    "has_instance",
    "initialize_instances",
    "register_instance",
    "reset_instances",
    "get_browser_for_dut",
    "get_browser_for_controller",
    "get_api_channel",
]


def get_browser_for_dut(device_id: Optional[str] = None) -> Any:
    """获取 DUT（默认浏览器）实例，等价 ``step_singletons.get_browser``。"""
    from lib.common.framework.step_singletons import get_browser

    return get_browser(device_id)


def get_browser_for_controller(device_id: Optional[str] = None) -> Any:
    """获取 Controller 浏览器实例（独立 key，默认 ``browser:controller``）。"""
    from lib.common.framework.step_singletons import get_browser

    return get_browser(device_id or "controller")


def get_api_channel(device_id: Optional[str] = None) -> Any:
    """获取第二通信通道（HTTP 客户端）实例。"""
    from lib.common.framework.step_singletons import get_api_client

    return get_api_client(device_id)
