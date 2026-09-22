# Copyright (C) 2026. All rights reserved.
"""Workflow JSON 数据模型与基础校验。

对应 WORKFLOW_JSON.md：

- 顶层必填：``id`` / ``name`` / ``nodes`` / ``edges``；
- 节点 type：step / check / condition / loop；
- step 节点用 ``step_id``，check/condition 用 ``check_id``；
- edge：``source`` / ``target`` / ``condition``(pass/fail/null)。

深度校验（id 是否注册、端点是否存在、参数引用等）见
``tblocks.tools.lego_validator``，本模块只做结构级解析。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from lib.core.exceptions import NodeNotFoundError, WorkflowValidationError

VALID_NODE_TYPES = ("step", "check", "condition", "loop")
VALID_EDGE_CONDITIONS = ("pass", "fail", "null", None)


@dataclass
class Node:
    """工作流节点。"""

    id: str
    type: str
    step_id: Optional[str] = None
    check_id: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    label: str = ""
    description: str = ""
    loop_type: Optional[str] = None
    loop_params: Dict[str, Any] = field(default_factory=dict)
    target_nodes: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    def node_ref(self) -> str:
        """节点实际调用的 step/check 注册表 ID。"""
        return self.step_id if self.type in ("step",) else self.check_id


@dataclass
class Edge:
    """工作流有向边。"""

    source: str
    target: str
    condition: Optional[str] = None
    label: Optional[str] = None
    id: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        condition = data.get("condition")
        if condition not in VALID_EDGE_CONDITIONS:
            raise WorkflowValidationError(
                f"边 {data.get('source')} -> {data.get('target')} 的 condition 非法: {condition!r}"
            )
        return cls(
            source=data["source"],
            target=data["target"],
            condition=condition,
            label=data.get("label"),
            id=data.get("id", ""),
        )


@dataclass
class Workflow:
    """完整工作流定义。"""

    id: str
    name: str
    nodes: List[Node]
    edges: List[Edge]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def node_map(self) -> Dict[str, Node]:
        return {node.id: node for node in self.nodes}

    def get_node(self, node_id: str) -> Node:
        mapping = self.node_map
        if node_id not in mapping:
            raise NodeNotFoundError(f"工作流 {self.id} 中不存在节点: {node_id}")
        return mapping[node_id]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        for required in ("id", "name", "nodes", "edges"):
            if required not in data:
                raise WorkflowValidationError(f"workflow JSON 缺少必填字段: {required}")
        if not isinstance(data["nodes"], list) or not data["nodes"]:
            raise WorkflowValidationError("workflow.nodes 必须是非空数组")
        if not isinstance(data["edges"], list):
            raise WorkflowValidationError("workflow.edges 必须是数组")

        nodes: List[Node] = []
        seen_ids = set()
        for item in data["nodes"]:
            node = _parse_node(item)
            if node.id in seen_ids:
                raise WorkflowValidationError(f"节点 id 重复: {node.id}")
            seen_ids.add(node.id)
            nodes.append(node)

        edges = [Edge.from_dict(item) for item in data["edges"]]

        known = {"id", "name", "nodes", "edges", "description", "metadata"}
        extra = {key: value for key, value in data.items() if key not in known}
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            nodes=nodes,
            edges=edges,
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
            extra=extra,
        )


def _parse_node(item: Dict[str, Any]) -> Node:
    if "id" not in item or "type" not in item:
        raise WorkflowValidationError(f"节点缺少 id/type: {item}")
    node_type = item["type"]
    if node_type not in VALID_NODE_TYPES:
        raise WorkflowValidationError(f"节点 {item['id']} 的 type 非法: {node_type!r}")

    step_id = item.get("step_id")
    check_id = item.get("check_id")
    if node_type == "step" and not step_id:
        raise WorkflowValidationError(f"step 节点 {item['id']} 缺少 step_id")
    if node_type in ("check", "condition") and not check_id:
        raise WorkflowValidationError(f"{node_type} 节点 {item['id']} 缺少 check_id")

    return Node(
        id=str(item["id"]),
        type=node_type,
        step_id=step_id,
        check_id=check_id,
        params=dict(item.get("params", {})),
        label=str(item.get("label", "")),
        description=str(item.get("description", "")),
        loop_type=item.get("loop_type"),
        loop_params=dict(item.get("loop_params", {})),
        target_nodes=list(item.get("target_nodes", [])),
        raw=item,
    )
