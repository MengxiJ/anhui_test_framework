# Copyright (C) 2026. All rights reserved.
"""项目路径常量（原子化项目自包含，不依赖任何旧框架目录）。"""
from __future__ import annotations

import os

# lib/core/paths.py -> lib/core -> lib -> 项目根
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# 原子化项目自带的数据目录（测试身份缓存等）
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CORE_DIR, "data")
