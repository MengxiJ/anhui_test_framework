# Copyright (C) 2026. All rights reserved.
"""前台会员业务核心类（普通类，类内不做单例）。

处理登录 / 注册 / 开户 / 额度申请 / 中心总览 / 资料 / 提醒 / 杂项页 / 站内消息业务。
本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL, CARD, NAME

# ---- 会员中心余额 ----
_MEMBER_CENTER_BALANCE_RE = re.compile(r"([\d,\.]+)\s*元")
_MEMBER_CENTER_BALANCE_TEXT_JS = (
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
_MEMBER_CENTER_BALANCE_CONTAINS_JS = (
    "var els = document.querySelectorAll('*');"
    "for (var i = 0; i < els.length; i++) {"
    "    var t = (els[i].textContent || '').trim();"
    "    if ((t.indexOf('账户余额') >= 0 || t.indexOf('可用余额') >= 0)"
    "        && t.length <= 60) { return t; }"
    "}"
    "return '';"
)
_READ_RECENT_TX_JS = (
    "function readTable(tbl) {"
    "    var headers = [];"
    "    var headRow = tbl.querySelector('thead tr') || tbl.querySelector('tr');"
    "    if (headRow) {"
    "        var cells = headRow.querySelectorAll('th,td');"
    "        for (var j = 0; j < cells.length; j++) {"
    "            var t = (cells[j].textContent || '').trim();"
    "            if (t) { headers.push(t); }"
    "        }"
    "    }"
    "    var rows = [];"
    "    var trs = tbl.querySelectorAll('tr');"
    "    for (var i = 0; i < trs.length; i++) {"
    "        var tds = trs[i].querySelectorAll('td');"
    "        if (!tds.length) { continue; }"
    "        var row = [];"
    "        var has = false;"
    "        for (var j = 0; j < tds.length; j++) {"
    "            var t = (tds[j].textContent || '').trim();"
    "            row.push(t);"
    "            if (t) { has = true; }"
    "        }"
    "        if (has) { rows.push(row); }"
    "    }"
    "    return {headers: headers, rows: rows};"
    "}"
    "function headerTextOf(tbl) {"
    "    var headRow = tbl.querySelector('thead tr') || tbl.querySelector('tr');"
    "    if (!headRow) { return ''; }"
    "    var cells = headRow.querySelectorAll('th,td');"
    "    var parts = [];"
    "    for (var j = 0; j < cells.length; j++) {"
    "        var tt = (cells[j].textContent || '').trim();"
    "        if (tt) { parts.push(tt); }"
    "    }"
    "    return parts.join('|');"
    "}"
    "var tables = document.querySelectorAll('table');"
    "var tbl = null;"
    "for (var i = 0; i < tables.length; i++) {"
    "    var ht = headerTextOf(tables[i]);"
    "    if (ht.indexOf('时间') >= 0 && ht.indexOf('类型') >= 0"
    "        && (ht.indexOf('存入') >= 0 || ht.indexOf('支出') >= 0 || ht.indexOf('余额') >= 0)"
    "        && !(ht.indexOf('资产') >= 0 && ht.indexOf('占比') >= 0)) {"
    "        tbl = tables[i]; break;"
    "    }"
    "}"
    "if (!tbl) {"
    "    var keywords = ['最近交易', '最新交易', '交易记录'];"
    "    var heading = null;"
    "    var cand = document.querySelectorAll('h1,h2,h3,h4,h5,span,b,strong,td,th,dt,em,p,label,a,div');"
    "    for (var i = 0; i < cand.length && !heading; i++) {"
    "        var t = (cand[i].textContent || '').trim();"
    "        if (t && t.length <= 20) {"
    "            for (var k = 0; k < keywords.length; k++) {"
    "                if (t.indexOf(keywords[k]) >= 0) { heading = cand[i]; break; }"
    "            }"
    "        }"
    "    }"
    "    if (heading) {"
    "        var node = heading;"
    "        for (var d = 0; d < 8 && node; d++) {"
    "            node = node.parentElement;"
    "            if (!node || !node.querySelector) { break; }"
    "            if (node.querySelector('table')) { tbl = node.querySelector('table'); break; }"
    "        }"
    "    }"
    "}"
    "if (!tbl) { return {headers: [], rows: [], found: false}; }"
    "var data = readTable(tbl);"
    "data.found = true;"
    "return data;"
)

# ---- 基础资料 ----
_PROFILE_SELECT_FIELDS = (
    "educationalBackground", "marryStatus", "companyIndustry",
    "companyScale", "companyOffice", "monthlyIncome",
    "hometownProvince", "hometownCity", "hometownArea",
)
_PROFILE_INPUT_FIELDS = ("graduated", "address")
_EDIT_BUTTON_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "编")]'),
    (By.XPATH, '//button[contains(text(), "编")]'),
)
_SAVE_BUTTON_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "保存")]'),
    (By.XPATH, '//input[contains(@value, "确认")]'),
    (By.XPATH, '//input[contains(@value, "提交")]'),
    (By.XPATH, '//button[contains(text(), "保存")]'),
    (By.XPATH, '//button[contains(text(), "确认")]'),
    (By.XPATH, '//button[contains(text(), "提交")]'),
    (By.CSS_SELECTOR, "input[type=submit]"),
)
_SAVE_RESULT_KEYWORDS = ("成功", "失败", "保存", "修改")

# ---- 提醒设置 ----
_CHECKBOX_CSS = 'input[type="checkbox"]'
_REMIND_SUBMIT_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "确认提交")]'),
    (By.XPATH, '//input[contains(@value, "提 交")]'),
    (By.XPATH, '//input[@type="submit"]'),
    (By.XPATH, '//button[contains(text(), "确认提交")]'),
    (By.XPATH, '//button[contains(text(), "提交")]'),
    (By.XPATH, '//a[contains(text(), "确认提交")]'),
    (By.XPATH, '//a[contains(text(), "提交")]'),
)

# ---- 杂项页 ----
_PAGE_SPECS = {
    "credit": ("/member/credit/index", "我的积分记录"),
    "safe": ("/member/member/safe", "安全设置"),
    "bank": ("/member/funds/bank", "银行卡信息"),
    "spread": ("/member/spread/myspread", "推广管理"),
}

# ---- 站内消息 ----
_MESSAGE_URL = BASE_URL + "/member/message/index"
_MESSAGE_LINK_CSS = ('a.msg[href*="message/index"], '
                     'a[href*="/member/message/index"]')
_MSG_TITLE_CSS = "table tbody tr a.msg-read"
_MSG_UNREAD_CSS = "table tbody tr a.msg-read:not(.readed)"
_MSG_DETAIL_CSS = "div.sys-msg-detai"
_PAGE_COUNT_RE = re.compile(r"(?:站内信[息]?|未读信?息?)[^0-9]{0,6}(\d+)")
_DIGIT_RE = re.compile(r"\d+")


class MemberManager(BasePage):
    """前台会员业务（登录 / 注册 / 开户 / 额度申请 / 中心总览 / 资料 / 提醒 / 杂项页）。"""

    # ---- 登录页（原 LoginPage） ----
    _login_url = BASE_URL + "/common/member/login"
    _login_phone = (By.ID, "keywords")
    _login_password = (By.ID, "password")
    _login_btn = (By.ID, "login-btn")
    _login_success_text = (By.CLASS_NAME, "a-link1")
    _login_fail_text = (By.CSS_SELECTOR, "span.ng-binding")

    # ---- 注册页（原 RegisterPage） ----
    _register_url = BASE_URL + "/common/member/reg"
    _register_wait_time = 2
    _register_phone = (By.ID, "phone")
    _register_password = (By.ID, "password")
    _register_verifycode = (By.ID, "verifycode")
    _register_get_phone = (By.ID, "get_phone_code")
    _register_phone_code = (By.ID, "phone_code")
    _reg_btn = (By.CLASS_NAME, "lg-btn")
    _register_success_text = (By.XPATH, "//*[text()='注册成功！']")
    _register_fail_text = (By.CLASS_NAME, "reg-title")

    # ---- 托管开户页（原 OpenAccountPage） ----
    _open_account_click_open = (By.LINK_TEXT, "立即开通")
    _open_account_real_name = (By.NAME, "realname")
    _open_account_id_card = (By.NAME, "card_id")
    _open_account_confirm_btn = (By.CSS_SELECTOR, '[value="确认提交"]')
    _open_account_act_now = (By.CSS_SELECTOR, ".btn.ng-scope")
    _open_account_success_text = (By.CSS_SELECTOR, "body")
    _open_account_fail_text = (By.CLASS_NAME, "validation-invalid")

    # ---- 额度申请页（原 CreditApplicationPage） ----
    _credit_switch_account = (By.XPATH, "//em[text()='借款账户']")
    _credit_account_apply = (By.LINK_TEXT, "申请额度")
    _credit_amount = (By.ID, "amount_account")
    _credit_detail_msg = (By.NAME, "remark")
    _credit_img_code = (By.ID, "verifycode")
    _credit_confirm_btn = (By.CSS_SELECTOR, ".btn-submit.btn-md")
    _credit_success_text = (By.XPATH, '//*[@id="amount_list"]/tr[1]/td[3]')
    _credit_fail_text = (By.XPATH, '//label[@class="error"]')

    # ---- 会员中心（原 MemberCenterPage） ----
    _center_url = BASE_URL + "/member/member/center"
    _center_message_link = (By.CSS_SELECTOR,
                            'a.msg[href*="message/index"], a[href*="/member/message/index"]')

    # ---- 基础资料（原 MemberInfoPage） ----
    _info_url = BASE_URL + "/member/info/index"

    # ---- 提醒设置（原 RemindPage） ----
    _remind_url = BASE_URL + "/member/remind/setremind"

    def __init__(self, driver) -> None:
        # 登录表单偶发 10s 以上才渲染可见，实测需放宽显式等待
        super().__init__(driver, timeout=20)
        self._center_unread: Optional[int] = None
        self._message_list_unread: int = 0

    # ============ 登录 ============
    def open_login_url(self):
        self.driver.get(self._login_url)

    def input_login_phone(self, phone):
        self.base_input(self._login_phone, phone)

    def input_login_password(self, password):
        self.base_input(self._login_password, password)

    def click_login_btn(self):
        self.base_click(self._login_btn)

    def get_login_success_text(self):
        return self.fd_element(self._login_success_text).text

    def get_login_fail_text(self):
        return self.fd_element(self._login_fail_text).text

    def login(self, phone, password="Aa123456"):
        self.input_login_phone(phone)
        self.input_login_password(password)
        self.click_login_btn()

    # 对外高层接口
    def open_login_page(self) -> None:
        self.open_login_url()

    def get_login_result_text(self) -> str:
        return self.get_login_success_text()

    # ============ 注册 ============
    def open_register_url(self):
        self.driver.get(self._register_url)

    def input_register_phone(self, phone):
        self.base_input(self._register_phone, phone)

    def input_register_password(self, password):
        self.base_input(self._register_password, password)

    def input_register_verifycode(self, verifycode="8888"):
        self.base_input(self._register_verifycode, verifycode)

    def click_get_phone_code(self):
        self.base_click(self._register_get_phone)

    def input_register_phone_code(self, phone_code="666666"):
        self.base_input(self._register_phone_code, phone_code)

    def click_reg_btn(self):
        self.base_click(self._reg_btn)

    def get_register_success_text(self):
        return self.fd_element(self._register_success_text).text

    def get_register_fail_text(self):
        return self.fd_element(self._register_fail_text).text

    def register(self, phone, password, verifycode="8888", phone_code="666666"):
        self.input_register_phone(phone)
        self.input_register_password(password)
        self.input_register_verifycode(verifycode)
        self.click_get_phone_code()
        time.sleep(self._register_wait_time)
        self.input_register_phone_code(phone_code)
        self.click_reg_btn()
        time.sleep(1)

    # 对外高层接口
    def open_register_page(self) -> None:
        self.open_register_url()

    def get_register_result_text(self) -> str:
        return self.get_register_success_text()

    # ============ 托管开户 ============
    def click_account(self):
        self.base_click(self._open_account_click_open)

    def input_real_name(self, real_name=NAME):
        self.base_input(self._open_account_real_name, real_name)

    def input_id_card(self, id_card=CARD):
        self.base_input(self._open_account_id_card, id_card)

    def click_open_confirm(self):
        self.base_click(self._open_account_confirm_btn)

    def click_act_now(self):
        self.base_click(self._open_account_act_now)

    def get_open_account_success_text(self):
        return self.base_switch_handle(self._open_account_success_text).text

    def get_open_account_fail_text(self):
        return self.fd_element(self._open_account_fail_text).text

    def open_account(self, real_name=NAME, id_card=CARD, expect_success=True):
        self.click_account()
        self.input_real_name(real_name)
        self.input_id_card(id_card)
        self.click_open_confirm()
        if expect_success:
            self.click_act_now()

    # 对外高层接口
    def get_open_account_result_text(self) -> str:
        return self.get_open_account_success_text()

    # ============ 额度申请 ============
    def click_switch_account(self):
        self.base_click(self._credit_switch_account)

    def click_account_apply(self):
        self.base_click(self._credit_account_apply)

    def input_credit_amount(self, amount):
        self.base_input(self._credit_amount, amount)

    def input_detail_msg(self, msg):
        self.base_input(self._credit_detail_msg, msg)

    def input_credit_img_code(self, img_code):
        self.base_input(self._credit_img_code, img_code)

    def click_credit_confirm(self):
        self.base_click(self._credit_confirm_btn)

    def credit_application(self, amount, msg, img_code="8888"):
        self.click_switch_account()
        self.click_account_apply()
        self.input_credit_amount(amount)
        self.input_detail_msg(msg)
        self.input_credit_img_code(img_code)
        self.click_credit_confirm()

    def get_credit_success_text(self):
        return self.fd_element(self._credit_success_text).text

    def get_credit_fail_text(self):
        return self.fd_element(self._credit_fail_text).text

    # 对外高层接口
    def get_credit_application_result_text(self) -> str:
        return self.get_credit_success_text()

    # ============ 会员中心 ============
    def open_center_url(self) -> None:
        self.driver.get(self._center_url)

    def _extract_balance_text(self, timeout: float = 10.0) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                text = self.driver.execute_script(_MEMBER_CENTER_BALANCE_TEXT_JS)
                if text and any(ch.isdigit() for ch in str(text)):
                    match = _MEMBER_CENTER_BALANCE_RE.search(str(text))
                    if match:
                        return match.group(1)
            except Exception:
                pass
            time.sleep(0.5)
        try:
            text = self.driver.execute_script(_MEMBER_CENTER_BALANCE_CONTAINS_JS) or ""
        except Exception:
            text = ""
        match = _MEMBER_CENTER_BALANCE_RE.search(str(text))
        return match.group(1) if match else ""

    def read_balance_text(self, timeout: float = 10.0) -> Optional[float]:
        raw = self._extract_balance_text(timeout=timeout)
        if not raw:
            return None
        try:
            return float(raw.replace(",", ""))
        except ValueError:
            return None

    def read_recent_transactions(self, timeout: float = 8.0) -> Dict[str, Any]:
        deadline = time.time() + timeout
        data: Dict[str, Any] = {}
        while time.time() < deadline:
            try:
                data = self.driver.execute_script(_READ_RECENT_TX_JS) or {}
            except Exception:
                data = {}
            if data.get("found"):
                break
            time.sleep(0.5)
        headers = [str(h) for h in (data.get("headers") or [])]
        rows = [[str(c) for c in row] for row in (data.get("rows") or [])]
        joined = " ".join(" ".join(row) for row in rows)
        body_hint = self._body_has_empty_hint()
        empty_state = (not data.get("found")) or ("暂无" in joined) or (not rows and body_hint)
        return {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
            "empty_state": empty_state,
        }

    def _body_has_empty_hint(self) -> bool:
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return False
        return ("暂无" in body) or ("暂无记录" in body)

    def read_unread_count(self) -> int:
        for _ in range(20):
            try:
                links = self.driver.find_elements(*self._center_message_link)
            except Exception:
                links = []
            for link in links:
                match = re.fullmatch(r"\s*(\d+)\s*", link.text or "")
                if match:
                    return int(match.group(1))
            time.sleep(0.5)
        return 0

    def read_center_info(self) -> Dict[str, Any]:
        balance_text = self._extract_balance_text()
        balance = None
        if balance_text:
            try:
                balance = float(balance_text.replace(",", ""))
            except ValueError:
                balance = None
        return {
            "balance_text": balance_text,
            "balance": balance,
            "unread_count": self.read_unread_count(),
            "risk_level_present": self._has_risk_level_text(),
        }

    def _has_risk_level_text(self) -> bool:
        try:
            return bool(
                self.driver.execute_script(
                    "var els = document.querySelectorAll('*');"
                    "for (var i = 0; i < els.length; i++) {"
                    "    var t = (els[i].textContent || '').trim();"
                    "    if (t.indexOf('风险测评等级') >= 0"
                    "        && t.replace(/\\s+/g, '').length <= 40) { return true; }"
                    "}"
                    "return false;"
                )
            )
        except Exception:
            return False

    # 对外高层接口
    def open_center(self) -> None:
        self.open_center_url()

    def get_center_summary(self) -> Dict[str, Any]:
        self.open_center_url()
        info = self.read_center_info()
        self._center_unread = info.get("unread_count")
        return info

    def get_recent_transactions(self) -> Dict[str, Any]:
        return self.read_recent_transactions()

    # ============ 站内消息 ============
    def open_message_url(self) -> str:
        self.driver.get(_MESSAGE_URL)
        return self.driver.current_url

    def read_topbar_unread(self) -> int:
        for _ in range(20):
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, _MESSAGE_LINK_CSS)
            except Exception:
                links = []
            for link in links:
                match = _DIGIT_RE.fullmatch((link.text or "").strip())
                if match:
                    return int(match.group())
            time.sleep(0.5)
        return 0

    def read_page_unread(self) -> Optional[int]:
        try:
            text = self.driver.execute_script(
                r"""
                var cand = document.querySelectorAll(
                    'h1,h2,h3,h4,h5,legend,td,th,strong,b,span,a,label,li');
                var best = '';
                for (var i = 0; i < cand.length; i++) {
                    var t = (cand[i].textContent || '').trim();
                    if (t && t.length <= 30 && t.indexOf('信') >= 0) {
                        if (/\d/.test(t)) { return t; }
                        if (!best) { best = t; }
                    }
                }
                return best;
                """
            ) or ""
        except Exception:
            return None
        match = _PAGE_COUNT_RE.search(str(text))
        if match:
            return int(match.group(1))
        return None

    def read_message_info(self, center_unread: Optional[int] = None) -> Dict[str, object]:
        final_url = self.open_message_url()
        return {
            "final_url": final_url,
            "topbar_unread": self.read_topbar_unread(),
            "page_unread": self.read_page_unread(),
            "center_unread": center_unread,
        }

    def read_list_rows(self) -> List[Dict[str, object]]:
        rows: List[Dict[str, object]] = []
        for a in self.driver.find_elements(By.CSS_SELECTOR, _MSG_TITLE_CSS):
            cls = a.get_attribute("class") or ""
            rows.append({
                "title": (a.text or "").strip(),
                "unread": "readed" not in cls,
            })
        return rows

    def read_list_unread_count(self) -> int:
        return len(self.driver.find_elements(By.CSS_SELECTOR, _MSG_UNREAD_CSS))

    def read_list_info(self) -> Dict[str, object]:
        final_url = self.open_message_url()
        time.sleep(2)
        rows = self.read_list_rows()
        first_unread = next((r["title"] for r in rows if r["unread"]), "")
        return {
            "final_url": final_url,
            "topbar_unread": self.read_topbar_unread(),
            "row_count": len(rows),
            "list_unread": sum(1 for r in rows if r["unread"]),
            "first_unread_title": first_unread,
            "rows": rows,
        }

    def open_first_unread(self) -> Dict[str, object]:
        topbar_before = self.read_topbar_unread()
        unread = self.driver.find_elements(By.CSS_SELECTOR, _MSG_UNREAD_CSS)
        if not unread:
            return {
                "opened": False, "title": "", "detail_text": "",
                "topbar_before": topbar_before,
                "topbar_after": topbar_before,
                "topbar_delta": 0,
            }
        title = (unread[0].text or "").strip()
        self.driver.execute_script("arguments[0].click();", unread[0])
        detail_text = ""
        for _ in range(10):
            time.sleep(0.5)
            dets = self.driver.find_elements(By.CSS_SELECTOR, _MSG_DETAIL_CSS)
            candidates = [
                (d.text or "").strip()
                for d in dets
                if d.is_displayed()
                and title in (d.text or "")
                and "发件时间" in (d.text or "")
            ]
            if candidates:
                detail_text = max(candidates, key=len)
                break
        topbar_after = self.read_topbar_unread()
        return {
            "opened": True,
            "title": title,
            "detail_text": detail_text,
            "topbar_before": topbar_before,
            "topbar_after": topbar_after,
            "topbar_delta": topbar_before - topbar_after,
        }

    def read_list_info_after_read(self, before_list_unread: int) -> Dict[str, object]:
        info = self.read_list_info()
        info["list_unread_before"] = before_list_unread
        info["list_unread_after"] = info["list_unread"]
        info["list_unread_delta"] = before_list_unread - int(info["list_unread"])
        return info

    # 对外高层接口
    def get_message_page_info(self) -> Dict[str, Any]:
        return self.read_message_info(center_unread=self._center_unread)

    def get_message_list_info(self) -> Dict[str, Any]:
        info = self.read_list_info()
        self._message_list_unread = int(info.get("list_unread", 0))
        return info

    def open_first_unread_message(self) -> Dict[str, Any]:
        return self.open_first_unread()

    def get_message_relist_info(self) -> Dict[str, Any]:
        before = getattr(self, "_message_list_unread", 0)
        return self.read_list_info_after_read(before)

    # ============ 基础资料 ============
    def open_info_url(self) -> None:
        self.driver.get(self._info_url)

    def read_profile_field(self, field_name: str, timeout: float = 8.0) -> str:
        deadline = time.time() + timeout
        while True:
            selects = self.driver.find_elements(
                By.CSS_SELECTOR, f'select[name="{field_name}"]'
            )
            if selects:
                select = Select(selects[0])
            else:
                select = None
            if select is not None:
                try:
                    options = select.options
                    text = select.first_selected_option.text.strip()
                except Exception:
                    options = []
                    text = ""
                if len(options) > 1 and text and text != "请选择":
                    return text
                if time.time() >= deadline:
                    return text
                time.sleep(0.4)
                continue
            inputs = self.driver.find_elements(
                By.CSS_SELECTOR, f'input[name="{field_name}"], input#{field_name}'
            )
            if inputs:
                value = (inputs[0].get_attribute("value") or "").strip()
                if value or time.time() >= deadline:
                    return value
                time.sleep(0.4)
                continue
            if time.time() >= deadline:
                return ""
            time.sleep(0.4)

    def read_all_profile(self) -> Dict[str, str]:
        profile: Dict[str, str] = {}
        for field in _PROFILE_SELECT_FIELDS:
            profile[field] = self.read_profile_field(field)
        for field in _PROFILE_INPUT_FIELDS:
            profile[field] = self.read_profile_field(field)
        return profile

    def click_edit(self) -> bool:
        return self._click_first_visible(_EDIT_BUTTON_CANDIDATES)

    def edit_profile_field(self, field_name: str, value: str) -> bool:
        if self._is_field_disabled(field_name):
            self.click_edit()
            self._wait_field_enabled(field_name)
        return self._do_edit_field(field_name, value)

    def _is_field_disabled(self, field_name: str) -> bool:
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            f'select[name="{field_name}"],input[name="{field_name}"],input#{field_name}',
        )
        if not elements:
            return False
        return not elements[0].is_enabled()

    def _wait_field_enabled(self, field_name: str, timeout: float = 6.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self._is_field_disabled(field_name):
                selects = self.driver.find_elements(
                    By.CSS_SELECTOR, f'select[name="{field_name}"]'
                )
                if not selects or len(Select(selects[0]).options) > 1:
                    return True
            time.sleep(0.3)
        return False

    def click_save(self, wait_field: str = "marryStatus", timeout: float = 8.0) -> bool:
        clicked = self._click_first_visible(_SAVE_BUTTON_CANDIDATES)
        if not clicked:
            return False
        deadline = time.time() + timeout
        while time.time() < deadline:
            alert_text = self._accept_alert_if_present(timeout=0.4)
            if alert_text:
                return True
            if self._is_field_disabled(wait_field):
                return True
            time.sleep(0.3)
        return True

    def read_save_result(self) -> str:
        alert_text = self._accept_alert_if_present()
        if alert_text:
            return alert_text
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            return ""
        for line in (body or "").splitlines():
            line = line.strip()
            if line and len(line) <= 40 and any(kw in line for kw in _SAVE_RESULT_KEYWORDS):
                return line
        return ""

    def _do_edit_field(self, field_name: str, value: str) -> bool:
        selects = self.driver.find_elements(
            By.CSS_SELECTOR, f'select[name="{field_name}"]'
        )
        if selects:
            self._select_by_text(selects[0], value)
            return True
        inputs = self.driver.find_elements(
            By.CSS_SELECTOR, f'input[name="{field_name}"], input#{field_name}'
        )
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys(value)
            return True
        return False

    def _select_by_text(self, element, value: str) -> None:
        select = Select(element)
        try:
            select.select_by_visible_text(value)
        except Exception:
            for option in select.options:
                if value and value in (option.text or "").strip():
                    select.select_by_visible_text(option.text)
                    return
            raise

    # 对外高层接口
    def read_profile(self) -> Dict[str, str]:
        self.open_info_url()
        return self.read_all_profile()

    def read_profile_field(self, field: str) -> str:
        self.open_info_url()
        return self.read_profile_field(field)

    # ============ 提醒设置 ============
    def open_remind_url(self) -> None:
        self.driver.get(self._remind_url)

    def read_checkbox_state(self, checkbox_id: str) -> bool:
        elements = self.driver.find_elements(By.ID, checkbox_id)
        if not elements:
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, f'input[type="checkbox"][name="{checkbox_id}"]'
            )
        if not elements:
            return False
        return bool(elements[0].is_selected())

    def read_all_states(self) -> Dict[str, bool]:
        states: Dict[str, bool] = {}
        boxes = self.driver.find_elements(By.CSS_SELECTOR, _CHECKBOX_CSS)
        for box in boxes:
            key = (box.get_attribute("id") or box.get_attribute("name") or "").strip()
            if key:
                states[key] = bool(box.is_selected())
        return states

    def toggle_checkbox(self, checkbox_id: str) -> bool:
        before = self.read_checkbox_state(checkbox_id)
        elements = self.driver.find_elements(By.ID, checkbox_id)
        if not elements:
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, f'input[type="checkbox"][name="{checkbox_id}"]'
            )
        if not elements:
            raise ValueError(f"提醒复选框不存在: {checkbox_id}")
        elements[0].click()
        return before

    def click_remind_submit(self) -> bool:
        for by, value in _REMIND_SUBMIT_CANDIDATES:
            try:
                visible = next(
                    (e for e in self.driver.find_elements(by, value) if e.is_displayed()),
                    None,
                )
                if visible:
                    visible.click()
                    self._accept_alert_if_present()
                    return True
            except Exception:
                continue
        return False

    def read_submit_result(self) -> str:
        alert_text = self._accept_alert_if_present()
        if alert_text:
            return alert_text
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return ""
        for line in body.splitlines():
            line = line.strip()
            if line and len(line) <= 40 and ("成功" in line or "失败" in line):
                return line
        return ""

    # 对外高层接口
    def read_remind_states(self) -> Dict[str, bool]:
        self.open_remind_url()
        return self.read_all_states()

    def read_remind_state(self, checkbox_id: str) -> bool:
        self.open_remind_url()
        return self.read_checkbox_state(checkbox_id)

    def toggle_remind(self, checkbox_id: str) -> Dict[str, Any]:
        self.open_remind_url()
        before = self.toggle_checkbox(checkbox_id)
        submitted = self.click_remind_submit()
        result_text = self.read_submit_result() if submitted else ""
        return {
            "checkbox_id": checkbox_id,
            "before": before,
            "submitted": submitted,
            "result_text": result_text,
        }

    # ============ 杂项页 ============
    def open_page(self, page: str) -> str:
        spec = _PAGE_SPECS.get(page)
        if spec is None:
            raise ValueError(f"未知账户管理页面: {page}")
        self.driver.get(BASE_URL + spec[0])
        return self.driver.current_url

    def page_spec(self, page: str) -> Dict[str, str]:
        path, head = _PAGE_SPECS[page]
        return {"path": path, "expected_head": head}

    def has_heading(self, expected_head: str) -> bool:
        try:
            return bool(
                self.driver.execute_script(
                    "var kw = arguments[0];"
                    "var cand = document.querySelectorAll("
                    "'h1,h2,h3,h4,h5,legend,td,th,strong,b,span,a,div,label');"
                    "for (var i = 0; i < cand.length; i++) {"
                    "  var t = (cand[i].textContent || '').trim();"
                    "  if (t && t.length <= 30 && t.indexOf(kw) >= 0) { return true; }"
                    "}"
                    "return false;",
                    expected_head,
                )
            )
        except Exception:
            return False

    def read_page_info(self, page: str) -> Dict[str, object]:
        final_url = self.open_page(page)
        expected_head = _PAGE_SPECS[page][1]
        head_present = self.has_heading(expected_head)
        body_text = self._body_text()
        empty_state = ("暂无" in body_text) or ("温馨提示" in body_text)
        return {
            "page": page,
            "final_url": final_url,
            "expected_head": expected_head,
            "head_present": head_present,
            "empty_state": empty_state,
        }

    def _body_text(self) -> str:
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return ""

    # 对外高层接口
    def open_member_page(self, page: str) -> Dict[str, Any]:
        return self.read_page_info(page)

    # ============ 内部通用工具 ============
    def _click_first_visible(self, candidates) -> bool:
        for by, value in candidates:
            try:
                elements = self.driver.find_elements(by, value)
                visible = next((e for e in elements if e.is_displayed()), None)
                if visible:
                    visible.click()
                    return True
            except Exception:
                continue
        return False

    def _accept_alert_if_present(self, timeout: float = 2.0) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                alert = self.driver.switch_to.alert
                text = (alert.text or "").strip()
                alert.accept()
                return text
            except Exception:
                time.sleep(0.3)
        return ""
