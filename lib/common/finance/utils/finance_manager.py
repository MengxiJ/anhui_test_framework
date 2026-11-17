# Copyright (C) 2026. All rights reserved.
"""资金域核心类（普通类，类内不做单例）。

处理充值 / 充值记录 / 交易明细业务，并复用 ``BrowserManager``
的通用读取能力（表格 / 文本 / alert / URL 稳定等待）；
本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from lib.common.browser.utils.browser_manager import BrowserManager
from lib.common.core.utils.text_number import parse_number_text
from lib.common.finance.utils.record_matcher import (
    AMOUNT_HEADERS,
    STATUS_HEADERS,
    TIME_HEADERS,
    TYPE_HEADERS,
    match_table_record,
)
from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

_MEMBER_CENTER_URL = BASE_URL + "/member/member/center"
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


class FinanceManager(BasePage):
    """前台资金业务（充值 / 记录核对 / 余额 / 资金管理巡检入口）。"""

    # ---- 充值页（原 RechargePage） ----
    _recharge_url = BASE_URL + "/finance/recharge/index"
    _recharge_money = (By.ID, "money")
    _recharge_valicode = (By.ID, "valicode")
    _recharge_submit_candidates = (
        (By.CSS_SELECTOR, 'form[name="reForm"] input[type=submit].recharge'),
        (By.CSS_SELECTOR, "input.recharge[type=submit]"),
        (By.CSS_SELECTOR, 'form[name="reForm"] input[type=submit]'),
        (By.CSS_SELECTOR, "button.btnbgorange"),
        (By.CSS_SELECTOR, "input.btnbgorange"),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
    )
    _recharge_message_candidates = (
        (By.CSS_SELECTOR, ".validation-invalid"),
        (By.CSS_SELECTOR, "[class*='error']"),
        (By.CSS_SELECTOR, "[class*='tip']"),
    )

    # ---- 充值记录页（原 RechargeLogPage） ----
    _recharge_log_url = BASE_URL + "/finance/recharge/log"

    # ---- 交易明细页（原 AccountLogPage） ----
    _account_log_url = BASE_URL + "/finance/accountlog/index"
    _account_log_start_time = (By.ID, "startTime")
    _account_log_end_time = (By.ID, "endTime")
    _account_log_type_select_candidates = (
        (By.CSS_SELECTOR, "select[name='type']"),
        (By.ID, "type"),
        (By.CSS_SELECTOR, "select.sm-select"),
        (By.CSS_SELECTOR, "select"),
    )
    _account_log_filter_btn_candidates = (
        (By.XPATH, '//button[contains(normalize-space(.), "筛选")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "筛选")]'),
        (By.XPATH, '//input[@value="筛选"]'),
        (By.XPATH, '//button[contains(normalize-space(.), "搜索")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "搜索")]'),
    )

    def __init__(self, driver) -> None:
        super().__init__(driver)
        self._browser: Optional[BrowserManager] = None

    @property
    def browser(self) -> BrowserManager:
        """通用浏览器读取能力（与当前 driver 同实例的轻量包装）。"""
        if self._browser is None:
            self._browser = BrowserManager(self.driver)
        return self._browser

    # ============ 充值页方法 ============
    def open_recharge_url(self):
        self.driver.get(self._recharge_url)

    def select_payment_type(self, payment_type="chinapnrTrust"):
        locator = (By.XPATH, f'//input[@name="paymentType" and @value="{payment_type}"]')
        self.base_click_special(locator)

    def input_money(self, amount):
        self.base_input(self._recharge_money, str(amount))

    def input_valicode(self, valicode):
        self.base_input(self._recharge_valicode, str(valicode))

    def click_submit(self):
        element = WebDriverWait(self.driver, self.default_timeout).until(
            lambda d: self._find_first_visible(self._recharge_submit_candidates)
        )
        element.click()

    def get_page_message(self):
        texts = []
        for by, value in self._recharge_message_candidates:
            try:
                for element in self.driver.find_elements(by, value):
                    text = (element.text or "").strip()
                    if text and text not in texts:
                        texts.append(text)
            except Exception:
                continue
        return " | ".join(texts)

    # ============ 充值记录页方法 ============
    def open_recharge_log_url(self):
        self.driver.get(self._recharge_log_url)

    # ============ 交易明细页方法 ============
    def open_account_log_url(self):
        self.driver.get(self._account_log_url)

    def select_log_type(self, text):
        element = self._find_first_visible(self._account_log_type_select_candidates)
        if element is None:
            raise ValueError("未找到交易分类下拉框")
        target = str(text)
        select = Select(element)
        try:
            select.select_by_visible_text(target)
            return
        except Exception:
            pass
        for option in select.options:
            option_text = (option.text or "").strip()
            if target and target in option_text:
                select.select_by_visible_text(option_text)
                return
        raise ValueError(f"交易分类下拉中无匹配选项: {target}")

    def input_date_range(self, start_date=None, end_date=None):
        if start_date:
            self.base_input(self._account_log_start_time, str(start_date))
        if end_date:
            self.base_input(self._account_log_end_time, str(end_date))

    def click_filter(self):
        element = self._find_first_visible(self._account_log_filter_btn_candidates)
        if element is None:
            raise ValueError("未找到筛选按钮")
        element.click()

    # ============ 通用工具 ============
    def _find_first_visible(self, candidates):
        for by, value in candidates:
            try:
                for element in self.driver.find_elements(by, value):
                    if element.is_displayed():
                        return element
            except Exception:
                continue
        return None

    # ============ 对外业务接口 ============
    def open_recharge_page(self) -> str:
        self.open_recharge_url()
        return str(self.driver.current_url)

    def recharge(
        self,
        amount: Any,
        valicode: str = "8888",
        payment_type: str = "chinapnrTrust",
    ) -> Dict[str, Any]:
        self.open_recharge_url()
        self.select_payment_type(payment_type)
        self.input_money(amount)
        self.input_valicode(valicode)
        handles_before = set(self.driver.window_handles)
        self.click_submit()

        result: Dict[str, Any] = {
            "amount": float(parse_number_text(amount)),
            "valicode": str(valicode),
            "payment_type": str(payment_type),
            "submitted": True,
        }
        new_handles = set(self.driver.window_handles) - handles_before
        if new_handles:
            self.driver.switch_to.window(sorted(new_handles)[-1])
        result["new_window"] = bool(new_handles)
        alert = self.browser.accept_alert(timeout=5)
        final_url = self._wait_url_settled()
        result.update(
            {
                "alert_present": alert["present"],
                "alert_text": alert["text"],
                "final_url": final_url,
                "page_message": self.get_page_message(),
            }
        )
        return result

    # ---- 余额 ----
    def get_balance(self) -> Dict[str, Any]:
        self.driver.get(_MEMBER_CENTER_URL)
        text = self._wait_balance_text(timeout=10.0)
        balance = parse_number_text(text)
        return {"balance": balance, "balance_text": text}

    def _wait_balance_text(self, timeout: float = 10.0) -> str:
        deadline = time.time() + timeout
        last_error: Optional[str] = None
        while time.time() < deadline:
            try:
                text = self.browser.execute_js(_BALANCE_TEXT_JS)
                if text and any(ch.isdigit() for ch in str(text)):
                    return str(text).strip()
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.5)
        raise TimeoutError(f"等待账户余额文本渲染超时（{timeout}s，最后错误: {last_error}）")

    # ---- 充值记录 ----
    def get_recharge_records(self) -> Dict[str, Any]:
        self.open_recharge_log_url()
        return self._read_records_table()

    def match_recharge_record(
        self,
        amount: Any,
        status_contains: str = "充值成功",
        time_window: float = 900.0,
    ) -> Dict[str, Any]:
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
        self.open_account_log_url()
        return self._read_records_table()

    def filter_account_logs(
        self,
        log_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.open_account_log_url()
        applied: Dict[str, Any] = {}
        if log_type:
            self.select_log_type(log_type)
            applied["log_type"] = str(log_type)
        if start_date or end_date:
            self.input_date_range(start_date, end_date)
            applied["start_date"] = str(start_date or "")
            applied["end_date"] = str(end_date or "")
        url_before = str(self.driver.current_url)
        self.click_filter()
        time.sleep(1.0)
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
        url = BASE_URL + "/finance/withdraw/index"
        final_url = self.browser.open_url_settled(url, settle_seconds=2.0, timeout=15.0)
        return {"requested_url": url, "url": final_url, "redirected": final_url != url}

    def open_trust_page(self) -> str:
        self.driver.get(BASE_URL + "/finance/trust/myTrust")
        return str(self.driver.current_url)

    def open_bounty_page(self) -> str:
        self.driver.get(BASE_URL + "/finance/newBounty/index")
        return str(self.driver.current_url)

    def get_current_page_text(self) -> str:
        return self.browser.get_text("tag_name", "body") or ""

    def get_current_records_table(self) -> Dict[str, Any]:
        return self._read_records_table()

    # ---- 内部工具 ----
    def _wait_url_settled(self, settle_seconds: float = 2.0, timeout: float = 15.0) -> str:
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
        deadline = time.time() + timeout
        last_error: Optional[Exception] = None
        while time.time() < deadline:
            try:
                return self._read_records_table_once(header_keywords)
            except Exception as exc:
                last_error = exc
                time.sleep(1.0)
        raise ValueError(f"当前页面记录表格无法读取（{timeout}s，最后错误: {last_error}）")

    def _read_records_table_once(self, header_keywords) -> Dict[str, Any]:
        table_count = self.browser.count_elements("tag_name", "table", timeout=5)
        if table_count == 0:
            raise ValueError("当前页面未找到记录表格 <table>")
        header_matched: Optional[Dict[str, Any]] = None
        fallback: Optional[Dict[str, Any]] = None
        for index in range(1, table_count + 1):
            try:
                table = self.browser.get_table_data("xpath", f"(//table)[{index}]", timeout=5)
            except Exception:
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
