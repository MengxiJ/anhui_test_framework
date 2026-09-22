# Copyright (C) 2026. All rights reserved.
"""框架统一异常定义。

按框架规范，Lib 层逻辑失败优先抛出有信息量的异常，由 TBlocks 装饰器
统一转换为节点失败结果，不在业务代码里广泛吞异常。
"""
from __future__ import annotations


class TBlocksFrameworkError(Exception):
    """框架基类异常。"""


class InstanceNotFoundError(TBlocksFrameworkError):
    """实例管理器中找不到指定 key 的实例。"""


class StepExecutionError(TBlocksFrameworkError):
    """Step 执行失败。"""

    def __init__(self, step_name: str, reason: str) -> None:
        super().__init__(f"步骤 {step_name} 执行失败: {reason}")
        self.step_name = step_name
        self.reason = reason


class CheckExecutionError(TBlocksFrameworkError):
    """Check 执行异常（区别于检查不通过）。"""

    def __init__(self, check_name: str, reason: str) -> None:
        super().__init__(f"检查 {check_name} 执行异常: {reason}")
        self.check_name = check_name
        self.reason = reason


class WorkflowValidationError(TBlocksFrameworkError):
    """Workflow JSON 结构非法。"""


class NodeNotFoundError(WorkflowValidationError):
    """工作流引用了不存在的节点。"""


class RegistryNotFoundError(TBlocksFrameworkError):
    """step/check 未在注册表中注册。"""

    def __init__(self, node_type: str, node_id: str) -> None:
        super().__init__(f"{node_type} 节点未注册: {node_id}")
        self.node_type = node_type
        self.node_id = node_id


class BrowserUnavailableError(TBlocksFrameworkError):
    """浏览器驱动不可用（未安装 Chrome 或 ChromeDriver）。"""


class UnresolvedVariableError(WorkflowValidationError):
    """``${...}`` 变量引用无法解析。"""
