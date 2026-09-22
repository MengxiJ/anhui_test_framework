# Copyright (C) 2026. All rights reserved.
"""步骤/检查目录构建器。

扫描注册表（单一事实源）生成：

- ``tblocks/tools/steps_catalog.json``
- ``tblocks/tools/checks_catalog.json``
- ``tblocks/tools/unique_apis.json``（原子节点 → Lib 入口映射）

用法：

    python -m tblocks.tools.build_steps_catalog
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from tblocks.tools.catalog_paths import (
    CHECKS_CATALOG_PATH,
    STEPS_CATALOG_PATH,
    UNIQUE_APIS_PATH,
)


def _registry_to_catalog(items: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    catalog = {}
    for node_id in sorted(items):
        info = items[node_id]
        catalog[node_id] = {
            "id": node_id,
            "name": info.get("name", node_id),
            "description": info.get("description", ""),
            "category": info.get("category", ""),
            "params": info.get("params", {}),
            "pre_conditions": info.get("pre_conditions", []),
            "post_conditions": info.get("post_conditions", []),
        }
    return catalog


def _build_unique_apis(steps: Dict[str, Any], checks: Dict[str, Any]) -> Dict[str, Any]:
    """原子节点与 Lib 入口一一对应（薄封装约定：同名函数）。"""
    apis = {"steps": {}, "checks": {}}
    for node_id in sorted(steps):
        apis["steps"][node_id] = {
            "tblocks_impl": f"tblocks/step_impl/{steps[node_id].get('category', '')}",
            "lib_entry": f"lib.common.{steps[node_id].get('category', '')}.*_step.{node_id}",
        }
    for node_id in sorted(checks):
        apis["checks"][node_id] = {
            "tblocks_impl": f"tblocks/check_impl/{checks[node_id].get('category', '')}",
            "lib_entry": f"lib.common.{checks[node_id].get('category', '')}.*_check.{node_id}",
        }
    return apis


def _write(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def build_all() -> Dict[str, str]:
    """触发注册并写出三个 catalog 文件，返回路径映射。"""
    import tblocks.check_impl  # noqa: F401
    import tblocks.step_impl  # noqa: F401
    from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY

    steps_catalog = _registry_to_catalog(STEP_REGISTRY.all_items())
    checks_catalog = _registry_to_catalog(CHECK_REGISTRY.all_items())
    _write(STEPS_CATALOG_PATH, steps_catalog)
    _write(CHECKS_CATALOG_PATH, checks_catalog)
    _write(UNIQUE_APIS_PATH, _build_unique_apis(steps_catalog, checks_catalog))
    return {
        "steps": STEPS_CATALOG_PATH,
        "checks": CHECKS_CATALOG_PATH,
        "unique_apis": UNIQUE_APIS_PATH,
    }


def main() -> int:
    paths = build_all()
    for kind, path in paths.items():
        print(f"{kind} catalog -> {os.path.relpath(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
