# Copyright (C) 2026. All rights reserved.
"""Workflow JSON 静态校验与原子节点实现门禁（gate）。

两类检查：

1. ``validate_workflow``：结构、节点 id 唯一、step/check 已注册、
   边端点存在、参数在 catalog 中声明、明显的变量引用问题；
2. ``gate_impl_files``：基于 AST 检查 step_impl/check_impl 源码：

   - 一个函数绑定多个 @composer_step/@composer_check；
   - 装饰器参数使用 JSON 风格 true/false/null（应为 True/False/None）；
   - params 声明的参数未出现在函数签名中。
"""
from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tblocks.tools.catalog_paths import CHECK_IMPL_DIR, STEP_IMPL_DIR

_COMPOSER_DECORATORS = {"composer_step", "composer_check"}
_JSON_NAME_CONSTANTS = {"true", "false", "null"}


@dataclass
class ValidationReport:
    """校验报告。"""

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationReport") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def render(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"错误 {len(self.errors)} 项：")
            lines.extend(f"  [ERROR] {item}" for item in self.errors)
        if self.warnings:
            lines.append(f"警告 {len(self.warnings)} 项：")
            lines.extend(f"  [WARN]  {item}" for item in self.warnings)
        if self.ok and not self.warnings:
            lines.append("校验通过，未发现问题")
        elif self.ok:
            lines.append("校验通过（存在警告）")
        return "\n".join(lines)


# ======================== Workflow 校验 ========================
def validate_workflow(
    workflow_data: Dict[str, Any],
    source: str = "<workflow>",
    check_registry: bool = True,
) -> ValidationReport:
    """校验单个 workflow JSON 字典。"""
    report = ValidationReport()

    for required in ("id", "name", "nodes", "edges"):
        if required not in workflow_data:
            report.add_error(f"{source}: 缺少必填字段 {required!r}")
    if report.errors:
        return report

    nodes = workflow_data.get("nodes", [])
    edges = workflow_data.get("edges", [])
    if not isinstance(nodes, list) or not nodes:
        report.add_error(f"{source}: nodes 必须是非空数组")
        return report
    if not isinstance(edges, list):
        report.add_error(f"{source}: edges 必须是数组")
        return report

    # 延迟导入注册表（需先完成装饰器注册）
    step_names = set()
    check_names = set()
    if check_registry:
        from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY

        step_names = set(STEP_REGISTRY.names())
        check_names = set(CHECK_REGISTRY.names())

    node_ids: List[str] = []
    for index, node in enumerate(nodes):
        prefix = f"{source}: 第 {index + 1} 个节点"
        if not isinstance(node, dict) or "id" not in node or "type" not in node:
            report.add_error(f"{prefix} 缺少 id/type")
            continue
        node_id = node["id"]
        if node_id in node_ids:
            report.add_error(f"{prefix} 节点 id 重复: {node_id}")
        node_ids.append(node_id)

        node_type = node["type"]
        ref_id = None
        if node_type == "step":
            ref_id = node.get("step_id")
            if not ref_id:
                report.add_error(f"{prefix}({node_id}) 缺少 step_id")
            elif check_registry and ref_id not in step_names:
                report.add_error(f"{node_id}: step_id 未注册: {ref_id}")
        elif node_type in ("check", "condition"):
            ref_id = node.get("check_id")
            if not ref_id:
                report.add_error(f"{prefix}({node_id}) 缺少 check_id")
            elif check_registry and ref_id not in check_names:
                report.add_error(f"{node_id}: check_id 未注册: {ref_id}")
        elif node_type == "loop":
            if node.get("loop_type") != "range":
                report.add_warning(f"{node_id}: 当前引擎仅实现 loop_type=range")
            if not node.get("target_nodes"):
                report.add_error(f"{node_id}: loop 节点缺少 target_nodes")
        else:
            report.add_error(f"{prefix}({node_id}) type 非法: {node_type!r}")

        _validate_node_params(node, ref_id, node_type, source, report,
                              step_names, check_names)

    node_id_set = set(node_ids)
    for index, edge in enumerate(edges):
        prefix = f"{source}: 第 {index + 1} 条边"
        if not isinstance(edge, dict) or "source" not in edge or "target" not in edge:
            report.add_error(f"{prefix} 缺少 source/target")
            continue
        if edge["source"] not in node_id_set:
            report.add_error(f"{prefix} source 节点不存在: {edge['source']}")
        if edge["target"] not in node_id_set:
            report.add_error(f"{prefix} target 节点不存在: {edge['target']}")
        condition = edge.get("condition")
        if condition not in ("pass", "fail", "null", None):
            report.add_error(f"{prefix} condition 非法: {condition!r}")

    _validate_hooks(workflow_data.get("metadata", {}), source, report, step_names)
    _validate_data_rows(workflow_data, source, report)
    return report


