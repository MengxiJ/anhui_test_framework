# Copyright (C) 2026. All rights reserved.
"""原子节点注册表。

注册表是 step/check 的**单一事实源**：装饰器注册、CLI 列举、catalog 构建、
workflow 静态校验均从这里读取。线程安全，注册重名时给出告警（后者覆盖前者）。
"""
from __future__ import annotations

import threading
import warnings
from typing import Any, Dict, List, Optional


class Registry:
    """同类原子节点（step 或 check）的注册表。"""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._items: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def register(self, node_id: str, info: Dict[str, Any], overwrite: bool = True) -> None:
        """注册节点元信息。

        Args:
            node_id: 节点唯一 ID。
            info: 含 name/description/category/params/func 等字段。
            overwrite: 重名是否覆盖（默认覆盖并告警）。
        """
        with self._lock:
            if node_id in self._items and overwrite:
                warnings.warn(
                    f"{self.kind} 节点 ID {node_id!r} 已存在，将被后者覆盖",
                    stacklevel=2,
                )
            if node_id not in self._items or overwrite:
                self._items[node_id] = info

    def has(self, node_id: str) -> bool:
        with self._lock:
            return node_id in self._items

    def get(self, node_id: str) -> Dict[str, Any]:
        with self._lock:
            if node_id not in self._items:
                from lib.core.exceptions import RegistryNotFoundError

                raise RegistryNotFoundError(self.kind, node_id)
            return self._items[node_id]

    def names(self) -> List[str]:
        with self._lock:
            return sorted(self._items)

    def all_items(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return dict(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)


STEP_REGISTRY = Registry("step")
CHECK_REGISTRY = Registry("check")
