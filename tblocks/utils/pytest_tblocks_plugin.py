# Copyright (C) 2026. All rights reserved.
"""pytest 集成插件：把 workflow JSON 收集为 pytest 用例。

默认不启用收集（不影响 scripts/ 下传统用例），通过参数开启：

    pytest --tblocks-workflows tblocks/workflows/demo

多个目录用逗号分隔；运行时台架参数用 ``--tblocks-custom-param key=value``。

插件在 configure 阶段导入 step_impl/check_impl，保证注册表就绪。
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


def pytest_addoption(parser) -> None:
    group = parser.getgroup("tblocks", "原子化 workflow")
    group.addoption(
        "--tblocks-workflows",
        action="store",
        default=None,
        help="逗号分隔的 workflow 目录（仅收集这些目录下的 .json）",
    )
    group.addoption(
        "--tblocks-custom-param",
        action="append",
        default=[],
        help="台架参数 key=value，可重复传入",
    )


# workflow 用例标记 = workflows/ 下一级业务目录名
_WORKFLOW_TAGS = (
    "smoke", "api", "portal", "functional", "member", "finance", "invest",
    "ui", "backend", "business", "demo", "performance", "load", "security",
)


def pytest_configure(config) -> None:
    # 保证从任意工作目录启动都能导入项目包（无条件置顶，避免同名包遮蔽）
    sys.path.insert(0, _project_root())
    for tag in _WORKFLOW_TAGS:
        config.addinivalue_line("markers", f"{tag}: tblocks workflow 业务域标记")
    try:
        import tblocks.check_impl  # noqa: F401
        import tblocks.step_impl  # noqa: F401
    except ImportError:
        pass


def pytest_load_initial_conftests(early_config, parser, args) -> None:
    """把 --tblocks-workflows 指定的目录追加为收集根。

    出现位置参数后 pytest 不再使用 ini 中的 testpaths，因此该模式下只收集
    workflow 用例，不会顺带执行 scripts/ 下的传统 UI/API 用例。
    """
    roots: List[str] = []
    explicit = False
    for index, item in enumerate(list(args)):
        if item == "--tblocks-workflows" and index + 1 < len(args):
            roots.append(args[index + 1])
            explicit = True
        elif item.startswith("--tblocks-workflows="):
            roots.append(item.split("=", 1)[1])
            explicit = True
    # 便捷入口：未显式指定收集根但用 -m 选择了 workflow 业务域标记时，
    # 自动收集 tblocks/workflows，例如 ``pytest -m smoke``。
    # 必须连同 --tblocks-workflows 选项一并注入，否则 pytest_collect_file
    # 因 option 为 None 不会收集 JSON。
    if not explicit and _marker_expr_targets_workflows(args):
        root = os.path.join(_project_root(), "tblocks", "workflows")
        args.extend(["--tblocks-workflows", root])
        roots.append(root)
    appended: List[str] = []
    for raw in roots:
        for root in raw.split(","):
            root = root.strip()
            # 只对自身追加的位置参数去重；不能用 `root in args` 判断，
            # 因为该字符串同时也是 --tblocks-workflows 的选项值。
            if root and root not in appended:
                appended.append(root)
                args.append(root)


def pytest_collect_file(file_path: Path, parent):
    option = parent.config.getoption("--tblocks-workflows")
    if not option or file_path.suffix != ".json":
        return None
    roots = [Path(item).resolve() for item in str(option).split(",") if item.strip()]
    resolved = file_path.resolve()
    if not any(_is_within(resolved, root) for root in roots):
        return None
    return WorkflowFile.from_parent(parent, path=file_path)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _project_root() -> str:
    # tblocks/utils/pytest_tblocks_plugin.py -> 上三级为项目根
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _marker_expr_targets_workflows(args: List[str]) -> bool:
    """判断 -m 表达式是否引用了 workflow 业务域标记。"""
    for index, item in enumerate(list(args)):
        if item == "-m" and index + 1 < len(args):
            expr = args[index + 1]
            return any(tag in expr for tag in _WORKFLOW_TAGS)
        if item.startswith("-m") and len(item) > 2:
            expr = item[2:]
            return any(tag in expr for tag in _WORKFLOW_TAGS)
    return False


def _workflow_tag(workflow_path: str) -> str:
    """workflows/<tag>/xxx.json -> tag。"""
    parts = Path(workflow_path).parts
    if "workflows" in parts:
        index = parts.index("workflows")
        if index + 1 < len(parts):
            return parts[index + 1]
    return "workflow"


class WorkflowFile(pytest.File):
    """workflow JSON 文件收集器。

    含顶层 ``data_rows`` 数组时按数据驱动展开：每行收集为一个独立 pytest
    项（``<文件名>[<row_id>]``），行间完全独立、各自建立会话与实例。
    """

    def collect(self):
        rows = None
        try:
            with open(self.path, encoding="utf-8") as handle:
                definition = json.load(handle)
            rows = definition.get("data_rows")
        except (OSError, json.JSONDecodeError):
            # 结构/JSON 错误交给执行期与静态校验器报出，收集阶段仍产出单项
            rows = None
        if rows:
            for index, row in enumerate(rows):
                row_id = str(row.get("row_id") or f"row{index}")
                yield WorkflowItem.from_parent(
                    self,
                    name=f"{self.path.stem}[{row_id}]",
                    workflow_path=str(self.path),
                    row_data=dict(row),
                )
        else:
            yield WorkflowItem.from_parent(
                self, name=self.path.stem, workflow_path=str(self.path), row_data=None
            )


class WorkflowItem(pytest.Item):
    """单个 workflow 执行项（数据驱动时绑定一行 data_rows）。"""

    def __init__(self, name, parent, workflow_path: str, row_data=None) -> None:
        super().__init__(name, parent)
        self.workflow_path = workflow_path
        self.row_data = row_data
        # 按 workflows/ 下一级目录自动打业务域标记，支持 -m smoke 等筛选
        self.add_marker(_workflow_tag(workflow_path))

    def runtest(self) -> None:
        from tblocks.utils.instance_manager import (
            initialize_instances,
            reset_instances,
        )
        from tblocks.utils.workflow_executor import WorkflowExecutor
        from tblocks.utils.workflow_models import Workflow

        with open(self.workflow_path, encoding="utf-8") as handle:
            workflow = Workflow.from_dict(json.load(handle))

        custom_params = _default_custom_params()
        custom_params.update(_parse_custom_params(self.config.getoption("--tblocks-custom-param")))
        initialize_instances()
        try:
            result = WorkflowExecutor().run(
                workflow, custom_params=custom_params, row_data=self.row_data
            )
        finally:
            reset_instances()
        if not result["status"]:
            failed_node = result.get("failed_node") or "未知节点"
            detail = result["node_results"].get(failed_node, {})
            row_prefix = f"[data_row={self.row_data.get('row_id')}] " if self.row_data else ""
            raise AssertionError(
                f"{row_prefix}workflow {workflow.id} 执行失败：节点 {failed_node} - "
                f"{detail.get('message', result.get('message'))}"
            )

    def reportinfo(self):
        return self.path, 0, f"workflow: {self.name}"


def _parse_custom_params(items: List[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    for raw in items:
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        try:
            params[key.strip()] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            params[key.strip()] = value
    return params


def _default_custom_params() -> Dict[str, Any]:
    """台架参数默认值（取自 project_config/.env，CLI --tblocks-custom-param 可覆盖）。"""
    from lib.core import project_config as cfg

    return {
        "admin_username": cfg.USERNAME,
        "admin_password": cfg.PASSWORD,
        "img_code": cfg.IMG_CODE,
        "user_phone": cfg.USER,
        "user_password": cfg.PWD,
    }