def _validate_data_rows(workflow_data: Dict[str, Any], source: str, report: ValidationReport) -> None:
    """校验数据驱动 ``data_rows``：非空对象数组、row_id 唯一；${row.x} 引用闭合。"""
    import re

    rows = workflow_data.get("data_rows")
    # 收集节点参数中全部 ${row.<field>} 引用
    row_refs = set()
    for node in workflow_data.get("nodes", []):
        params = node.get("params", {})
        if not isinstance(params, dict):
            continue

        def _walk(value: Any) -> None:
            if isinstance(value, str):
                for match in re.finditer(r"\$\{row\.([a-zA-Z_][\w]*)\}", value):
                    row_refs.add(match.group(1))
            elif isinstance(value, dict):
                for item in value.values():
                    _walk(item)
            elif isinstance(value, list):
                for item in value:
                    _walk(item)

        _walk(params)

    if rows is None:
        if row_refs:
            report.add_error(f"{source}: 节点引用了 ${{row.*}} 但缺少顶层 data_rows 定义")
        return
    if not isinstance(rows, list) or not rows:
        report.add_error(f"{source}: data_rows 必须是非空数组")
        return
    row_keys: set = set()
    seen_ids: set = set()
    for index, row in enumerate(rows):
        prefix = f"{source}: data_rows 第 {index + 1} 行"
        if not isinstance(row, dict):
            report.add_error(f"{prefix} 必须是对象")
            continue
        row_id = row.get("row_id")
        if not row_id or not str(row_id).strip():
            report.add_error(f"{prefix} 缺少非空 row_id")
        elif str(row_id) in seen_ids:
            report.add_error(f"{prefix} row_id 重复: {row_id}")
        else:
            seen_ids.add(str(row_id))
        row_keys.update(row.keys())
    missing = sorted(ref for ref in row_refs if ref not in row_keys and ref != "row_id")
    for ref in missing:
        report.add_error(f"{source}: ${{row.{ref}}} 在所有 data_rows 中均无对应字段")


def _validate_node_params(node, ref_id, node_type, source, report, step_names, check_names):
    params = node.get("params", {})
    if not isinstance(params, dict):
        report.add_error(f"{source}: 节点 {node['id']} params 必须是对象")
        return
    if not ref_id or not (step_names or check_names):
        return
    try:
        from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY

        registry = STEP_REGISTRY if node_type == "step" else CHECK_REGISTRY
        info = registry.all_items().get(ref_id)
    except Exception:  # noqa: BLE001
        return
    if not info:
        return
    schema = info.get("params", {})
    raw_func = info.get("raw_func")
    signature_names = set()
    if raw_func is not None:
        import inspect

        signature_names = set(inspect.signature(raw_func).parameters)
    for key, value in params.items():
        if schema and key not in schema:
            report.add_warning(
                f"{source}: 节点 {node['id']} 参数 {key!r} 未在 {ref_id} 的 params 中声明"
            )
        if signature_names and key not in signature_names:
            report.add_error(
                f"{source}: 节点 {node['id']} 参数 {key!r} 不在 {ref_id} 函数签名中"
            )
        if isinstance(value, str) and "${" in value and "}" not in value:
            report.add_warning(f"{source}: 节点 {node['id']} 参数 {key!r} 疑似残缺变量引用")


