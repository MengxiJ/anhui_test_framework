# Copyright (C) 2026. All rights reserved.
"""step_impl：Step 原子节点（@composer_step 薄封装层）。

导入本包即导入全部业务域子模块，触发装饰器注册到 STEP_REGISTRY。
本层函数只允许 import 并调用 ``lib/common/<domain>/*_step.py``，
不写业务逻辑、不做实例 register/get。
"""
from . import account as account  # noqa: F401
from . import backend as backend  # noqa: F401
from . import borrow as borrow  # noqa: F401
from . import browser as browser  # noqa: F401
from . import core as core  # noqa: F401
from . import finance as finance  # noqa: F401
from . import invest as invest  # noqa: F401
from . import load as load  # noqa: F401
from . import member as member  # noqa: F401
from . import portal as portal  # noqa: F401
from . import probe as probe  # noqa: F401
