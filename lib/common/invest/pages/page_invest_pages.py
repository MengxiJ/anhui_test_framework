# Copyright (C) 2026. All rights reserved.
"""理财巡检页集合：我的收款计划 / 债权转让 / 自动投标入口。

实测结构（菜单真实链接）：

- 我的收款计划 ``/loan/recover/index``：筛选日期 ``#start`` / ``#end`` +
  ``INPUT.btn-search[value=筛选]``，表头 [标题, 应收日期，借款者，第几期/总期数，
  应收总额，应收本金，应收利息, 逾期天数, 状态]；
- 债权转让 ``/loan/transfer/mytransfer``：状态下拉 ``select#change_nid``
  （全部/可以转让 can/转让中 now/转让成功 yes/已撤销 cancel），页面含多张表格；
- 自动投标 ``/loan/loan/auto``：实测重定向到 ``/finance/trust/myTrust``（拦截确认）。
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# 收款计划数据表表头关键字（用于多表中识别数据表）
_RECEIVE_PLAN_KEYWORDS = ("应收", "标题")
# 债权转让状态下拉选项
_DEBT_FILTER_OPTIONS = ("全部", "可以转让", "转让中", "转让成功", "已撤销")


class InvestPages(BasePage):
    """理财管理巡检页面对象（我的收款计划 / 债权转让 / 自动投标入口）。"""

    # 菜单真实链接（实测）：
    # 我的收款计划 → /loan/recover/index；债权转让 → /loan/transfer/mytransfer；
    # 自动投标 → /loan/loan/auto（未开通托管时重定向 /finance/trust/myTrust）
    __receive_plan_url = BASE_URL + "/loan/recover/index"
    __debt_url = BASE_URL + "/loan/transfer/mytransfer"
    __auto_tender_url = BASE_URL + "/loan/loan/auto"

    __start_date = (By.ID, "start")
    __end_date = (By.ID, "end")
    __receive_filter = (By.CSS_SELECTOR, 'input.btn-search[value="筛选"], input[value="筛选"]')
    __debt_select = (By.ID, "change_nid")
    __tables = (By.TAG_NAME, "table")

    # ---- 收款计划 ----
    def open_receive_plan(self) -> str:
        """打开收款计划页，返回当前 URL。"""
        self.driver.get(self.__receive_plan_url)
        return str(self.driver.current_url)

    def read_receive_plan_table(self, timeout: float = 10.0) -> Dict[str, Any]:
        """读取收款计划数据表（轮询等待 AngularJS 渲染）。"""
        deadline = time.time() + timeout
        last: Dict[str, Any] = {"headers": [], "rows": [], "row_count": 0, "empty_state": True}
        while time.time() < deadline:
            last = self._read_best_table(_RECEIVE_PLAN_KEYWORDS)
            if last["headers"]:
                break
            time.sleep(0.8)
        joined = " ".join(" ".join(r) for r in last["rows"])
        last["empty_state"] = ("暂无" in joined) or ("没有" in joined) or last["row_count"] == 0
        return last

    def filter_receive_plan(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """按日期区间筛选收款计划后读取表格。"""
        if start_date:
            self._input_clear(self.__start_date, start_date)
        if end_date:
            self._input_clear(self.__end_date, end_date)
        try:
            buttons = self.driver.find_elements(*self.__receive_filter)
            if buttons:
                buttons[0].click()
        except Exception:  # noqa: BLE001 - 筛选按钮渲染竞态
            pass
        time.sleep(1.5)
        return self.read_receive_plan_table()

    # ---- 债权转让 ----
    def open_debt_page(self) -> str:
        """打开债权转让页，返回当前 URL。"""
        self.driver.get(self.__debt_url)
        return str(self.driver.current_url)

    def read_debt_filter_options(self) -> List[str]:
        """读取债权转让状态下拉选项文本。"""
        try:
            selects = self.driver.find_elements(*self.__debt_select)
            if not selects:
                return []
            return [o.text.strip() for o in Select(selects[0]).options if o.text.strip()]
        except Exception:  # noqa: BLE001
            return []

    def filter_debt_by_status(self, option_text: str) -> bool:
        """按状态筛选债权转让（匹配选项则 True）。"""
        try:
            selects = self.driver.find_elements(*self.__debt_select)
            if not selects:
                return False
            select = Select(selects[0])
            for option in select.options:
                if option_text and option_text in (option.text.strip() or ""):
                    select.select_by_visible_text(option.text)
                    time.sleep(1.5)
                    return True
            return False
        except Exception:  # noqa: BLE001
            return False

    def read_debt_tables(self) -> List[Dict[str, Any]]:
        """读取债权转让页全部表格。"""
        return self._read_all_tables()

    # ---- 自动投标 ----
    def open_auto_tender_entry(self) -> Dict[str, Any]:
        """打开自动投标入口并等待重定向稳定（未开通托管时跳托管页）。"""
        requested = self.__auto_tender_url
        try:
            self.driver.get(requested)
        except Exception:  # noqa: BLE001 - 跳转中的导航超时
            pass
        time.sleep(2.0)
        final_url = str(self.driver.current_url)
        # 重定向后等待稳定
        stable_since = time.time()
        last_url = final_url
        deadline = time.time() + 8.0
        while time.time() < deadline:
            time.sleep(0.5)
            current = str(self.driver.current_url)
            if current == last_url:
                if time.time() - stable_since >= 1.5:
                    final_url = current
                    break
            else:
                last_url = current
                stable_since = time.time()
        return {"requested_url": requested, "url": final_url, "redirected": final_url != requested}

    # ---- 内部工具 ----
    def _input_clear(self, locator, value: str) -> None:
        inputs = self.driver.find_elements(*locator)
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys(value)

    def _read_all_tables(self) -> List[Dict[str, Any]]:
        tables = self.driver.find_elements(*self.__tables)
        result: List[Dict[str, Any]] = []
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
                if header_cells or rows:
                    result.append(
                        {"headers": header_cells, "rows": rows, "row_count": len(rows)}
                    )
            except Exception:  # noqa: BLE001 - 渲染竞态跳过
                continue
        return result

    def _read_best_table(self, header_keywords) -> Dict[str, Any]:
        """多表中优先返回表头含关键字的表，否则行数最多的表。"""
        tables = self._read_all_tables()
        chosen: Optional[Dict[str, Any]] = None
        fallback: Optional[Dict[str, Any]] = None
        for info in tables:
            text = "".join(info["headers"])
            if any(k in text for k in header_keywords):
                chosen = info
                break
            if fallback is None or info["row_count"] > fallback["row_count"]:
                fallback = info
        return chosen or fallback or {"headers": [], "rows": [], "row_count": 0}
