# Copyright (C) 2026. All rights reserved.
"""Workflow 执行器：按 nodes/edges 图执行节点。

执行顺序（见 WORKFLOW_JSON.md）：

    setup_hooks(顺序) → setup_hook_graph → 主节点图
        → finally: teardown_hook_graph → teardown_hooks(逆序)

路由：step/check 成功走 ``condition=pass`` 的边，失败走 ``fail`` 的边，
无匹配时回退到 ``condition=null`` 的无条件边，再无则结束当前链。
check “校验不通过”是正常结果（status=False），不是执行异常。
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY
from tblocks.utils.type_caster import cast_value
from tblocks.utils.variable_resolver import VariableResolver
from tblocks.utils.workflow_models import Edge, Node, Workflow
from lib.common.result_helper import now_timestamp
from lib.core.exceptions import WorkflowValidationError
from lib.core.logging_utils import get_logger


class WorkflowExecutor:
    """有状态的工作流执行器（同一实例可被调试器复用做单步 / 序列执行）。"""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.logger = get_logger("tblocks.executor")
        self.context: Dict[str, Any] = {}
        self.custom_params: Dict[str, Any] = {}
        self.node_order: List[str] = []
        self.node_results: Dict[str, Any] = {}
        self.failed_node: Optional[str] = None
        self._current_node_map: Dict[str, Node] = {}

    # ================= 对外主入口 =================
    def run(
        self,
        workflow: Workflow,
        custom_params: Optional[Dict[str, Any]] = None,
        row_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        started_at = now_timestamp()
        start_monotonic = time.monotonic()
        self.custom_params = dict(custom_params or {})
        # 数据驱动：data_rows 中某一行以 ``row`` 为上下文键注入，
        # 节点参数通过 ${row.<字段>} 引用，见 WORKFLOW_JSON.md 数据驱动章节。
        if row_data:
            self.context["row"] = dict(row_data)
        status = True
        message = "工作流执行成功"

        skip_setup, skip_teardown = self._collect_skip_sets(workflow.metadata)

        setup_ok = True
        try:
            if not skip_setup:
                setup_ok = self._run_setup(workflow.metadata)
            if not setup_ok:
                status = False
                message = "setup 阶段失败，主流程未执行"
            else:
                ok, failed_id = self._traverse(workflow.node_map, workflow.edges)
                if not ok:
                    status = False
                    self.failed_node = failed_id
                    message = f"节点 {failed_id} 执行失败或校验未通过"
        finally:
            if not skip_teardown:
                self._run_teardown(workflow.metadata)

        finished_at = now_timestamp()
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "row_id": (row_data or {}).get("row_id"),
            "status": status,
            "message": message,
            "failed_node": self.failed_node,
            "node_order": list(self.node_order),
            "node_results": dict(self.node_results),
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": round(time.monotonic() - start_monotonic, 3),
        }

    # ================= setup / teardown =================
    def _run_setup(self, metadata: Dict[str, Any]) -> bool:
        try:
            for step_id, params in self._iter_hook_steps(metadata.get("setup_hooks")):
                result = self._invoke_registered("step", step_id, params)
                if not result["status"]:
                    return False
            graph = metadata.get("setup_hook_graph")
            if graph:
                ok, _ = self._run_hook_graph(graph)
                return ok
        except Exception as exc:  # noqa: BLE001 - setup 任何异常均阻断，但保证 teardown 执行
            self.logger.error("setup 执行异常: %s", exc)
            return False
        return True

    def _run_teardown(self, metadata: Dict[str, Any]) -> None:
        graph = metadata.get("teardown_hook_graph")
        if graph:
            try:
                self._run_hook_graph(graph)
            except Exception as exc:  # noqa: BLE001 - teardown best-effort
                self.logger.warning("teardown_hook_graph 异常: %s", exc)
        for step_id, params in reversed(list(self._iter_hook_steps(metadata.get("teardown_hooks")))):
            try:
                self._invoke_registered("step", step_id, params)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("teardown step %s 异常: %s", step_id, exc)

    def _run_hook_graph(self, graph: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if not isinstance(graph, dict) or "nodes" not in graph or "edges" not in graph:
            raise WorkflowValidationError("hook graph 必须包含 nodes 与 edges")
        node_map: Dict[str, Node] = {}
        edges: List[Edge] = []
        for item in graph["nodes"]:
            node = Node(
                id=str(item["id"]),
                type=item["type"],
                step_id=item.get("step_id"),
                check_id=item.get("check_id"),
                params=dict(item.get("params", {})),
            )
            node_map[node.id] = node
        for item in graph["edges"]:
            edges.append(Edge(source=item["source"], target=item["target"],
                              condition=item.get("condition")))
        return self._traverse(node_map, edges)

    # ================= 图遍历 =================
    def _traverse(self, node_map: Dict[str, Node], edges: List[Edge]) -> Tuple[bool, Optional[str]]:
        incoming = {node_id: 0 for node_id in node_map}
        for edge in edges:
            if edge.target in incoming:
                incoming[edge.target] += 1
        # loop 体节点由 loop 节点驱动，不作为独立起始节点
        loop_body_ids = set()
        for node in node_map.values():
            if node.type == "loop":
                loop_body_ids.update(
                    target for target in node.target_nodes if target in node_map
                )
        starts = [
            node_id
            for node_id, count in incoming.items()
            if count == 0 and node_id not in loop_body_ids
        ]
        if not starts:
            raise WorkflowValidationError("图中找不到无入边的起始节点")
        if len(starts) > 1:
            self.logger.warning("图含多个起始节点，当前引擎将依次串行执行")

        self._current_node_map = node_map
        for start in starts:
            current: Optional[str] = start
            visited = set()
            while current:
                if current not in node_map:
                    raise WorkflowValidationError(f"边指向了不存在的节点: {current}")
                if current in visited:
                    raise WorkflowValidationError(f"检测到环路，节点 {current} 被重复执行")
                visited.add(current)
                node = node_map[current]
                result = self._execute_node(node)
                status = bool(result["status"])

                edge = self._select_edge(edges, current, status)
                if edge is None:
                    if not status:
                        return False, current
                    current = None
                else:
                    current = edge.target
        return True, None

    @staticmethod
    def _select_edge(edges: List[Edge], node_id: str, status: bool) -> Optional[Edge]:
        wanted = "pass" if status else "fail"
        fallback: Optional[Edge] = None
        for edge in edges:
            if edge.source != node_id:
                continue
            if edge.condition == wanted:
                return edge
            if edge.condition in (None, "null"):
                fallback = edge
        return fallback

    # ================= 节点执行 =================
    def _execute_node(self, node: Node) -> Dict[str, Any]:
        if node.type == "step":
            return self._invoke_registered("step", node.step_id, node.params, context_key=node.id)
        if node.type in ("check", "condition"):
            return self._invoke_registered("check", node.check_id, node.params, context_key=node.id)
        if node.type == "loop":
            return self._execute_loop(node)
        raise WorkflowValidationError(f"不支持的节点类型: {node.type}")

    def _execute_loop(self, node: Node) -> Dict[str, Any]:
        if node.loop_type != "range":
            raise WorkflowValidationError(
                f"当前引擎仅支持 loop_type=range，收到: {node.loop_type!r}"
            )
        if not node.target_nodes:
            raise WorkflowValidationError(f"loop 节点 {node.id} 缺少 target_nodes")
        params = node.loop_params
        start = int(params.get("start", 0))
        stop = int(params.get("stop", 0))
        step = int(params.get("step", 1))
        last_result: Optional[Dict[str, Any]] = None
        for index in range(start, stop, step):
            self.context["loop_index"] = {"data": {"result": index}}
            self.context["loop_current_item"] = {"data": {"result": index, "path": index}}
            for target_id in node.target_nodes:
                # target_nodes 优先解释为主图节点 id（携带自身 params/type），
                # 也支持直接写已注册 step id。
                if target_id in self._current_node_map:
                    last_result = self._execute_node(self._current_node_map[target_id])
                else:
                    last_result = self._invoke_registered(
                        "step", target_id, {}, context_key=target_id
                    )
        result = {
            "step": node.id,
            "status": True,
            "message": f"range 循环完成: range({start}, {stop}, {step})",
            "data": {"result": stop, "iterations": max(0, len(range(start, stop, step)))},
            "timestamp": now_timestamp(),
        }
        self._record(node.id, result)
        return result

    def _invoke_registered(
        self,
        kind: str,
        ref_id: Optional[str],
        params: Dict[str, Any],
        context_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        registry = STEP_REGISTRY if kind == "step" else CHECK_REGISTRY
        node_id = self._resolve_registry_id(registry.has, ref_id, kind)
        info = registry.get(node_id)

        resolver = VariableResolver(self._resolver_context())
        resolved = resolver.resolve(dict(params or {}), strict=True)

        schema = info.get("params", {})
        kwargs: Dict[str, Any] = {}
        for key, value in resolved.items():
            param_type = schema.get(key, {}).get("type") if isinstance(schema.get(key), dict) else None
            kwargs[key] = cast_value(value, param_type) if param_type else value

        self.logger.info("执行 %s 节点: %s，参数: %s", kind, node_id, kwargs)
        result = info["func"](**kwargs)
        self._record(context_key or node_id, result)
        return result

    def _resolver_context(self, extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = dict(self.context)
        context["custom_params"] = self.custom_params
        if extras:
            context.update(extras)
        return context

    @staticmethod
    def _resolve_registry_id(has_func, ref_id: Optional[str], kind: str) -> str:
        if not ref_id:
            raise WorkflowValidationError(f"缺少 {kind} 节点引用 ID")
        if has_func(ref_id):
            return ref_id
        prefixed = f"{kind}_{ref_id}"
        if has_func(prefixed):
            return prefixed
        from lib.core.exceptions import RegistryNotFoundError

        raise RegistryNotFoundError(kind, ref_id)

    def _record(self, key: str, result: Dict[str, Any]) -> None:
        self.context[key] = result
        self.node_results[key] = result
        if key not in self.node_order:
            self.node_order.append(key)

    # ================= hook 工具 =================
    @staticmethod
    def _iter_hook_steps(value: Optional[Any]):
        if not value:
            return
        # 兼容旧写法：hooks 值本身是 {nodes, edges}
        if isinstance(value, dict) and "nodes" in value and "edges" in value:
            return
        for item in value:
            if isinstance(item, str):
                yield item, {}
            elif isinstance(item, dict):
                step_id = item.get("step_id") or item.get("id")
                yield step_id, dict(item.get("params", {}))
            else:
                raise WorkflowValidationError(f"非法 hook 定义: {item!r}")

    def _collect_skip_sets(self, metadata: Dict[str, Any]) -> Tuple[bool, bool]:
        env_skip = {item.strip() for item in os.getenv("TBLOCKS_SKIP_HOOKS", "").split(",") if item.strip()}
        skip_setup = bool(env_skip)
        skip_teardown = bool(env_skip)
        for item in metadata.get("skip_setup_hooks", []):
            skip_setup = True
        for item in metadata.get("skip_teardown_hooks", []):
            skip_teardown = True
        return skip_setup, skip_teardown

    # ================= 调试器复用入口 =================
    def execute_single(self, kind: str, ref_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """单节点执行（结果以节点 ID 为 key 保存到上下文）。"""
        return self._invoke_registered(kind, ref_id, params)

    def execute_sequence(self, sequence: List[Tuple[str, str]], params_map: Dict[str, Dict[str, Any]]):
        """按顺序执行节点序列，节点结果在同一上下文中共享。"""
        results = []
        for kind, ref_id in sequence:
            result = self._invoke_registered(kind, ref_id, params_map.get(ref_id, {}))
            results.append(result)
        return results
