# Copyright (C) 2026. All rights reserved.
"""tblocks：原子化 Step-Check-Workflow 测试引擎。

三层单向调用链（对应实习公司框架规范）：

    Workflow(JSON 图)
        → TBlocks（tblocks/step_impl、tblocks/check_impl，薄封装）
            → Lib 入口（lib/common/<domain>/*_step.py、*_check.py）
                → Lib 核心（lib/common/<domain>/utils/*_manager.py）

核心组件：

- ``tblocks.utils.composer``：``@composer_step`` / ``@composer_check`` 装饰器与注册表；
- ``tblocks.utils.workflow_executor``：按 nodes/edges 执行 JSON 工作流；
- ``tblocks.workflow_runner``：工作流执行 CLI；
- ``tblocks.tblocks_debugger``：单节点 / 序列调试 CLI；
- ``tblocks.tools``：catalog 构建与 workflow 静态校验。

导入本包即会导入全部 step_impl / check_impl，触发装饰器注册。
"""
__version__ = "1.0.0"
