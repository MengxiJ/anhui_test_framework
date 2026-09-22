# Copyright (C) 2026. All rights reserved.
"""catalog 与 workflow 目录路径统一定义。"""
from __future__ import annotations

import os

# tblocks/tools/ -> tblocks/ -> 项目根
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
TBLOCKS_DIR = os.path.dirname(TOOLS_DIR)
PROJECT_ROOT = os.path.dirname(TBLOCKS_DIR)

STEPS_CATALOG_PATH = os.path.join(TOOLS_DIR, "steps_catalog.json")
CHECKS_CATALOG_PATH = os.path.join(TOOLS_DIR, "checks_catalog.json")
UNIQUE_APIS_PATH = os.path.join(TOOLS_DIR, "unique_apis.json")

WORKFLOWS_DIR = os.path.join(TBLOCKS_DIR, "workflows")
STEP_IMPL_DIR = os.path.join(TBLOCKS_DIR, "step_impl")
CHECK_IMPL_DIR = os.path.join(TBLOCKS_DIR, "check_impl")
TBLOCKS_REPORT_DIR = os.path.join(PROJECT_ROOT, "output", "tblocks")
