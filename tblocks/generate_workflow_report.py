# Copyright (C) 2026. All rights reserved.
"""工作流执行结果报告生成器。

输出到 ``output/tblocks/<时间戳>_<工作流名>/``：

- ``result.json``：完整结构化结果（节点返回值、耗时、失败节点）；
- ``summary.md``：人工可读摘要。
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict

from tblocks.tools.catalog_paths import TBLOCKS_REPORT_DIR


def _safe_name(name: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_\-一-龥]+", "_", str(name)).strip("_")
    return text or "workflow"


def generate_report(result: Dict[str, Any]) -> str:
    """生成 result.json + summary.md，返回报告目录。"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(TBLOCKS_REPORT_DIR, f"{timestamp}_{_safe_name(result.get('name', 'workflow'))}")
    os.makedirs(report_dir, exist_ok=True)

    with open(os.path.join(report_dir, "result.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    with open(os.path.join(report_dir, "summary.md"), "w", encoding="utf-8") as handle:
        handle.write(_render_markdown(result))
    return report_dir


def _render_markdown(result: Dict[str, Any]) -> str:
    status = "PASS" if result.get("status") else "FAIL"
    lines = [
        f"# Workflow 报告：{result.get('name', '')}",
        "",
        f"- 工作流 ID：`{result.get('workflow_id', '')}`",
        f"- 执行结果：**{status}**",
        f"- 失败节点：{result.get('failed_node') or '无'}",
        f"- 结果说明：{result.get('message', '')}",
        f"- 开始时间：{result.get('started_at', '')}",
        f"- 结束时间：{result.get('finished_at', '')}",
        f"- 耗时（秒）：{result.get('duration_seconds', '')}",
        "",
        "## 节点执行明细",
        "",
        "| 序号 | 节点 | 结果 | 说明 |",
        "| ---- | ---- | ---- | ---- |",
    ]
    node_results = result.get("node_results", {})
    for index, node_id in enumerate(result.get("node_order", []), start=1):
        node = node_results.get(node_id, {})
        node_status = "PASS" if node.get("status") else "FAIL"
        message = str(node.get("message", "")).replace("|", "\\|")
        lines.append(f"| {index} | {node_id} | {node_status} | {message} |")
    lines.append("")
    return "\n".join(lines)
