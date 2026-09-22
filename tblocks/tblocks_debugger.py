#!/usr/bin/env python
# Copyright (C) 2026. All rights reserved.
"""TBlocks 工作流调试器 CLI。

支持子命令：

    init                       初始化输出目录并打印环境/注册信息
    list                       列出 step/check 数量概览
    list-steps                 列出全部已注册 step
    list-checks                列出全部已注册 check
    step <step_id>             单步执行 step（--param k=v）
    check <check_id>           单次执行 check
    sequence --flow a,b        按顺序执行节点序列（共享上下文）
    validate --flow a,b        只校验不执行；也可 validate <workflow.json>
    run <workflow.json>        执行完整 workflow
    gate [files...]            装饰器/参数静态门禁（不连接设备）

示例：

    python tblocks/tblocks_debugger.py list-steps
    python tblocks/tblocks_debugger.py step step_add_numbers --param left=2 --param right=3
    python tblocks/tblocks_debugger.py sequence --flow step_add_numbers,check_value_equal ^
        --param check_value_equal.actual=${step_add_numbers.data.result} ^
        --param check_value_equal.expected=5
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from typing import Any, Dict, List, Tuple

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 无条件置顶：脚本直跑时脚本目录（tblocks/）会遮蔽项目根的同名顶层包
# （tblocks/tools 与项目根 tools/），项目根必须排在最前。
sys.path.insert(0, _PROJECT_ROOT)

import tblocks.check_impl  # noqa: F401,E402
import tblocks.step_impl  # noqa: F401,E402
from tblocks.tools.lego_validator import (  # noqa: E402
    ValidationReport,
    gate_impl_files,
    validate_workflow,
    validate_workflow_file,
)
from tblocks.utils.instance_manager import (  # noqa: E402
    initialize_instances,
    reset_instances,
)
from tblocks.utils.registry import CHECK_REGISTRY, STEP_REGISTRY  # noqa: E402
from tblocks.utils.workflow_executor import WorkflowExecutor  # noqa: E402


# ---------------- 通用工具 ----------------
def _parse_value(raw: str) -> Any:
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


def _parse_param(raw: str, default_node: str = "") -> Tuple[str, str, Any]:
    """解析 --param，支持 ``node.key=value`` 与 ``key=value``。"""
    if "=" not in raw:
        raise SystemExit(f"参数格式应为 key=value 或 node.key=value：{raw}")
    key_path, value = raw.split("=", 1)
    key_path = key_path.strip()
    if "." in key_path:
        node_id, param_name = key_path.split(".", 1)
    else:
        node_id, param_name = default_node, key_path
    return node_id, param_name, _parse_value(value)


def _infer_kind(node_id: str) -> str:
    if node_id.startswith("check_"):
        return "check"
    if node_id.startswith("step_"):
        return "step"
    if STEP_REGISTRY.has(node_id):
        return "step"
    if CHECK_REGISTRY.has(node_id):
        return "check"
    raise SystemExit(f"无法识别节点（未注册）：{node_id}")


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_table(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print("（无）")
        return
    width_id = max(len("ID"), max(len(row["id"]) for row in rows))
    width_cat = max(len("分类"), max(len(str(row.get("category", ""))) for row in rows))
    print(f"{'ID':<{width_id}}  {'分类':<{width_cat}}  说明")
    print("-" * (width_id + width_cat + 30))
    for row in rows:
        print(f"{row['id']:<{width_id}}  {row.get('category', ''):<{width_cat}}  {row.get('description', '')}")


def _run_gate() -> bool:
    report = gate_impl_files()
    print(report.render())
    return report.ok


# ---------------- 子命令实现 ----------------
def cmd_init(_args) -> int:
    from lib.core.paths import OUTPUT_DIR

    os.makedirs(os.path.join(OUTPUT_DIR, "log"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "screenshot"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "tblocks"), exist_ok=True)
    print(f"Python: {sys.executable}")
    print(f"输出目录已就绪: {OUTPUT_DIR}")
    print(f"已注册 step: {len(STEP_REGISTRY)} 个，check: {len(CHECK_REGISTRY)} 个")
    return 0


def cmd_list(_args) -> int:
    steps = STEP_REGISTRY.all_items()
    checks = CHECK_REGISTRY.all_items()
    categories = sorted({info.get("category", "") for info in list(steps.values()) + list(checks.values())})
    print(f"step 节点 {len(steps)} 个，check 节点 {len(checks)} 个")
    print(f"业务域: {', '.join(categories)}")
    print("使用 list-steps / list-checks 查看明细")
    return 0


def cmd_list_steps(args) -> int:
    rows = list(STEP_REGISTRY.all_items().values())
    if args.category:
        rows = [row for row in rows if row.get("category") == args.category]
    _print_table(rows)
    return 0


def cmd_list_checks(args) -> int:
    rows = list(CHECK_REGISTRY.all_items().values())
    if args.category:
        rows = [row for row in rows if row.get("category") == args.category]
    _print_table(rows)
    return 0


def _execute_single(kind: str, node_id: str, params: Dict[str, Any], store_key: str = "") -> Tuple[Dict[str, Any], WorkflowExecutor]:
    executor = WorkflowExecutor(verbose=True)
    initialize_instances()
    try:
        result = executor.execute_single(kind, node_id, params)
        if store_key:
            executor.context[store_key] = result
        return result, executor
    finally:
        reset_instances()


def cmd_step(args) -> int:
    if not args.no_gate and not _run_gate():
        return 1
    params: Dict[str, Any] = {}
    for raw in args.param:
        _, name, value = _parse_param(raw, default_node=args.node_id)
        params[name] = value
    result, _ = _execute_single("step", args.node_id, params, store_key=args.store_result_as or "")
    _print_json(result)
    return 0 if result.get("status") else 1


def cmd_check(args) -> int:
    if not args.no_gate and not _run_gate():
        return 1
    params: Dict[str, Any] = {}
    for raw in args.param:
        _, name, value = _parse_param(raw, default_node=args.node_id)
        params[name] = value
    result, _ = _execute_single("check", args.node_id, params, store_key=args.store_result_as or "")
    _print_json(result)
    return 0 if result.get("status") else 1


def _parse_flow(flow: str) -> List[Tuple[str, str]]:
    sequence = []
    for item in flow.split(","):
        node_id = item.strip()
        if node_id:
            sequence.append((_infer_kind(node_id), node_id))
    if not sequence:
        raise SystemExit("--flow 至少包含一个节点")
    return sequence


def _validate_sequence(sequence: List[Tuple[str, str]], params_map: Dict[str, Dict[str, Any]]) -> ValidationReport:
    import inspect

    report = ValidationReport()
    for kind, node_id in sequence:
        registry = STEP_REGISTRY if kind == "step" else CHECK_REGISTRY
        info = registry.get(node_id)
        signature_names = set(inspect.signature(info["raw_func"]).parameters)
        for name in params_map.get(node_id, {}):
            if name not in signature_names:
                report.add_error(f"节点 {node_id} 的参数 {name!r} 不在函数签名中")
    return report


def cmd_sequence(args) -> int:
    if not args.no_gate and not _run_gate():
        return 1
    sequence = _parse_flow(args.flow)

    params_map: Dict[str, Dict[str, Any]] = {}
    for raw in args.param:
        node_id, name, value = _parse_param(raw)
        params_map.setdefault(node_id, {})[name] = value

    report = _validate_sequence(sequence, params_map)
    if not report.ok:
        print(report.render())
        return 1
    if args.validate_only:
        print("序列校验通过：" + ", ".join(node_id for _, node_id in sequence))
        return 0

    executor = WorkflowExecutor(verbose=True)
    initialize_instances()
    all_pass = True
    try:
        for kind, node_id in sequence:
            result = executor._invoke_registered(  # noqa: SLF001 - 调试器内部复用
                kind, node_id, params_map.get(node_id, {})
            )
            _print_json(result)
            if not result.get("status"):
                all_pass = False
                break
        for raw in args.use:
            # --use NODE:KEY[=PARAM]：把已存储上下文注入指定节点（本命令仅做声明校验）
            if ":" not in raw:
                raise SystemExit(f"--use 格式应为 NODE:KEY[=PARAM]：{raw}")
    finally:
        reset_instances()
    return 0 if all_pass else 1


def cmd_validate(args) -> int:
    if not args.no_gate and not _run_gate():
        return 1
    if args.flow:
        sequence = _parse_flow(args.flow)
        params_map: Dict[str, Dict[str, Any]] = {}
        for raw in args.param:
            node_id, name, value = _parse_param(raw)
            params_map.setdefault(node_id, {})[name] = value
        report = _validate_sequence(sequence, params_map)
        print(report.render())
        return 0 if report.ok else 1
    if args.workflow_path:
        report = validate_workflow_file(args.workflow_path)
        print(report.render())
        return 0 if report.ok else 1
    raise SystemExit("validate 需要 --flow 或 workflow 文件路径")


def cmd_run(args) -> int:
    if not args.no_gate and not _run_gate():
        return 1
    from tblocks.workflow_runner import run_workflow

    custom_params: Dict[str, Any] = {}
    for raw in args.custom_param:
        if "=" not in raw:
            raise SystemExit(f"--custom-param 格式 key=value：{raw}")
        key, value = raw.split("=", 1)
        custom_params[key.strip()] = _parse_value(value)

    result = run_workflow(args.workflow_path, custom_params=custom_params)
    _print_json({
        key: result[key]
        for key in ("workflow_id", "name", "status", "message", "failed_node",
                    "node_order", "started_at", "finished_at", "duration_seconds", "report_dir")
        if key in result
    })
    return 0 if result["status"] else 1


def cmd_gate(args) -> int:
    report = gate_impl_files(args.files or None)
    print(report.render())
    return 0 if report.ok else 1


# ---------------- 参数解析 ----------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TBlocks 工作流调试器")
    parser.add_argument("--device-id", default=None, help="逻辑设备 ID（默认 default）")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--timeout", type=float, default=None, help="（预留）单节点超时秒数")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("list").set_defaults(func=cmd_list)

    p = sub.add_parser("list-steps")
    p.add_argument("--category", default=None)
    p.set_defaults(func=cmd_list_steps)

    p = sub.add_parser("list-checks")
    p.add_argument("--category", default=None)
    p.set_defaults(func=cmd_list_checks)

    p = sub.add_parser("step")
    p.add_argument("node_id")
    p.add_argument("--param", action="append", default=[])
    p.add_argument("--store-result-as", default="", dest="store_result_as")
    p.add_argument("--no-gate", action="store_true")
    p.set_defaults(func=cmd_step)

    p = sub.add_parser("check")
    p.add_argument("node_id")
    p.add_argument("--param", action="append", default=[])
    p.add_argument("--store-result-as", default="", dest="store_result_as")
    p.add_argument("--no-gate", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("sequence")
    p.add_argument("--flow", required=True, help="逗号分隔的节点 ID 序列")
    p.add_argument("--param", action="append", default=[])
    p.add_argument("--store", action="append", default=[], help="NODE:KEY 存储上下文别名")
    p.add_argument("--use", action="append", default=[], help="NODE:KEY[=PARAM] 使用上下文")
    p.add_argument("--validate-only", action="store_true", help="只校验序列，不执行")
    p.add_argument("--no-gate", action="store_true")
    p.set_defaults(func=cmd_sequence)

    p = sub.add_parser("validate")
    p.add_argument("workflow_path", nargs="?")
    p.add_argument("--flow", default=None)
    p.add_argument("--param", action="append", default=[])
    p.add_argument("--no-gate", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("run")
    p.add_argument("workflow_path")
    p.add_argument("--custom-param", action="append", default=[])
    p.add_argument("--no-gate", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("gate")
    p.add_argument("files", nargs="*")
    p.add_argument("--import-modules", action="store_true", help="（默认即导入注册模块）")
    p.add_argument("--coverage-file", default=None, help="（预留）覆盖矩阵")
    p.add_argument("--require-coverage", action="store_true", help="（预留）")
    p.set_defaults(func=cmd_gate)
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "device_id", None):
        os.environ["TBLOCKS_DEVICE_ID"] = args.device_id
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
