#!/usr/bin/env python
# Copyright (C) 2026. All rights reserved.
"""Workflow 执行主入口 CLI。

示例：

    python tblocks/workflow_runner.py --workflow-path tblocks/workflows/demo/demo_math_offline.json
    python tblocks/workflow_runner.py --workflow-path tblocks/workflows/api/api_login.json \
        --custom-param keywords=18800002008 --device-id default --verbose

生命周期：initialize_instances() → 执行（setup hooks → 主图 → teardown hooks）
→ finally: reset_instances()。退出码 0 表示 PASS，1 表示 FAIL。
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from typing import Any, Dict, List

# 允许 `python tblocks/workflow_runner.py` 直接运行（把项目根加入 sys.path）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 无条件置顶：脚本直跑时脚本目录（tblocks/）会遮蔽项目根的同名顶层包
# （tblocks/tools 与项目根 tools/），项目根必须排在最前。
sys.path.insert(0, _PROJECT_ROOT)

import tblocks.check_impl  # noqa: F401,E402  - 触发 check 注册
import tblocks.step_impl  # noqa: F401,E402  - 触发 step 注册
from tblocks.generate_workflow_report import generate_report  # noqa: E402
from tblocks.tools.lego_validator import validate_workflow_file  # noqa: E402
from tblocks.utils.instance_manager import (  # noqa: E402
    initialize_instances,
    reset_instances,
)
from tblocks.utils.workflow_executor import WorkflowExecutor  # noqa: E402
from tblocks.utils.workflow_models import Workflow  # noqa: E402


def parse_custom_param(raw: str) -> Dict[str, Any]:
    """解析 ``key=value`` 参数，value 支持 Python 字面量（200/True/None/[...]）。"""
    if "=" not in raw:
        raise argparse.ArgumentTypeError(f"台架参数格式应为 key=value：{raw}")
    key, value = raw.split("=", 1)
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        parsed = value
    return {key.strip(): parsed}


def merge_custom_params(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for item in items:
        merged.update(item)
    return merged


def load_workflow(path: str) -> Workflow:
    with open(path, encoding="utf-8") as handle:
        return Workflow.from_dict(json.load(handle))


def run_workflow(
    workflow_path: str,
    custom_params: Dict[str, Any] | None = None,
    skip_validation: bool = False,
    write_report: bool = True,
) -> Dict[str, Any]:
    """加载、校验并执行一个 workflow，返回执行结果。"""
    if not skip_validation:
        report = validate_workflow_file(workflow_path)
        for warning in report.warnings:
            print(f"[WARN] {warning}")
        if not report.ok:
            print(report.render())
            raise SystemExit(1)

    workflow = load_workflow(workflow_path)
    rows = workflow.extra.get("data_rows")

    if rows:
        return _run_data_rows(workflow, rows, custom_params or {})

    initialize_instances()
    try:
        result = WorkflowExecutor().run(workflow, custom_params=custom_params or {})
    finally:
        reset_instances()

    if write_report:
        report_dir = generate_report(result)
        result["report_dir"] = report_dir
    return result


def _run_data_rows(
    workflow: Workflow,
    rows: List[Dict[str, Any]],
    custom_params: Dict[str, Any],
) -> Dict[str, Any]:
    """数据驱动工作流逐行执行：每行独立实例/会话，汇总为一个结果。"""
    row_results: List[Dict[str, Any]] = []
    total = 0.0
    for index, row in enumerate(rows):
        row_id = row.get("row_id", f"row{index}")
        initialize_instances()
        try:
            result = WorkflowExecutor().run(
                workflow, custom_params=custom_params, row_data=row
            )
        finally:
            reset_instances()
        total += float(result.get("duration_seconds") or 0)
        row_results.append({"row_id": row_id, "status": result["status"],
                            "failed_node": result.get("failed_node"),
                            "message": result.get("message"),
                            "duration_seconds": result.get("duration_seconds")})
        flag = "PASS" if result["status"] else "FAIL"
        print(f"  [{flag}] {row_id} ({result.get('duration_seconds')}s)"
              + ("" if result["status"] else f" -> {result.get('failed_node')}"))
    passed = sum(1 for item in row_results if item["status"])
    aggregate = {
        "workflow_id": workflow.id,
        "name": workflow.name,
        "status": passed == len(row_results),
        "message": f"数据驱动 {passed}/{len(row_results)} 行通过",
        "failed_node": next(
            (item["failed_node"] for item in row_results if not item["status"]), None
        ),
        "node_order": [],
        "node_results": {},
        "data_rows": row_results,
        "duration_seconds": round(total, 3),
    }
    return aggregate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="原子化 workflow 执行器")
    parser.add_argument("--workflow-path", required=True, help="workflow JSON 路径")
    parser.add_argument(
        "--custom-param",
        action="append",
        default=[],
        type=parse_custom_param,
        help="台架参数 key=value，可重复传入",
    )
    parser.add_argument("--device-id", default=None, help="逻辑设备 ID（默认 default）")
    parser.add_argument("--verbose", action="store_true", help="打印详细节点信息")
    parser.add_argument("--skip-validation", action="store_true", help="跳过 lego 静态校验")
    parser.add_argument("--no-report", action="store_true", help="不生成结果报告文件")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.device_id:
        os.environ["TBLOCKS_DEVICE_ID"] = args.device_id

    custom_params = merge_custom_params(args.custom_param)
    result = run_workflow(
        args.workflow_path,
        custom_params=custom_params,
        skip_validation=args.skip_validation,
        write_report=not args.no_report,
    )

    print("=" * 60)
    print(f"工作流: {result['name']} ({result['workflow_id']})")
    print(f"结果: {'PASS' if result['status'] else 'FAIL'}")
    if result.get("data_rows") is not None:
        passed = sum(1 for item in result["data_rows"] if item["status"])
        print(f"数据行: {passed}/{len(result['data_rows'])} 通过，"
              f"总耗时: {result['duration_seconds']}s")
    else:
        print(f"耗时: {result['duration_seconds']}s，节点数: {len(result['node_order'])}")
    if result.get("report_dir"):
        print(f"报告目录: {result['report_dir']}")
    if args.verbose or not result["status"]:
        for node_id in result["node_order"]:
            node = result["node_results"][node_id]
            flag = "PASS" if node.get("status") else "FAIL"
            print(f"  [{flag}] {node_id}: {node.get('message', '')}")
    if not result["status"]:
        print(f"失败节点: {result.get('failed_node')}；{result.get('message')}")
    return 0 if result["status"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
