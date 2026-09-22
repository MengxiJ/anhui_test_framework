# Copyright (C) 2026. All rights reserved.
"""check_impl：Check 原子节点（@composer_check 薄封装层）。

导入本包即导入全部业务域子模块，触发装饰器注册到 CHECK_REGISTRY。
"""
from . import account as account  # noqa: F401
from . import backend as backend  # noqa: F401
from . import browser as browser  # noqa: F401
from . import core as core  # noqa: F401
from . import finance as finance  # noqa: F401
from . import invest as invest  # noqa: F401
from . import load as load  # noqa: F401
from . import member as member  # noqa: F401
from . import portal as portal  # noqa: F401
from . import probe as probe  # noqa: F401
