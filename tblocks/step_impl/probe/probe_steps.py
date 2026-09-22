# Copyright (C) 2026. All rights reserved.
"""probe 域 step 原子节点（薄封装，仅调用 lib 入口）。

返回 data 字段：http_status / code / message / content_type / body_length /
body_text / elapsed_ms / final_url / body。
"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.probe import probe_step as lib


@composer_step(
    name="step_probe_http_get",
    description="GET 连通性探针：访问前/后台任意路径，回传状态码、Content-Type、响应体特征",
    category="probe",
    params={
        "path": {"name": "请求路径", "type": "str", "required": True,
                 "description": "以 / 开头，如 / 或 /common/public/verifycode1/0.1"},
        "site": {"name": "目标站点", "type": "str", "required": False,
                 "default": "front", "enum": ["front", "back"],
                 "description": "front=前台8081，back=后台8082"},
        "allow_redirects": {"name": "跟随重定向", "type": "bool", "required": False,
                            "default": True, "description": "是否跟随 302"},
    },
)
def step_probe_http_get(path, site="front", allow_redirects=True):
    """GET 探针。"""
    return lib.step_probe_http_get(path, site=site, allow_redirects=allow_redirects)


@composer_step(
    name="step_probe_http_post",
    description="POST 表单探针：向前/后台任意路径提交表单，回传状态码与响应体特征",
    category="probe",
    params={
        "path": {"name": "请求路径", "type": "str", "required": True,
                 "description": "以 / 开头，如 /loan/loan/listtender"},
        "data": {"name": "表单参数", "type": "dict", "required": False,
                 "default": {}, "description": "application/x-www-form-urlencoded 表单键值"},
        "site": {"name": "目标站点", "type": "str", "required": False,
                 "default": "front", "enum": ["front", "back"],
                 "description": "front=前台8081，back=后台8082"},
        "allow_redirects": {"name": "跟随重定向", "type": "bool", "required": False,
                            "default": True, "description": "是否跟随 302"},
    },
)
def step_probe_http_post(path, data=None, site="front", allow_redirects=True):
    """POST 探针。"""
    return lib.step_probe_http_post(path, data=data, site=site,
                                    allow_redirects=allow_redirects)