def _validate_hooks(metadata, source, report, step_names):
    if not isinstance(metadata, dict):
        return
    for hook_key in ("setup_hooks", "teardown_hooks"):
        hooks = metadata.get(hook_key)
        if not hooks:
            continue
        if isinstance(hooks, dict):
            report.add_warning(f"{source}: {hook_key} 建议改用 *_hook_graph 写法")
            continue
        if not isinstance(hooks, list):
            report.add_error(f"{source}: {hook_key} 必须是数组")
            continue
        for hook in hooks:
            step_id = hook if isinstance(hook, str) else hook.get("step_id") or hook.get("id")
            if step_names and step_id not in step_names:
                report.add_error(f"{source}: {hook_key} 引用了未注册 step: {step_id}")
    for graph_key in ("setup_hook_graph", "teardown_hook_graph"):
        graph = metadata.get(graph_key)
        if graph:
            sub_report = validate_workflow(
                {"id": f"{source}:{graph_key}", "name": graph_key,
                 "nodes": graph.get("nodes", []), "edges": graph.get("edges", [])},
                source=f"{source}:{graph_key}",
            )
            report.merge(sub_report)


def validate_workflow_file(path: str, check_registry: bool = True) -> ValidationReport:
    """从文件加载并校验 workflow。"""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return validate_workflow(data, source=path, check_registry=check_registry)


# ======================== AST gate ========================
def gate_impl_files(file_paths: Optional[List[str]] = None) -> ValidationReport:
    """对 step_impl/check_impl Python 文件执行 AST 门禁检查。"""
    if not file_paths:
        file_paths = _collect_impl_files()
    report = ValidationReport()
    for path in file_paths:
        report.merge(_gate_single_file(path))
    return report


def _collect_impl_files() -> List[str]:
    files = []
    for root_dir in (STEP_IMPL_DIR, CHECK_IMPL_DIR):
        for base, _, names in os.walk(root_dir):
            for name in names:
                if name.endswith(".py") and name != "__init__.py":
                    files.append(os.path.join(base, name))
    return sorted(set(files))


def _gate_single_file(path: str) -> ValidationReport:
    report = ValidationReport()
    try:
        with open(path, encoding="utf-8") as handle:
            tree = ast.parse(handle.read(), filename=path)
    except SyntaxError as exc:
        report.add_error(f"{path}:{exc.lineno}: 语法错误: {exc.msg}")
        return report

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        composer_decos = [
            deco for deco in node.decorator_list
            if _is_composer_decorator(deco)
        ]
        if len(composer_decos) > 1:
            report.add_error(
                f"{path}:{node.lineno}: 函数 {node.name!r} 绑定了多个 composer 装饰器"
            )
        for deco in composer_decos:
            _check_decorator_arguments(path, node, deco, report)
    return report


def _is_composer_decorator(deco: ast.expr) -> bool:
    call = deco if isinstance(deco, ast.Call) else None
    func = getattr(call, "func", None)
    if isinstance(func, ast.Name) and func.id in _COMPOSER_DECORATORS:
        return True
    if isinstance(func, ast.Attribute) and func.attr in _COMPOSER_DECORATORS:
        return True
    return False


def _check_decorator_arguments(path, func_node, deco: ast.Call, report) -> None:
    # 1) JSON 风格 true/false/null（Python 中会被解析为 Name 节点）
    for child in ast.walk(deco):
        if isinstance(child, ast.Name) and child.id in _JSON_NAME_CONSTANTS:
            report.add_error(
                f"{path}:{child.lineno}: 装饰器参数使用了 JSON 风格 {child.id!r}，"
                f"请改用 Python 字面量 True/False/None（函数 {func_node.name}）"
            )

    # 2) params 声明的参数必须出现在函数签名中
    signature_names = {arg.arg for arg in func_node.args.args}
    signature_names.update(arg.arg for arg in func_node.args.kwonlyargs)
    for keyword in deco.keywords:
        if keyword.arg != "params" or not isinstance(keyword.value, ast.Dict):
            continue
        for key_node in keyword.value.keys:
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                if key_node.value not in signature_names:
                    report.add_error(
                        f"{path}:{key_node.lineno}: 声明的参数 {key_node.value!r} "
                        f"未出现在函数 {func_node.name} 的签名中"
                    )


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else None
    result = validate_workflow_file(target) if target and target.endswith(".json") else gate_impl_files(
        [target] if target else None
    )
    print(result.render())
    sys.exit(0 if result.ok else 1)
