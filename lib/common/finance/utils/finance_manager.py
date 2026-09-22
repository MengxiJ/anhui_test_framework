# Copyright (C) 2026. All rights reserved.
"""资金域核心类（普通类，类内不做单例）。

组合充值 / 充值记录 / 交易明细三个 PageObject，并复用 ``BrowserManager``
的通用读取能力（表格 / 文本 / alert / URL 稳定等待）；
本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from selenium.webdriver.common.by import By

from lib.common.browser.utils.browser_manager import BrowserManager
from lib.common.core.utils.text_number import parse_number_text
from lib.common.finance.pages import AccountLogPage, RechargeLogPage, RechargePage
from lib.common.finance.utils.record_matcher import (
    AMOUNT_HEADERS,
    STATUS_HEADERS,
    TIME_HEADERS,
    TYPE_HEADERS,
    match_table_record,
)
from lib.core.project_config import BASE_URL

_MEMBER_CENTER_URL = BASE_URL + "/member/member/center"
# 会员中心余额结构：<div class="raw1"><p><em ng-bind>78,000.00</em>元</p><p>账户余额</p></div>
# 余额数字由 AngularJS ng-bind 异步渲染，须轮询等待数字出现后解析
_BALANCE_TEXT_JS = (
    "var all = document.querySelectorAll('*');"
    "for (var i = 0; i < all.length; i++) {"
    "    var el = all[i];"
    "    var t = (el.textContent || '').trim();"
    "    if (t === '账户余额' && !el.children.length) {"
    "        var p = el.parentElement;"
    "        return p ? (p.textContent || '').trim() : t;"
    "    }"
    "}"
    "return null;"
)
_TABLE_HEADER_KEYWORDS = ("金额", "时间", "状态", "类型")


class FinanceManager:
    """前台资金业务（充值 / 记录核对 / 余额 / 资金管理巡检入口）。"""

    def __init__(self, driver) -> None:
        self.driver = driver
        self._recharge_page: Optional[RechargePage] = None
        self._recharge_log_page: Optional[RechargeLogPage] = None
        self._account_log_page: Optional[AccountLogPage] = None
        self._browser: Optional[BrowserManager] = None

    # ---- 页面对象 / 通用能力懒加载（与 driver 绑定，随实例复用） ----
    @property
    def recharge_page(self) -> RechargePage:
        if self._recharge_page is None:
            self._recharge_page = RechargePage(self.driver)
        return self._recharge_page

    @property
    def recharge_log_page(self) -> RechargeLogPage:
        if self._recharge_log_page is None:
            self._recharge_log_page = RechargeLogPage(self.driver)
        return self._recharge_log_page

    @property
    def account_log_page(self) -> AccountLogPage:
        if self._account_log_page is None:
            self._account_log_page = AccountLogPage(self.driver)
        return self._account_log_page

    @property
    def browser(self) -> BrowserManager:
        """通用浏览器读取能力（与当前 driver 同实例的轻量包装）。"""
        if self._browser is None:
            self._browser = BrowserManager(self.driver)
        return self._browser

    # ---- 充值 ----
    def open_recharge_page(self) -> str:
        """打开充值页，返回当前 URL。"""
        self.recharge_page.open_url()
        return str(self.driver.current_url)

    def recharge(
        self,
        amount: Any,
        valicode: str = "8888",
        payment_type: str = "chinapnrTrust",
    ) -> Dict[str, Any]:
        """提交一笔充值并捕获提交后交互（新窗口 / alert / 重定向 / 页面文案）。

        只负责「提交 + 证据捕获」，业务成败由后续充值记录/余额 check 判定。
        """
        page = self.recharge_page
        page.open_url()
        page.select_payment_type(payment_type)
        page.input_money(amount)
        page.input_valicode(valicode)
        handles_before = set(self.driver.window_handles)
        page.click_submit()

        result: Dict[str, Any] = {
            "amount": float(parse_number_text(amount)),
            "valicode": str(valicode),
            "payment_type": str(payment_type),
            "submitted": True,
        }
        # 托管网关可能打开新窗口：检测并切换到新窗口
        new_handles = set(self.driver.window_handles) - handles_before
        if new_handles:
            self.driver.switch_to.window(sorted(new_handles)[-1])
        result["new_window"] = bool(new_handles)
        # 提交后的原生 alert/confirm（存在则接受并记录文本）
        alert = self.browser.accept_alert(timeout=5)
        # 等待 URL 稳定（网关跳转/回跳后不再变化）
        final_url = self._wait_url_settled()
        result.update(
            {
                "alert_present": alert["present"],
                "alert_text": alert["text"],
                "final_url": final_url,
                "page_message": page.get_page_message(),
            }
        )
        return result

    # ---- 余额 ----
    def get_balance(self) -> Dict[str, Any]:
        """打开会员中心读取账户余额（``78,000.00元账户余额`` → 78000.0）。

        余额数字由 ng-bind 异步渲染，轮询等待容器文本中出现数字。
        """
        self.driver.get(_MEMBER_CENTER_URL)
        text = self._wait_balance_text(timeout=10.0)
        balance = parse_number_text(text)
        return {"balance": balance, "balance_text": text}

    def _wait_balance_text(self, timeout: float = 10.0) -> str:
        """轮询读取余额容器文本，直到其中出现数字（渲染完成）。"""
        deadline = time.time() + timeout
        last_error: Optional[str] = None
        while time.time() < deadline:
            try:
                text = self.browser.execute_js(_BALANCE_TEXT_JS)
                if text and any(ch.isdigit() for ch in str(text)):
                    return str(text).strip()
            except Exception as exc:  # noqa: BLE001 - 渲染中 JS 可能读不到，轮询重试
                last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.5)
        raise TimeoutError(f"等待账户余额文本渲染超时（{timeout}s，最后错误: {last_error}）")

    # ---- 充值记录 ----
    def get_recharge_records(self) -> Dict[str, Any]:
        """打开充值记录页并读取记录表格。"""
        self.recharge_log_page.open_url()
        return self._read_records_table()

    def match_recharge_record(
        self,
        amount: Any,
        status_contains: str = "充值成功",
        time_window: float = 900.0,
    ) -> Dict[str, Any]:
        """打开充值记录页，按金额+时间窗口（+状态关键字）匹配记录行。"""
        table = self.get_recharge_records()
        rules = []
        if status_contains:
            rules.append((STATUS_HEADERS, str(status_contains)))
        match = match_table_record(table, amount, time_window=time_window, keyword_rules=rules)
        match["table_headers"] = table.get("headers", [])
        match["row_count"] = table.get("row_count", 0)
        return match

    # ---- 交易明细 ----
    def get_account_logs(self) -> Dict[str, Any]:
        """打开交易明细页读取全部流水表格。"""
        self.account_log_page.open_url()
        return self._read_records_table()

    def filter_account_logs(
        self,
        log_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """交易明细按类型/日期区间筛选后读取表格。"""
        page = self.account_log_page
        page.open_url()
        applied: Dict[str, Any] = {}
        if log_type:
            page.select_log_type(log_type)
            applied["log_type"] = str(log_type)
        if start_date or end_date:
            page.input_date_range(start_date, end_date)
            applied["start_date"] = str(start_date or "")
            applied["end_date"] = str(end_date or "")
        url_before = str(self.driver.current_url)
        page.click_filter()
        time.sleep(1.0)  # 允许重载/重渲染启动（主同步手段是下方 URL 变化等待 + 表格读取重试）
        # 表单提交型筛选会整页重载（URL 追加查询参数）：等待 URL 变化后读取
        deadline = time.time() + 5.0
        while time.time() < deadline:
            if str(self.driver.current_url) != url_before:
                break
            time.sleep(0.3)
        table = self._read_records_table()
        table["applied_filter"] = applied
        return table

    def match_account_log(
        self,
        amount: Any,
        type_contains: Optional[str] = None,
        time_window: float = 900.0,
    ) -> Dict[str, Any]:
        """打开交易明细页，按金额+时间窗口（+类型关键字）匹配流水行。"""
        table = self.get_account_logs()
        rules = []
        if type_contains:
            rules.append((TYPE_HEADERS, str(type_contains)))
        match = match_table_record(table, amount, time_window=time_window, keyword_rules=rules)
        match["table_headers"] = table.get("headers", [])
        match["row_count"] = table.get("row_count", 0)
        return match

    # ---- 资金管理巡检入口 ----
    def open_withdraw_entry(self) -> Dict[str, Any]:
        """打开提现入口并等待重定向稳定（未绑卡时强制跳银行卡页）。"""
        url = BASE_URL + "/finance/withdraw/index"
        final_url = self.browser.open_url_settled(url, settle_seconds=2.0, timeout=15.0)
        return {"requested_url": url, "url": final_url, "redirected": final_url != url}

    def open_trust_page(self) -> str:
        """打开我的支付账户页（托管状态页），返回当前 URL。"""
        self.driver.get(BASE_URL + "/finance/trust/myTrust")
        return str(self.driver.current_url)

    def open_bounty_page(self) -> str:
        """打开我的红包页，返回当前 URL。"""
        self.driver.get(BASE_URL + "/finance/newBounty/index")
        return str(self.driver.current_url)

    def get_current_page_text(self) -> str:
        """读取当前页面可见文本（body）。"""
        return self.browser.get_text("tag_name", "body") or ""

    def get_current_records_table(self) -> Dict[str, Any]:
        """读取当前页面记录表格（供筛选后的一致性 check 使用）。"""
        return self._read_records_table()

    # ---- 内部工具 ----
    def _wait_url_settled(self, settle_seconds: float = 2.0, timeout: float = 15.0) -> str:
        """等待当前 URL 稳定（连续 settle_seconds 秒不变），返回最终 URL。"""
        last_url = self.driver.current_url
        stable_since = time.time()
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.3)
            current = self.driver.current_url
            if current == last_url:
                if time.time() - stable_since >= settle_seconds:
                    return current
            else:
                last_url = current
                stable_since = time.time()
        return last_url

    def _read_records_table(
        self, header_keywords=_TABLE_HEADER_KEYWORDS, timeout: float = 15.0
    ) -> Dict[str, Any]:
        """读取当前页面的记录表格（带重试，兼容筛选触发表单提交后的页面重载）。"""
        deadline = time.time() + timeout
        last_error: Optional[Exception] = None
        while time.time() < deadline:
            try:
                return self._read_records_table_once(header_keywords)
            except Exception as exc:  # noqa: BLE001 - 重载/重渲染竞态，轮询重试
                last_error = exc
                time.sleep(1.0)
        raise ValueError(f"当前页面记录表格无法读取（{timeout}s，最后错误: {last_error}）")

    def _read_records_table_once(self, header_keywords) -> Dict[str, Any]:
        """读取当前页面记录表格；多张表时优先选表头含关键字的表，否则选行数最多的表。"""
        table_count = self.browser.count_elements("tag_name", "table", timeout=5)
        if table_count == 0:
            raise ValueError("当前页面未找到记录表格 <table>")
        header_matched: Optional[Dict[str, Any]] = None
        fallback: Optional[Dict[str, Any]] = None
        for index in range(1, table_count + 1):
            try:
                table = self.browser.get_table_data("xpath", f"(//table)[{index}]", timeout=5)
            except Exception:  # noqa: BLE001 - 布局表格可能不可读，逐张尝试
                continue
            if fallback is None or table.get("row_count", 0) > fallback.get("row_count", 0):
                fallback = table
            headers_text = "".join(str(h) for h in table.get("headers", []))
            if header_matched is None and any(k in headers_text for k in header_keywords):
                header_matched = table
        chosen = header_matched or fallback
        if chosen is None:
            raise ValueError("当前页面记录表格无法读取")
        return chosen
