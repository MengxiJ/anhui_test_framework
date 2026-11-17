# Copyright (C) 2026. All rights reserved.
"""投资域核心类（普通类，类内不做单例）。

处理风险测评 / 投资列表 / 标的详情 / 我的投资 / 理财巡检业务，
复用 ``BrowserManager`` 通用能力；本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from lib.common.browser.utils.browser_manager import BrowserManager
from lib.common.core.utils.text_number import parse_number_text
from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

_MEMBER_CENTER_URL = BASE_URL + "/member/member/center"

# ---- 风险测评 ----
QUESTION_COUNT = 10

# ---- 投资列表 ----
_LIST_AVAILABLE_RE = re.compile(r"可投[:：]?\s*([\d,\.]+)\s*元")
_LIST_LOAN_ID_RE = re.compile(r"[?&]id=(\d+)")
_PARSE_LOANS_JS = (
    "var cards = document.querySelectorAll('.loan-item');"
    "var r = [];"
    "for (var i = 0; i < cards.length; i++) {"
    "    var c = cards[i];"
    "    var tit = c.querySelector('a.tit');"
    "    var btn = null;"
    "    var links = c.querySelectorAll('a');"
    "    for (var j = 0; j < links.length; j++) {"
    "        if ((links[j].textContent || '').trim().indexOf('马上投标') >= 0) { btn = links[j]; break; }"
    "    }"
    "    r.push({"
    "        name: tit ? (tit.getAttribute('title') || tit.textContent || '').trim() : '',"
    "        title: tit ? tit.textContent.trim() : '',"
    "        text: c.textContent.replace(/\\s+/g, ' ').trim().substring(0, 200),"
    "        tender_href: btn ? btn.href : ''"
    "    });"
    "}"
    "return r;"
)

# ---- 标的详情 ----
_MIN_AMOUNT_RE = re.compile(r"最低投标金额[:：]?\s*([\d,\.]+)")
_DETAIL_AVAILABLE_RE = re.compile(r"可投金额[:：]?\s*([\d,\.]+)")
_BALANCE_RE = re.compile(r"可用余额[:：]?\s*([\d,\.]+)")

# ---- 我的投资 ----
DEFAULT_TABS = ("回款中", "投标中", "已结清", "已流标")

# ---- 理财巡检 ----
_RECEIVE_PLAN_KEYWORDS = ("应收", "标题")
_DEBT_FILTER_OPTIONS = ("全部", "可以转让", "转让中", "转让成功", "已撤销")


class InvestManager(BasePage):
    """前台理财业务（测评 / 选标投标 / 我的投资 / 理财巡检）。"""

    # ---- 风险测评（原 RiskQuizPage） ----
    _quiz_url = BASE_URL + "/risk/answer/record"
    _quiz_modal_close = (By.CSS_SELECTOR, "a.xubox_close")
    _question_radio_fmt = 'input[type=radio][name="{qid}"]'
    _quiz_submit_candidates = (
        (By.CSS_SELECTOR, "input.btnbgoragne"),
        (By.CSS_SELECTOR, 'input[type=submit][value="提交"]'),
        (By.CSS_SELECTOR, "input[type=submit]"),
    )

    # ---- 投资列表（原 InvestListPage） ----
    _list_url = BASE_URL + "/loan/tender/index"
    _list_filter_tag = (By.CSS_SELECTOR, "li.ui-filter-tag")
    _list_tender_button = (By.XPATH, '//a[contains(text(), "马上投标")]')

    # ---- 标的详情（原 LoanDetailPage） ----
    _detail_money_input = (By.ID, "money")
    _detail_tender_id = (By.ID, "tender_id")
    _tender_outer_confirm = (By.CSS_SELECTOR, 'input[type="submit"][ng-click*="tender_it"]')
    _tender_submit_candidates = (
        (By.CSS_SELECTOR, "input.btnbgoragne"),
        (By.XPATH, '//input[@type="submit"]'),
        (By.XPATH, '//a[contains(text(), "立即投资")]'),
    )
    _confirm_iframe = (By.ID, "xubox_iframe1")
    _confirm_submit = (By.ID, "tender_new_submit")

    # ---- 我的投资（原 MyTenderPage） ----
    _my_tender_url = BASE_URL + "/loan/tender/mytender"
    _my_tender_tab_items = (By.CSS_SELECTOR, "li")
    _my_tender_tables = (By.TAG_NAME, "table")

    # ---- 理财巡检（原 InvestPages） ----
    _receive_plan_url = BASE_URL + "/loan/recover/index"
    _debt_url = BASE_URL + "/loan/transfer/mytransfer"
    _auto_tender_url = BASE_URL + "/loan/loan/auto"
    _receive_start_date = (By.ID, "start")
    _receive_end_date = (By.ID, "end")
    _receive_filter = (By.CSS_SELECTOR, 'input.btn-search[value="筛选"], input[value="筛选"]')
    _debt_select = (By.ID, "change_nid")
    _ip_tables = (By.TAG_NAME, "table")

    def __init__(self, driver) -> None:
        super().__init__(driver)
        self._browser: Optional[BrowserManager] = None

    @property
    def browser(self) -> BrowserManager:
        if self._browser is None:
            self._browser = BrowserManager(self.driver)
        return self._browser

    # ============ 风险测评 ============
    def open_quiz_url(self) -> None:
        self.driver.get(self._quiz_url)

    def close_risk_modal(self, timeout: float = 3.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                close_btns = self.driver.find_elements(*self._quiz_modal_close)
                if close_btns:
                    self.driver.execute_script("arguments[0].click();", close_btns[0])
                    time.sleep(0.5)
                    return True
            except Exception:
                pass
            time.sleep(0.3)
        return False

    def answer_quiz(self, answers: Optional[List[int]] = None) -> Dict[str, Any]:
        plan: Dict[int, int] = {}
        for qid in range(1, QUESTION_COUNT + 1):
            default = 0
            if answers and len(answers) >= qid and answers[qid - 1] is not None:
                default = int(answers[qid - 1])
            plan[qid] = default

        answered: List[int] = []
        options: Dict[str, int] = {}
        for qid, opt_index in plan.items():
            selector = self._question_radio_fmt.format(qid=qid)
            radios = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if not radios:
                continue
            index = min(max(opt_index, 0), len(radios) - 1)
            radios[index].click()
            answered.append(qid)
            options[str(qid)] = index
        missing = [q for q in range(1, QUESTION_COUNT + 1) if q not in answered]
        return {"answered": answered, "options": options, "missing": missing}

    def click_quiz_submit(self) -> None:
        last_error: Optional[Exception] = None
        for by, value in self._quiz_submit_candidates:
            try:
                btns = self.driver.find_elements(by, value)
                visible = next((b for b in btns if b.is_displayed()), None)
                if visible:
                    visible.click()
                    return
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"测评提交按钮不可用（最后错误: {last_error}）")

    def is_on_introduce(self) -> bool:
        return "risk/answer/introduce" in str(self.driver.current_url)

    def get_level_text(self) -> Optional[str]:
        try:
            return self.driver.execute_script(
                "var els = document.querySelectorAll('*');"
                "for (var i = 0; i < els.length; i++) {"
                "    var t = (els[i].textContent || '').trim();"
                "    if (t.indexOf('风险测评等级') >= 0) {"
                "        var clean = t.replace(/\\s+/g, '');"
                "        if (clean.length <= 40) { return clean; }"
                "    }"
                "}"
                "return null;"
            )
        except Exception:
            return None

    # ============ 投资列表 ============
    def open_list_url(self) -> None:
        self.driver.get(self._list_url)

    def wait_loaded(self, timeout: float = 10.0) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".loan-item")
        )

    def read_loan_cards(self) -> List[Dict[str, Any]]:
        raw = self.driver.execute_script(_PARSE_LOANS_JS) or []
        loans: List[Dict[str, Any]] = []
        for item in raw:
            text = str(item.get("text", ""))
            href = str(item.get("tender_href", ""))
            m = _LIST_AVAILABLE_RE.search(text)
            amount_text = m.group(1) if m else ""
            amount = None
            if amount_text:
                try:
                    amount = float(amount_text.replace(",", ""))
                except ValueError:
                    amount = None
            loan_id = None
            m2 = _LIST_LOAN_ID_RE.search(href)
            if m2:
                loan_id = int(m2.group(1))
            loans.append(
                {
                    "loan_id": loan_id,
                    "name": str(item.get("name", "")),
                    "available_text": amount_text,
                    "available_amount": amount,
                    "tender_href": href,
                    "can_tender": bool(href),
                }
            )
        return loans

    def read_filter_tags(self) -> List[str]:
        tags = self.driver.find_elements(*self._list_filter_tag)
        return [t.text.strip() for t in tags if t.text.strip()]

    def click_filter_tag(self, tag_text: str, timeout: float = 8.0) -> bool:
        deadline = time.time() + timeout
        target = "".join(str(tag_text).split())
        tags = []
        while time.time() < deadline:
            tags = [t for t in self.driver.find_elements(*self._list_filter_tag) if t.is_displayed()]
            texts = ["".join((t.text or "").split()) for t in tags]
            if any(t == target or (target and target in t) for t in texts):
                break
            time.sleep(0.5)
        for tag in tags:
            text = "".join((tag.text or "").split())
            if text == target or (target and target in text):
                tag.click()
                time.sleep(1.5)
                return True
        return False

    def click_tender_button(self, index: int = 0) -> Optional[str]:
        WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (e for e in d.find_elements(*self._list_tender_button) if e.is_displayed()),
                None,
            )
        )
        buttons = [
            e for e in self.driver.find_elements(*self._list_tender_button) if e.is_displayed()
        ]
        if not buttons or index >= len(buttons):
            return None
        href = buttons[index].get_attribute("href") or ""
        buttons[index].click()
        return href

    # ============ 标的详情 ============
    @staticmethod
    def is_detail_url(url: str) -> bool:
        return "loaninfoview" in url

    def current_url(self) -> str:
        return str(self.driver.current_url)

    def wait_detail_ready(self, nav_timeout: float = 8.0, ready_timeout: float = 6.0) -> bool:
        nav_deadline = time.time() + nav_timeout
        while time.time() < nav_deadline:
            if self.is_detail_url(self.current_url()):
                break
            time.sleep(0.15)
        else:
            return False
        deadline = time.time() + ready_timeout
        while time.time() < deadline:
            if not self.is_detail_url(self.current_url()):
                return False
            try:
                ids = self.driver.find_elements(*self._detail_tender_id)
                if ids and (ids[0].get_attribute("value") or "").strip():
                    return True
            except Exception:
                pass
            time.sleep(0.15)
        return False

    def read_detail_info(self) -> Dict[str, Any]:
        try:
            tid = self.driver.find_elements(*self._detail_tender_id)
            tender_id = (tid[0].get_attribute("value") if tid else "") or ""
        except Exception:
            tender_id = ""
        try:
            body = self.driver.execute_script(
                "return document.body ? document.body.textContent : '';"
            ) or ""
        except Exception:
            body = ""

        def _num(pattern) -> Optional[float]:
            m = pattern.search(body)
            if not m:
                return None
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                return None

        money_input_present = False
        try:
            money_input_present = bool(self.driver.find_elements(*self._detail_money_input))
        except Exception:
            money_input_present = False
        return {
            "tender_id": tender_id,
            "min_amount": _num(_MIN_AMOUNT_RE),
            "available_amount": _num(_DETAIL_AVAILABLE_RE),
            "balance": _num(_BALANCE_RE),
            "money_input_present": money_input_present,
        }

    def input_amount(self, amount: Any) -> bool:
        try:
            if not self.is_detail_url(self.current_url()):
                return False
            WebDriverWait(self.driver, 1.5).until(
                lambda d: next(
                    (e for e in d.find_elements(*self._detail_money_input) if e.is_displayed()),
                    None,
                )
            )
            inputs = self.driver.find_elements(*self._detail_money_input)
            if not inputs:
                return False
            inputs[0].clear()
            inputs[0].send_keys(str(amount))
            return True
        except Exception:
            return False

    def click_tender_submit(self, modal_timeout: float = 8.0) -> Dict[str, Any]:
        status = {"outer_clicked": False, "confirm_modal": False, "confirm_clicked": False}
        try:
            if not self.is_detail_url(self.current_url()):
                return status
            outer = next(
                (
                    e
                    for e in self.driver.find_elements(*self._tender_outer_confirm)
                    if e.is_displayed()
                ),
                None,
            )
            if outer is None:
                for by, value in self._tender_submit_candidates:
                    try:
                        outer = next(
                            (e for e in self.driver.find_elements(by, value) if e.is_displayed()),
                            None,
                        )
                        if outer is not None:
                            break
                    except Exception:
                        continue
            if outer is None:
                return status
            outer.click()
            status["outer_clicked"] = True

            deadline = time.time() + modal_timeout
            iframe_el = None
            while time.time() < deadline:
                if not self.is_detail_url(self.current_url()):
                    return status
                frames = self.driver.find_elements(*self._confirm_iframe)
                if frames and frames[0].is_displayed():
                    iframe_el = frames[0]
                    break
                time.sleep(0.2)
            if iframe_el is None:
                return status
            status["confirm_modal"] = True

            try:
                self.driver.switch_to.frame(iframe_el)
                inner_deadline = time.time() + modal_timeout
                while time.time() < inner_deadline:
                    buttons = self.driver.find_elements(*self._confirm_submit)
                    visible = next((e for e in buttons if e.is_displayed()), None)
                    if visible is not None:
                        visible.click()
                        status["confirm_clicked"] = True
                        break
                    time.sleep(0.2)
            finally:
                self.driver.switch_to.default_content()
            return status
        except Exception:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
            return status

    # ============ 我的投资 ============
    def open_my_tender_url(self) -> None:
        self.driver.get(self._my_tender_url)

    def read_tabs(self) -> List[str]:
        items = self.driver.find_elements(*self._my_tender_tab_items)
        tabs = []
        for item in items:
            text = item.text.strip()
            if text in DEFAULT_TABS:
                tabs.append(text)
        return tabs

    def switch_tab(self, tab_name: str) -> bool:
        items = self.driver.find_elements(*self._my_tender_tab_items)
        for item in items:
            if item.text.strip() == tab_name:
                try:
                    item.click()
                except Exception:
                    time.sleep(0.5)
                    item.click()
                time.sleep(1.5)
                return True
        return False

    def read_current_table(self) -> Dict[str, Any]:
        tables = self.driver.find_elements(*self._my_tender_tables)
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
            except Exception:
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
        result: Dict[str, Dict[str, Any]] = {}
        for tab in self.read_tabs():
            if self.switch_tab(tab):
                result[tab] = self.read_current_table()
        return result

    # ============ 理财巡检 ============
    def open_receive_plan(self) -> str:
        self.driver.get(self._receive_plan_url)
        return str(self.driver.current_url)

    def read_receive_plan_table(self, timeout: float = 10.0) -> Dict[str, Any]:
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
        if start_date:
            self._input_clear(self._receive_start_date, start_date)
        if end_date:
            self._input_clear(self._receive_end_date, end_date)
        try:
            buttons = self.driver.find_elements(*self._receive_filter)
            if buttons:
                buttons[0].click()
        except Exception:
            pass
        time.sleep(1.5)
        return self.read_receive_plan_table()

    def open_debt_page(self) -> str:
        self.driver.get(self._debt_url)
        return str(self.driver.current_url)

    def read_debt_filter_options(self) -> List[str]:
        try:
            selects = self.driver.find_elements(*self._debt_select)
            if not selects:
                return []
            return [o.text.strip() for o in Select(selects[0]).options if o.text.strip()]
        except Exception:
            return []

    def filter_debt_by_status(self, option_text: str) -> bool:
        try:
            selects = self.driver.find_elements(*self._debt_select)
            if not selects:
                return False
            select = Select(selects[0])
            for option in select.options:
                if option_text and option_text in (option.text.strip() or ""):
                    select.select_by_visible_text(option.text)
                    time.sleep(1.5)
                    return True
            return False
        except Exception:
            return False

    def read_debt_tables(self) -> List[Dict[str, Any]]:
        return self._read_all_tables()

    def open_auto_tender_entry(self) -> Dict[str, Any]:
        requested = self._auto_tender_url
        try:
            self.driver.get(requested)
        except Exception:
            pass
        time.sleep(2.0)
        final_url = str(self.driver.current_url)
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

    # ============ 内部工具 ============
    def _input_clear(self, locator, value: str) -> None:
        inputs = self.driver.find_elements(*locator)
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys(value)

    def _read_all_tables(self) -> List[Dict[str, Any]]:
        tables = self.driver.find_elements(*self._ip_tables)
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
            except Exception:
                continue
        return result

    def _read_best_table(self, header_keywords) -> Dict[str, Any]:
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

    # ============ 对外业务接口 ============
    _LEVEL_KEYWORDS = ("保守", "稳健", "平衡", "成长", "进取", "激进")

    def get_risk_level(self) -> Dict[str, Any]:
        self.driver.get(_MEMBER_CENTER_URL)
        time.sleep(2.0)
        level = self.get_level_text()
        source = _MEMBER_CENTER_URL
        assessed = bool(level and any(kw in level for kw in self._LEVEL_KEYWORDS))
        if not assessed:
            result_url = BASE_URL + "/risk/answer/result"
            self.driver.get(result_url)
            time.sleep(2.0)
            level_result = self.get_level_text()
            if level_result:
                level = level_result
                source = result_url
                assessed = any(kw in level_result for kw in self._LEVEL_KEYWORDS)
        return {"level_text": level or "", "assessed": assessed, "source_url": source}

    def submit_risk_quiz(self, answers: Optional[List[int]] = None) -> Dict[str, Any]:
        self.open_quiz_url()
        time.sleep(2.0)
        modal_closed = self.close_risk_modal()
        time.sleep(0.5)
        answer_info = self.answer_quiz(answers)
        self.click_quiz_submit()
        time.sleep(3.0)
        final_url = str(self.driver.current_url)
        submitted = self.is_on_introduce()
        return {
            **answer_info,
            "modal_closed": modal_closed,
            "submitted": submitted,
            "final_url": final_url,
            "level_text": self.get_level_text() or "",
        }

    # ---- 投资列表 ----
    def list_loans(self, settle_seconds: float = 2.0) -> Dict[str, Any]:
        self.open_list_url()
        self.wait_loaded()
        time.sleep(settle_seconds)
        loans = self.read_loan_cards()
        return {"loans": loans, "count": len(loans)}

    def filter_invest_list(self, tag_text: str) -> Dict[str, Any]:
        self.open_list_url()
        self.wait_loaded()
        applied = self.click_filter_tag(tag_text)
        time.sleep(1.0)
        loans = self.read_loan_cards() if applied else []
        return {"applied": applied, "filter_tag": tag_text, "loans": loans, "count": len(loans)}

    # ---- 选标与投标 ----
    def choose_loan_and_open_detail(
        self,
        min_available: float = 0.0,
        index: int = 0,
        exclude_loan_ids: Optional[set] = None,
    ) -> Dict[str, Any]:
        excluded = exclude_loan_ids or set()
        listing = self.list_loans()
        loans: List[Dict[str, Any]] = listing["loans"]
        candidates = [
            loan
            for loan in loans
            if loan["can_tender"]
            and loan["available_amount"] is not None
            and loan["loan_id"] not in excluded
        ]
        target: Optional[Dict[str, Any]] = None
        if min_available > 0:
            matched = [loan for loan in candidates if loan["available_amount"] >= min_available]
            if matched:
                target = max(matched, key=lambda loan: loan["available_amount"])
        if target is None and candidates:
            target = candidates[min(index, len(candidates) - 1)]
        if target is None:
            return {
                "loan_id": None,
                "loan_name": "",
                "available_amount": None,
                "tender_href": "",
                "detail_available": False,
                "redirected": True,
                "stayed": False,
                "detail": {},
                "reason": "排除后无可投标的" if excluded else "投资列表无可投标的",
            }
        href = self._click_tender_by_loan_id(target["loan_id"])
        if href is None:
            return {
                "loan_id": target["loan_id"],
                "loan_name": target["name"],
                "available_amount": target["available_amount"],
                "tender_href": target["tender_href"],
                "detail_available": False,
                "redirected": True,
                "stayed": False,
                "detail": {},
                "reason": "未找到目标标的的「马上投标」按钮",
            }
        ready = self.wait_detail_ready()
        detail = self.read_detail_info() if ready else {}
        redirected = not self.is_detail_url(self.current_url())
        stayed = not redirected
        return {
            "loan_id": target["loan_id"],
            "loan_name": target["name"],
            "available_amount": target["available_amount"],
            "tender_href": href,
            "detail_available": ready,
            "redirected": redirected,
            "stayed": stayed,
            "detail": detail,
        }

    def _choose_eligible_loan(
        self, amount: Any, min_available: float = 0.0, max_attempts: int = 4
    ) -> Dict[str, Any]:
        try:
            wanted = float(parse_number_text(amount))
        except (TypeError, ValueError):
            wanted = 0.0
        excluded: set = set()
        last: Optional[Dict[str, Any]] = None
        for _ in range(max(1, max_attempts)):
            chosen = self.choose_loan_and_open_detail(
                min_available=min_available, exclude_loan_ids=excluded
            )
            last = chosen
            if not chosen.get("detail_available"):
                return chosen
            min_amount = (chosen.get("detail") or {}).get("min_amount")
            if min_amount is None or wanted >= float(min_amount):
                return chosen
            if chosen.get("loan_id") is not None:
                excluded.add(chosen["loan_id"])
        assert last is not None
        last["detail_available"] = False
        last["redirected"] = True
        last["reason"] = "无满足最低投标金额的标的（候选均已排除）"
        return last

    def tender(self, amount: Any, min_available: float = 0.0) -> Dict[str, Any]:
        chosen = self._choose_eligible_loan(
            amount=amount, min_available=min_available, max_attempts=4
        )
        result: Dict[str, Any] = {
            "loan_id": chosen["loan_id"],
            "loan_name": chosen["loan_name"],
            "available_amount": chosen["available_amount"],
            "amount": float(parse_number_text(amount)) if amount else 0.0,
            "detail_available": chosen["detail_available"],
            "detail": chosen["detail"],
        }
        if not chosen["detail_available"]:
            result.update(
                {
                    "amount_input": False,
                    "submit_clicked": False,
                    "confirm_modal_opened": False,
                    "modal_confirmed": False,
                    "redirected": chosen["redirected"],
                    "stayed": chosen.get("stayed", False),
                    "final_url": self.current_url(),
                }
            )
            return result
        amount_input = self.input_amount(amount)
        submit_info = self.click_tender_submit() if amount_input else {
            "outer_clicked": False,
            "confirm_modal": False,
            "confirm_clicked": False,
        }
        time.sleep(2.0)
        alert = self.browser.accept_alert(timeout=3)
        result.update(
            {
                "amount_input": amount_input,
                "submit_clicked": submit_info["outer_clicked"],
                "confirm_modal_opened": submit_info["confirm_modal"],
                "modal_confirmed": submit_info["confirm_clicked"],
                "redirected": not self.is_detail_url(self.current_url()),
                "final_url": str(self.driver.current_url),
                "alert_present": alert["present"],
                "alert_text": alert["text"],
            }
        )
        return result

    def _click_tender_by_loan_id(self, loan_id: Optional[int]) -> Optional[str]:
        buttons = [
            e
            for e in self.driver.find_elements(
                By.XPATH, '//a[contains(text(), "马上投标")]'
            )
            if e.is_displayed()
        ]
        if not buttons:
            return None
        if loan_id is None:
            href = buttons[0].get_attribute("href") or ""
            buttons[0].click()
            return href
        for button in buttons:
            href = button.get_attribute("href") or ""
            if f"id={loan_id}" in href or f"id={loan_id}&" in href:
                button.click()
                return href
        href = buttons[0].get_attribute("href") or ""
        buttons[0].click()
        return href

    # ---- 我的投资 ----
    def get_my_tender_records(self, tab: Optional[str] = None) -> Dict[str, Any]:
        self.open_my_tender_url()
        time.sleep(2.0)
        tabs = self.read_tabs()
        current_tab = None
        if tab and tab in tabs:
            if self.switch_tab(tab):
                current_tab = tab
        elif tabs:
            current_tab = tabs[0]
        table = self.read_current_table()
        return {"tabs": tabs, "current_tab": current_tab, **table}

    def get_my_tender_all_tabs(self) -> Dict[str, Dict[str, Any]]:
        self.open_my_tender_url()
        time.sleep(2.0)
        return self.read_all_tabs()

    # ---- 理财巡检 ----
    def get_receive_plan(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        url = self.open_receive_plan()
        time.sleep(1.5)
        if start_date or end_date:
            table = self.filter_receive_plan(start_date, end_date)
            table["filtered"] = {"start_date": start_date, "end_date": end_date}
        else:
            table = self.read_receive_plan_table()
            table["filtered"] = {}
        table["url"] = url
        return table

    def get_debt_transfer(self, status: str = "") -> Dict[str, Any]:
        url = self.open_debt_page()
        time.sleep(2.0)
        options = self.read_debt_filter_options()
        applied = False
        if status:
            applied = self.filter_debt_by_status(status)
            time.sleep(1.0)
        tables = self.read_debt_tables()
        return {
            "url": url,
            "filter_options": options,
            "applied_filter": status if applied else "",
            "tables": tables,
            "table_count": len(tables),
            "total_rows": sum(t["row_count"] for t in tables),
        }
