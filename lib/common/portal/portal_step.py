# Copyright (C) 2026. All rights reserved.
"""portal 域 Lib 入口：门户公共只读接口步骤（无装饰器，纯实现）。

列表类步骤的 ``data`` 含 ``result``(=本页条数)、``items``、``total_items``、
``total_pages``、``page``；全部步骤都含 ``http_status``、``code``、``message``、
``body``，便于 check 节点以 ``${节点.data.xxx}`` 引用。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.framework.step_singletons import current_device_id
from lib.common.portal.utils.portal_manager import PortalManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "portal_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> PortalManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, PortalManager())
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 PortalManager（HTTP 会话随实例关闭）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


def _wrap(step: str, info: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(info)
    # 列表类接口 result = 本页条数；非列表接口 result = 业务码
    data["result"] = len(info["items"]) if isinstance(info.get("items"), list) else info.get("code")
    message = (
        f"门户接口 {step} 完成，HTTP: {info.get('http_status')}，"
        f"业务码: {info.get('code')}，本页条数: {data['result']}"
    )
    return step_result(step, True, message, data)


# ---- 投资标的 ----
def step_query_loan_list(page: int = 1, epage: int = 5, order: str = "",
                         borrow_type: str = "", account_status: str = "",
                         borrow_interestrate: str = "", spread_month: str = "") -> Dict[str, Any]:
    """查询投资标的分页列表。"""
    return _wrap(
        "step_query_loan_list",
        _get_core().query_loan_list(
            int(page), int(epage), order=order, borrow_type=borrow_type,
            account_status=account_status, borrow_interestrate=borrow_interestrate,
            spread_month=spread_month,
        ),
    )


def step_query_home_loan_list() -> Dict[str, Any]:
    """查询首页理财项目列表。"""
    return _wrap("step_query_home_loan_list", _get_core().query_home_loan_list())


def step_query_loan_total_stats() -> Dict[str, Any]:
    """查询平台数据统计（注册数/累计投资等）。"""
    return _wrap("step_query_loan_total_stats", _get_core().query_loan_total_stats())


def step_query_loan_plans() -> Dict[str, Any]:
    """查询首页理财计划（listOne）。"""
    return _wrap("step_query_loan_plans", _get_core().query_loan_plans())


def step_query_loan_search_filters() -> Dict[str, Any]:
    """查询投资列表筛选枚举（利率/期限/金额/类型）。"""
    return _wrap("step_query_loan_search_filters", _get_core().query_loan_search_filters())


def step_query_new_tender_preview() -> Dict[str, Any]:
    """查询新标预告。"""
    return _wrap("step_query_new_tender_preview", _get_core().query_new_tender_preview())


# ---- 内容 ----
def step_query_notice_list(page: int = 1) -> Dict[str, Any]:
    """查询网站公告列表。"""
    return _wrap("step_query_notice_list", _get_core().query_notice_list(int(page)))


def step_query_article_columns() -> Dict[str, Any]:
    """查询智客动态栏目文章（拍平 articleList）。"""
    return _wrap("step_query_article_columns", _get_core().query_article_columns())


def step_get_article_detail(article_id: int = 1) -> Dict[str, Any]:
    """获取文章详情页（HTML，回传标题与内容长度）。"""
    info = _get_core().get_article_detail(int(article_id))
    data = dict(info)
    data["result"] = info["content_length"]
    return step_result(
        "step_get_article_detail",
        True,
        f"文章 {article_id} 详情获取完成，HTTP: {info['http_status']}，长度: {info['content_length']}",
        data,
    )


# ---- 债权转让 / 体验标 ----
def step_query_transfer_list(page: int = 1) -> Dict[str, Any]:
    """查询债权转让可购买列表（可能为空）。"""
    return _wrap("step_query_transfer_list", _get_core().query_transfer_list(int(page)))

def step_query_transfer_types() -> Dict[str, Any]:
    """查询债权转让筛选枚举。"""
    return _wrap("step_query_transfer_types", _get_core().query_transfer_types())

def step_query_experience_loan_list(page: int = 1) -> Dict[str, Any]:
    """查询体验标列表（可能为空）。"""
    return _wrap("step_query_experience_loan_list", _get_core().query_experience_loan_list(int(page)))


# ---- 只读探针（负向 / 边界参数功能验证） ----
def step_probe_portal_endpoint(path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """对白名单只读接口发送任意表单参数并探测响应（不做 JSON 结构假设）。

    ``data`` 中的值不做类型转换，保持原样发送（如 ``{"page": "abc"}``），
    用于验证服务端对非法 / 边界参数的处理是否符合预期（优雅拒绝而非 5xx）。
    """
    info = _get_core().probe_readonly_endpoint(path, data)
    result = {
        "result": info.get("http_status"),
        **info,
    }
    return step_result(
        "step_probe_portal_endpoint",
        True,
        f"探针 {path} 完成，HTTP: {info['http_status']}，"
        f"JSON: {info['is_json']}，业务码: {info.get('code')}",
        result,
    )
