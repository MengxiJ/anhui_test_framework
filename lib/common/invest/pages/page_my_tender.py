# Copyright (C) 2026. All rights reserved.
"""我的投资页（理财管理 → 我的投资）。

实测结构：

- 状态 tab：``li``（回款中默认 ``.on`` / 投标中 / 已结清 / 已流标）；
- 记录表头：[起息日-到期日, 项目名称, 投资金额, 总收益, 已收利息, 待收本息, 状态, 操作]；
- 空态行文本 ``-- 暂无记录 --``。
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# tab 名称 → 默认落点（运行时以实际渲染为准）
DEFAULT_TABS = ("回款中", "投标中", "已结清", "已流标")


class MyTenderPage(BasePage):
    """我的投资页面对象。"""

    # 菜单真实链接为小写 mytender（Tomcat 大小写敏感，myTender 会 404/空页）
    __my_tender_url = BASE_URL + "/loan/tender/mytender"
    __tab_items = (By.CSS_SELECTOR, "li")
    __tables = (By.TAG_NAME, "table")

    def open_url(self) -> None:
        """打开我的投资页。"""
        self.driver.get(self.__my_tender_url)

    def read_tabs(self) -> List[str]:
        """读取状态 tab 文本列表。"""
        items = self.driver.find_elements(*self.__tab_items)
        tabs = []
        for item in items:
            text = item.text.strip()
            if text in DEFAULT_TABS:
                tabs.append(text)
        return tabs

    def switch_tab(self, tab_name: str) -> bool:
        """切换到指定状态 tab（点击后等待表格重渲染）。"""
        items = self.driver.find_elements(*self.__tab_items)
        for item in items:
            if item.text.strip() == tab_name:
                try:
                    item.click()
                except Exception:  # noqa: BLE001 - 点击竞态重试一次
                    time.sleep(0.5)
                    item.click()
                time.sleep(1.5)  # AngularJS 重渲染
                return True
        return False

    def read_current_table(self) -> Dict[str, Any]:
        """读取当前 tab 的记录表格（多表时取含「项目名称/投资金额」表头的数据表）。"""
        tables = self.driver.find_elements(*self.__tables)
        if not tables:
            return {"headers": [], "rows": [], "row_count": 0, "empty_state": True}
        chosen: Optional[Dict[str, Any]] = None
        fallback: Optional[Dict[str, Any]] = None
        for table in tables:
            try:
                headers = table.find_elements(
                    By.CSS_SELECTOR,
                    "thead tr:nth-child(1) th, thead tr:nth-child(1) td, tr:nth-child(1) th",
                )
                header_cells = [h.text.strip() for h in headers if h.text.strip()]
                rows: List[List[str]] = []
                for tr in table.find_elements(By.TAG_NAME, "tr"):
                    cells = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                    if cells and any(cells):
                        rows.append(cells)
                info = {"headers": header_cells, "rows": rows, "row_count": len(rows)}
            except Exception:  # noqa: BLE001 - 渲染竞态跳过该表
                continue
            if any(k in "".join(header_cells) for k in ("项目名称", "投资金额")):
                chosen = info
                break
            if fallback is None or info["row_count"] > fallback["row_count"]:
                fallback = info
        result = chosen or fallback or {"headers": [], "rows": [], "row_count": 0}
        joined = " ".join(" ".join(r) for r in result["rows"])
        result["empty_state"] = ("暂无" in joined) or result["row_count"] == 0
        return result

    def read_all_tabs(self) -> Dict[str, Dict[str, Any]]:
        """逐一切换全部 tab 并读取各自表格，返回 {tab: 表格信息}。"""
        result: Dict[str, Dict[str, Any]] = {}
        for tab in self.read_tabs():
            if self.switch_tab(tab):
                result[tab] = self.read_current_table()
        return result
