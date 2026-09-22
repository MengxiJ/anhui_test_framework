# Copyright (C) 2026. All rights reserved.
"""portal 域 step 原子节点（薄封装，仅调用 lib 入口）。

全部为站点免登录只读接口，data 中含 http_status/code/message/items/
total_items/total_pages/page/body/result，可用 ``${节点.data.xxx}`` 引用。
"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.portal import portal_step as lib


@composer_step(
    name="step_query_loan_list",
    description="查询投资标的分页列表 POST /loan/loan/listtender",
    category="portal",
    params={
        "page": {"name": "页码", "type": "int", "required": False,
                 "default": 1, "min": 1, "description": "页码，从 1 开始"},
        "epage": {"name": "每页条数", "type": "int", "required": False,
                  "default": 5, "min": 1, "max": 50, "description": "每页条数"},
        "order": {"name": "排序", "type": "str", "required": False,
                  "default": "", "description": "排序方式，可空"},
        "borrow_type": {"name": "标的类型", "type": "str", "required": False,
                        "default": "", "description": "标的类型筛选，可空"},
        "account_status": {"name": "状态", "type": "str", "required": False,
                           "default": "", "description": "账户状态筛选，可空"},
        "borrow_interestrate": {"name": "利率区间", "type": "str", "required": False,
                                "default": "", "description": "利率筛选，可空"},
        "spread_month": {"name": "期限", "type": "str", "required": False,
                         "default": "", "description": "期限筛选，可空"},
    },
)
def step_query_loan_list(page=1, epage=5, order="", borrow_type="",
                         account_status="", borrow_interestrate="", spread_month=""):
    """投资标的分页列表。"""
    return lib.step_query_loan_list(
        page, epage, order=order, borrow_type=borrow_type,
        account_status=account_status, borrow_interestrate=borrow_interestrate,
        spread_month=spread_month,
    )


@composer_step(
    name="step_query_home_loan_list",
    description="查询首页理财项目列表 POST /common/loan/listindex",
    category="portal",
)
def step_query_home_loan_list():
    """首页理财项目列表。"""
    return lib.step_query_home_loan_list()


@composer_step(
    name="step_query_loan_total_stats",
    description="查询平台数据统计 POST /common/loan/loantotal",
    category="portal",
)
def step_query_loan_total_stats():
    """平台数据统计。"""
    return lib.step_query_loan_total_stats()


@composer_step(
    name="step_query_loan_plans",
    description="查询首页理财计划 listOne POST /common/loan/plans",
    category="portal",
)
def step_query_loan_plans():
    """首页理财计划。"""
    return lib.step_query_loan_plans()


@composer_step(
    name="step_query_loan_search_filters",
    description="查询投资列表筛选枚举 POST /loan/loan/loansearch",
    category="portal",
)
def step_query_loan_search_filters():
    """投资列表筛选枚举。"""
    return lib.step_query_loan_search_filters()


@composer_step(
    name="step_query_new_tender_preview",
    description="查询新标预告 POST /common/index/newTender",
    category="portal",
)
def step_query_new_tender_preview():
    """新标预告。"""
    return lib.step_query_new_tender_preview()


@composer_step(
    name="step_query_notice_list",
    description="查询网站公告列表 POST /content/notice/noticelist",
    category="portal",
    params={
        "page": {"name": "页码", "type": "int", "required": False,
                 "default": 1, "min": 1, "description": "页码"},
    },
)
def step_query_notice_list(page=1):
    """网站公告列表。"""
    return lib.step_query_notice_list(page)


@composer_step(
    name="step_query_article_columns",
    description="查询智客动态栏目文章 POST /content/articles/mydtarticles",
    category="portal",
)
def step_query_article_columns():
    """智客动态栏目文章。"""
    return lib.step_query_article_columns()


@composer_step(
    name="step_get_article_detail",
    description="获取文章详情页 GET /content/articles/getDetail?id=",
    category="portal",
    params={
        "article_id": {"name": "文章ID", "type": "int", "required": False,
                       "default": 1, "min": 1, "description": "文章 ID"},
    },
)
def step_get_article_detail(article_id=1):
    """文章详情页。"""
    return lib.step_get_article_detail(article_id)


@composer_step(
    name="step_query_transfer_list",
    description="查询债权转让可购买列表 POST /loan/transfer/buyTransferList（可能为空）",
    category="portal",
    params={
        "page": {"name": "页码", "type": "int", "required": False,
                 "default": 1, "min": 1, "description": "页码"},
    },
)
def step_query_transfer_list(page=1):
    """债权转让列表。"""
    return lib.step_query_transfer_list(page)


@composer_step(
    name="step_query_transfer_types",
    description="查询债权转让筛选枚举 POST /loan/transfer/transferTypes",
    category="portal",
)
def step_query_transfer_types():
    """债权转让筛选枚举。"""
    return lib.step_query_transfer_types()


@composer_step(
    name="step_query_experience_loan_list",
    description="查询体验标列表 POST /loan/experience/tenderList（可能为空）",
    category="portal",
    params={
        "page": {"name": "页码", "type": "int", "required": False,
                 "default": 1, "min": 1, "description": "页码"},
    },
)
def step_query_experience_loan_list(page=1):
    """体验标列表。"""
    return lib.step_query_experience_loan_list(page)


@composer_step(
    name="step_probe_portal_endpoint",
    description="只读接口探针：向白名单接口发送任意表单参数并探测响应（负向/边界功能验证）",
    category="portal",
    params={
        "path": {"name": "接口路径", "type": "str", "required": True,
                 "description": "白名单只读 POST 接口路径，如 /loan/loan/listtender"},
        "data": {"name": "表单参数", "type": "dict", "required": False,
                 "default": {}, "description": "任意表单参数（值保持原样发送，如 page=abc）"},
    },
)
def step_probe_portal_endpoint(path, data=None):
    """只读接口探针。"""
    return lib.step_probe_portal_endpoint(path, data)
