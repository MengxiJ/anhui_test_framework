# Copyright (C) 2026. All rights reserved.
"""门户公共接口核心类（普通类，类内不做单例）。

封装站点免登录、只读的公共接口（HTTP 通道，复用 ``BaseRequest``），
把 requests.Response 归一化为结构化字典：

    {
        "http_status": 200,
        "code": 200 / None,           # 门户接口业务字段名为 status
        "message": "OK" / None,       # 门户接口业务字段名为 description
        "items": [...],               # 列表类接口的记录（非列表接口为 None）
        "total_items": 496,           # 列表总条数（无则 None）
        "total_pages": 50,
        "page": 1,
        "body": {...} / str,          # 原始响应体
    }

所有方法均为只读查询，不产生任何业务数据变更。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from lib.core.base_request import BaseRequest

# 只读 POST 接口白名单：探针仅允许访问这些端点，从代码层面保证 portal 域零数据变更
_READONLY_POST_ENDPOINTS = frozenset({
    "/loan/loan/listtender",
    "/common/loan/listindex",
    "/common/loan/loantotal",
    "/common/loan/plans",
    "/loan/loan/loansearch",
    "/common/index/newTender",
    "/content/notice/noticelist",
    "/content/articles/mydtarticles",
    "/loan/transfer/buyTransferList",
    "/loan/transfer/transferTypes",
    "/loan/experience/tenderList",
})


class PortalManager:
    """门户公共数据查询。"""

    def __init__(self, api_client: Optional[BaseRequest] = None) -> None:
        self.api = api_client or BaseRequest()

    # ---- 归一化 ----
    @staticmethod
    def _normalize(response: Any, items: Any = None,
                   total_items: Any = None, total_pages: Any = None,
                   page: Any = None) -> Dict[str, Any]:
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - 非 JSON 响应退化为文本
            body = response.text
        code = body.get("status") if isinstance(body, dict) else None
        message = body.get("description") if isinstance(body, dict) else None
        return {
            "http_status": response.status_code,
            "code": code,
            "message": message,
            "items": items,
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "body": body,
        }

    def _page(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理 {page, epage, total_items, total_pages, items} 形态的分页接口。"""
        response = self.api.post(url, data=data or {})
        body = response.json()
        items = body.get("items") if isinstance(body, dict) else None
        return self._normalize(
            response,
            items=items,
            total_items=body.get("total_items") if isinstance(body, dict) else None,
            total_pages=body.get("total_pages") if isinstance(body, dict) else None,
            page=body.get("page") if isinstance(body, dict) else None,
        )

    # ---- 投资标的 ----
    def query_loan_list(self, page: int = 1, epage: int = 10,
                        order: str = "", borrow_type: str = "",
                        account_status: str = "", borrow_interestrate: str = "",
                        spread_month: str = "") -> Dict[str, Any]:
        """投资列表（智能投顾）POST /loan/loan/listtender。"""
        data = {
            "page": page,
            "epage": epage,
            "order": order,
            "borrow_type": borrow_type,
            "account_status": account_status,
            "borrow_interestrate": borrow_interestrate,
            "spread_month": spread_month,
        }
        return self._page("/loan/loan/listtender", data=data)

    def query_home_loan_list(self) -> Dict[str, Any]:
        """首页理财项目 POST /common/loan/listindex（分页数据包在 data 字段中）。"""
        response = self.api.post("/common/loan/listindex", data={})
        body = response.json()
        page_data = body.get("data") if isinstance(body, dict) else None
        items = None
        total_items = total_pages = page = None
        if isinstance(page_data, dict):
            items = page_data.get("items")
            total_items = page_data.get("total_items")
            total_pages = page_data.get("total_pages")
            page = page_data.get("page")
        return self._normalize(response, items=items, total_items=total_items,
                               total_pages=total_pages, page=page)

    def query_loan_total_stats(self) -> Dict[str, Any]:
        """平台数据统计 POST /common/loan/loantotal。"""
        return self._normalize(self.api.post("/common/loan/loantotal", data={}))

    def query_loan_plans(self) -> Dict[str, Any]:
        """首页理财计划 POST /common/loan/plans。"""
        response = self.api.post("/common/loan/plans", data={})
        body = response.json()
        items: Optional[List[Any]] = None
        data = body.get("data") if isinstance(body, dict) else None
        if isinstance(data, dict) and isinstance(data.get("listOne"), list):
            items = data["listOne"]
        return self._normalize(response, items=items, total_items=len(items) if items is not None else None)

    def query_loan_search_filters(self) -> Dict[str, Any]:
        """投资列表筛选项枚举 POST /loan/loan/loansearch。"""
        return self._normalize(self.api.post("/loan/loan/loansearch", data={}))

    def query_new_tender_preview(self) -> Dict[str, Any]:
        """新标预告 POST /common/index/newTender。"""
        return self._normalize(self.api.post("/common/index/newTender", data={}))

    # ---- 内容：公告 / 文章 ----
    def query_notice_list(self, page: int = 1) -> Dict[str, Any]:
        """网站公告列表 POST /content/notice/noticelist。"""
        return self._page("/content/notice/noticelist", data={"page": page})

    def query_article_columns(self) -> Dict[str, Any]:
        """智客动态栏目文章 POST /content/articles/mydtarticles。

        响应 data 为栏目数组，每栏目含 articleList；此处拍平为文章列表。
        """
        response = self.api.post("/content/articles/mydtarticles", data={})
        body = response.json()
        articles: List[Any] = []
        columns = body.get("data") if isinstance(body, dict) else None
        if isinstance(columns, list):
            for column in columns:
                if isinstance(column, dict) and isinstance(column.get("articleList"), list):
                    articles.extend(column["articleList"])
        return self._normalize(response, items=articles, total_items=len(articles))

    def get_article_detail(self, article_id: int) -> Dict[str, Any]:
        """文章详情页 GET /content/articles/getDetail?id=（HTML 页面，提取标题与长度）。"""
        response = self.api.get("/content/articles/getDetail", params={"id": article_id})
        html = response.text
        title = ""
        marker = "<title>"
        if marker in html and "</title>" in html:
            title = html.split(marker, 1)[1].split("</title>", 1)[0].strip()
        return {
            "http_status": response.status_code,
            "code": None,
            "message": None,
            "items": None,
            "total_items": None,
            "total_pages": None,
            "page": None,
            "body": html[:2000],
            "title": title,
            "content_length": len(html),
            "article_id": article_id,
        }

    # ---- 债权转让 / 体验标 ----
    def query_transfer_list(self, page: int = 1) -> Dict[str, Any]:
        """债权转让（可购买）列表 POST /loan/transfer/buyTransferList（允许为空列表）。"""
        return self._page("/loan/transfer/buyTransferList", data={"page": page})

    def query_transfer_types(self) -> Dict[str, Any]:
        """债权转让筛选枚举 POST /loan/transfer/transferTypes。"""
        return self._normalize(self.api.post("/loan/transfer/transferTypes", data={}))

    def query_experience_loan_list(self, page: int = 1) -> Dict[str, Any]:
        """体验标列表 POST /loan/experience/tenderList（允许为空列表）。"""
        return self._page("/loan/experience/tenderList", data={"page": page})

    # ---- 只读探针（负向 / 边界参数功能验证） ----
    def probe_readonly_endpoint(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """对白名单只读接口发送任意表单参数，探测服务端的参数校验行为。

        与 ``_page`` 的区别：不做 JSON 结构假设（非法参数可能返回 4xx/HTML），
        用于负向与边界值功能测试；path 必须在 ``_READONLY_POST_ENDPOINTS``
        白名单内，从代码层面保证 portal 域零数据变更。
        """
        if path not in _READONLY_POST_ENDPOINTS:
            raise ValueError(
                f"探针仅允许访问只读接口白名单，收到: {path!r}；"
                f"允许: {sorted(_READONLY_POST_ENDPOINTS)}"
            )
        response = self.api.post(path, data=data or {})
        try:
            body: Any = response.json()
            is_json = True
            code = body.get("status") if isinstance(body, dict) else None
            message = body.get("description") if isinstance(body, dict) else None
            items = body.get("items") if isinstance(body, dict) else None
            total_items = body.get("total_items") if isinstance(body, dict) else None
            preview = json.dumps(body, ensure_ascii=False)[:500]
        except Exception:  # noqa: BLE001 - 非 JSON 响应（如 4xx HTML 错误页）
            body = response.text
            is_json = False
            code = message = items = total_items = None
            preview = str(body)[:500]
        return {
            "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "is_json": is_json,
            "code": code,
            "message": message,
            "items": items,
            "total_items": total_items,
            "body_preview": preview,
            "path": path,
            "data": data or {},
        }
