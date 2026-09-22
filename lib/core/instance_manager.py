# Copyright (C) 2026. All rights reserved.
"""实例管理器（线程安全，字符串 key）。

对应框架文档：
- ``lib/core/instance_manager.py``：全局唯一实例缓存；
- 多实例场景使用字符串 key（如 ``browser:default``、``api_client:default``），
  不使用“裸类型”作为 key；
- 工作流开始时可调用 :func:`initialize_instances`，结束（finally）时调用
  :func:`reset_instances` 统一释放资源。

普通业务类不允许在类内自建单例，生命周期统一由本模块托管。
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from lib.core.exceptions import InstanceNotFoundError


class InstanceManager:
    """线程安全的字符串 key 实例容器。"""

    def __init__(self) -> None:
        self._instances: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def has_instance(self, key: str) -> bool:
        """判断指定 key 的实例是否已注册。

        Args:
            key: 实例唯一键。

        Returns:
            是否存在。
        """
        with self._lock:
            return key in self._instances

    def register_instance(self, key: str, instance: Any, overwrite: bool = False) -> Any:
        """注册实例。

        Args:
            key: 实例唯一键。
            instance: 待托管对象。
            overwrite: 已存在时是否覆盖，默认 False 并抛出异常。

        Returns:
            注册后的实例。

        Raises:
            KeyError: key 已存在且 overwrite=False。
        """
        with self._lock:
            if key in self._instances and not overwrite:
                raise KeyError(f"实例 key 已存在且未允许覆盖: {key}")
            self._instances[key] = instance
            return instance

    def get_instance(self, key: str, default: Any = None) -> Any:
        """按 key 获取实例。

        Args:
            key: 实例唯一键。
            default: key 不存在时返回的默认值（不抛异常）。

        Returns:
            托管实例或 default。

        Raises:
            InstanceNotFoundError: key 不存在且未提供 default。
        """
        with self._lock:
            if key in self._instances:
                return self._instances[key]
            if default is not None:
                return default
            raise InstanceNotFoundError(f"实例不存在: {key}")

    def clear_instance(self, key: Optional[str] = None) -> None:
        """清理实例；不传 key 时清空全部。

        若被清理对象实现了 ``close()`` / ``quit()`` 方法，会先尝试调用以释放资源。

        Args:
            key: 可选的实例键。
        """
        with self._lock:
            if key is None:
                targets = list(self._instances.values())
                self._instances.clear()
            elif key in self._instances:
                targets = [self._instances.pop(key)]
            else:
                targets = []
        for obj in targets:
            _safe_release(obj)

    def keys(self) -> list:
        """返回当前全部实例 key。"""
        with self._lock:
            return list(self._instances.keys())

    def __len__(self) -> int:
        with self._lock:
            return len(self._instances)


def _safe_release(obj: Any) -> None:
    """尽力释放对象占用的资源（浏览器驱动、HTTP 会话等）。"""
    for method_name in ("quit", "close", "release"):
        method = getattr(obj, method_name, None)
        if callable(method):
            try:
                method()
                return
            except Exception:  # noqa: BLE001 - 清理动作 best-effort
                continue


# 全局唯一实例管理器（与框架 tblocks.utils.instance_manager 共享同一份缓存）
instance_manager = InstanceManager()


def has_instance(key: str) -> bool:
    """模块级快捷方法：判断实例是否存在。"""
    return instance_manager.has_instance(key)


def register_instance(key: str, instance: Any, overwrite: bool = False) -> Any:
    """模块级快捷方法：注册实例。"""
    return instance_manager.register_instance(key, instance, overwrite=overwrite)


def get_instance(key: str, default: Any = None) -> Any:
    """模块级快捷方法：获取实例。"""
    return instance_manager.get_instance(key, default=default)


def clear_instance(key: Optional[str] = None) -> None:
    """模块级快捷方法：清理实例。"""
    instance_manager.clear_instance(key)


def initialize_instances() -> None:
    """工作流生命周期开始（先清空旧实例，保证隔离）。"""
    instance_manager.clear_instance()


def reset_instances() -> None:
    """工作流生命周期结束（finally 中调用，释放全部资源）。"""
    instance_manager.clear_instance()
