# Copyright (C) 2026. All rights reserved.
"""投资域核心类（普通类，类内不做单例）。

组合风险测评 / 投资列表 / 标的详情 / 我的投资 / 理财巡检五个 PageObject，
复用 ``BrowserManager`` 通用能力；本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from lib.common.browser.utils.browser_manager import BrowserManager
from lib.common.core.utils.text_number import parse_number_text
from lib.common.invest.pages import (
    InvestListPage,
    InvestPages,
    LoanDetailPage,
    MyTenderPage,
    RiskQuizPage,
)
from lib.core.project_config import BASE_URL

_MEMBER_CENTER_URL = BASE_URL + "/member/member/center"


class InvestManager:
    """前台理财业务（测评 / 选标投标 / 我的投资 / 理财巡检）。"""

    def __init__(self, driver) -> None:
        self.driver = driver
        self._risk_quiz_page: Optional[RiskQuizPage] = None
        self._invest_list_page: Optional[InvestListPage] = None
        self._loan_detail_page: Optional[LoanDetailPage] = None
        self._my_tender_page: Optional[MyTenderPage] = None
        self._invest_pages: Optional[InvestPages] = None
        self._browser: Optional[BrowserManager] = None

    # ---- 页面对象懒加载 ----
    @property
    def risk_quiz_page(self) -> RiskQuizPage:
        if self._risk_quiz_page is None:
            self._risk_quiz_page = RiskQuizPage(self.driver)
        return self._risk_quiz_page

    @property
    def invest_list_page(self) -> InvestListPage:
        if self._invest_list_page is None:
            self._invest_list_page = InvestListPage(self.driver)
        return self._invest_list_page

    @property
    def loan_detail_page(self) -> LoanDetailPage:
        if self._loan_detail_page is None:
            self._loan_detail_page = LoanDetailPage(self.driver)
        return self._loan_detail_page

    @property
    def my_tender_page(self) -> MyTenderPage:
        if self._my_tender_page is None:
            self._my_tender_page = MyTenderPage(self.driver)
        return self._my_tender_page

    @property
    def invest_pages(self) -> InvestPages:
        if self._invest_pages is None:
            self._invest_pages = InvestPages(self.driver)
        return self._invest_pages

    @property
    def browser(self) -> BrowserManager:
        if self._browser is None:
            self._browser = BrowserManager(self.driver)
        return self._browser

    # ---- 风险测评 ----
    _LEVEL_KEYWORDS = ("保守", "稳健", "平衡", "成长", "进取", "激进")

    def get_risk_level(self) -> Dict[str, Any]:
        """读取风险测评等级（先读会员中心，读不到时回退测评结果页）。

        Returns:
            {level_text, assessed, source_url}
            ``assessed`` 以等级文本中是否含等级关键词（保守/稳健/…）判定。
        """
        # 1) 会员中心「风险测评等级」标签文本
        self.driver.get(_MEMBER_CENTER_URL)
        time.sleep(2.0)
        level = self.risk_quiz_page.get_level_text()
        source = _MEMBER_CENTER_URL
        assessed = bool(level and any(kw in level for kw in self._LEVEL_KEYWORDS))
        if not assessed:
            # 2) 回退测评结果页 /risk/answer/result（已测评显示等级，未测评弹提示框）
            result_url = BASE_URL + "/risk/answer/result"
            self.driver.get(result_url)
            time.sleep(2.0)
            level_result = self.risk_quiz_page.get_level_text()
            if level_result:
                level = level_result
                source = result_url
                assessed = any(kw in level_result for kw in self._LEVEL_KEYWORDS)
        return {"level_text": level or "", "assessed": assessed, "source_url": source}

    def submit_risk_quiz(self, answers: Optional[List[int]] = None) -> Dict[str, Any]:
        """完成一次风险测评：开页 → 关「风险提示」模态框 → 逐题作答 → 提交。

        Returns:
            {answered, options, missing, final_url, submitted, level_text}
            ``submitted`` 以是否跳转 introduce 页为准。
        """
        page = self.risk_quiz_page
        page.open_url()
        time.sleep(2.0)  # 等待 xubox 模态框弹出
        modal_closed = page.close_risk_modal()
        time.sleep(0.5)
        answer_info = page.answer_quiz(answers)
        page.click_submit()
        time.sleep(3.0)  # 等待整页跳转 introduce
        final_url = str(self.driver.current_url)
        submitted = page.is_on_introduce()
        return {
            **answer_info,
            "modal_closed": modal_closed,
            "submitted": submitted,
            "final_url": final_url,
            "level_text": page.get_level_text() or "",
        }

    # ---- 投资列表 ----
    def list_loans(self, settle_seconds: float = 2.0) -> Dict[str, Any]:
        """打开投资列表并解析标的卡片。"""
        page = self.invest_list_page
        page.open_url()
        page.wait_loaded()
        time.sleep(settle_seconds)  # 等待卡片金额 ng-bind 渲染
        loans = page.read_loan_cards()
        return {"loans": loans, "count": len(loans)}

    def filter_invest_list(self, tag_text: str) -> Dict[str, Any]:
        """打开投资列表 → 按筛选标签（信用标/天标/担保标等）筛选 → 重新读取列表。

        步骤与 check 均调用本方法，故每次自包含地重新打开列表页，
        保证筛选状态确定（不受上一次点击的开关态影响）。
        """
        page = self.invest_list_page
        page.open_url()
        page.wait_loaded()
        applied = page.click_filter_tag(tag_text)
        time.sleep(1.0)
        loans = page.read_loan_cards() if applied else []
        return {"applied": applied, "filter_tag": tag_text, "loans": loans, "count": len(loans)}

    # ---- 选标与投标（窗口期交互 + 降级双态） ----
    def choose_loan_and_open_detail(
        self,
        min_available: float = 0.0,
        index: int = 0,
        exclude_loan_ids: Optional[set] = None,
    ) -> Dict[str, Any]:
        """从投资列表选择标的并点击「马上投标」进入详情页（窗口期读取详情）。

        选标策略完全由运行时数据决定：优先取可投金额 ≥ min_available 且
        可投金额最大的标；无匹配时取第一个可投标。

        Args:
            exclude_loan_ids: 显式排除的 loan_id 集合（例如详情页校验发现
                标的最低投标金额高于拟投金额，回列表重选下一候选）。

        Returns:
            {loan_id, loan_name, available_amount, tender_href, detail_available,
             redirected, detail}
        """
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
                # 可投金额最大者优先（降低满标竞态）
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
        # 重新定位目标卡片的「马上投标」按钮（按 loan_id 匹配 href）
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
        detail_page = self.loan_detail_page
        ready = detail_page.wait_detail_ready()
        detail = detail_page.read_detail_info() if ready else {}
        redirected = not detail_page.is_detail_url(detail_page.current_url())
        # stayed：URL 停留详情页（详情页可达，但数据渲染可能超时）
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
        """选标并校验标的最低投标金额：不满足则排除该标回列表重选下一候选。

        详情页「最低投标金额」是标的级门槛（实测存在 50 元/10000 元不等），
        仅过滤列表可投余额会选中最低门槛高于拟投金额的标，导致 ``tender_it``
        前端静默拦截、确认弹窗不出现。本方法在详情数据就绪后读取
        ``detail.min_amount``，若高于拟投金额则加入排除集重选。

        窗口期详情不可达（无法读取门槛）时直接返回，交由既有降级口径处理；
        所有候选均被排除时返回最后一次选择并置 ``detail_available=False``
        （reason=无满足最低投标金额的标的），同样走降级而非误报失败。
        """
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
                return chosen  # 窗口期/无可投标：走既有降级
            min_amount = (chosen.get("detail") or {}).get("min_amount")
            if min_amount is None or wanted >= float(min_amount):
                return chosen  # 满足门槛（或门槛读不到时不阻塞业务）
            # 门槛高于拟投金额：排除并回列表重选
            if chosen.get("loan_id") is not None:
                excluded.add(chosen["loan_id"])
        # 候选耗尽：全部标的最低投标金额都高于拟投金额
        assert last is not None
        last["detail_available"] = False
        last["redirected"] = True
        last["reason"] = "无满足最低投标金额的标的（候选均已排除）"
        return last

    def tender(self, amount: Any, min_available: float = 0.0) -> Dict[str, Any]:
        """完整投标：列表选标 → 详情页窗口期输金额 → 提交（捕获拦截证据）。

        Returns:
            {loan_id, loan_name, amount, amount_input, submit_clicked,
             confirm_modal_opened, modal_confirmed,
             final_url, redirected, detail}
            站点在窗口期重定向回列表时 amount_input/submit_clicked 为 False，
            由 check 做降级双态判定。
            投标为两段式：submit_clicked=外层「确认投标」已点（弹窗已唤起），
            modal_confirmed=iframe 弹窗内「马上投标」已点（订单真正提交）。
        """
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
        detail_page = self.loan_detail_page
        if not chosen["detail_available"]:
            result.update(
                {
                    "amount_input": False,
                    "submit_clicked": False,
                    "confirm_modal_opened": False,
                    "modal_confirmed": False,
                    "redirected": chosen["redirected"],
                    "stayed": chosen.get("stayed", False),
                    "final_url": detail_page.current_url(),
                }
            )
            return result
        amount_input = detail_page.input_amount(amount)
        submit_info = detail_page.click_tender_submit() if amount_input else {
            "outer_clicked": False,
            "confirm_modal": False,
            "confirm_clicked": False,
        }
        time.sleep(2.0)
        # 提交后交互证据：alert / 新窗口 / URL（成功路径无 alert，订单直接生成）
        alert = self.browser.accept_alert(timeout=3)
        result.update(
            {
                "amount_input": amount_input,
                "submit_clicked": submit_info["outer_clicked"],
                "confirm_modal_opened": submit_info["confirm_modal"],
                "modal_confirmed": submit_info["confirm_clicked"],
                "redirected": not detail_page.is_detail_url(detail_page.current_url()),
                "final_url": str(self.driver.current_url),
                "alert_present": alert["present"],
                "alert_text": alert["text"],
            }
        )
        return result

    def _click_tender_by_loan_id(self, loan_id: Optional[int]) -> Optional[str]:
        """按 loan_id 匹配卡片的「马上投标」按钮并点击（无 id 时点第一个）。"""
        from selenium.webdriver.common.by import By

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
        # 未精确匹配到 id（列表可能已翻页/重渲染）：回退第一个
        href = buttons[0].get_attribute("href") or ""
        buttons[0].click()
        return href

    # ---- 我的投资 ----
    def get_my_tender_records(self, tab: Optional[str] = None) -> Dict[str, Any]:
        """打开我的投资页，切换 tab 并读取记录表格。"""
        page = self.my_tender_page
        page.open_url()
        time.sleep(2.0)
        tabs = page.read_tabs()
        current_tab = None
        if tab and tab in tabs:
            if page.switch_tab(tab):
                current_tab = tab
        elif tabs:
            current_tab = tabs[0]
        table = page.read_current_table()
        return {"tabs": tabs, "current_tab": current_tab, **table}

    def get_my_tender_all_tabs(self) -> Dict[str, Dict[str, Any]]:
        """打开我的投资页，逐 tab 读取全部记录。"""
        page = self.my_tender_page
        page.open_url()
        time.sleep(2.0)
        return page.read_all_tabs()

    # ---- 理财巡检 ----
    def get_receive_plan(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """打开收款计划页（可选日期筛选）读取表格。"""
        page = self.invest_pages
        url = page.open_receive_plan()
        time.sleep(1.5)
        if start_date or end_date:
            table = page.filter_receive_plan(start_date, end_date)
            table["filtered"] = {"start_date": start_date, "end_date": end_date}
        else:
            table = page.read_receive_plan_table()
            table["filtered"] = {}
        table["url"] = url
        return table

    def get_debt_transfer(
        self, status: str = ""
    ) -> Dict[str, Any]:
        """打开债权转让页（可选状态筛选）读取表格与筛选项。"""
        page = self.invest_pages
        url = page.open_debt_page()
        time.sleep(2.0)
        options = page.read_debt_filter_options()
        applied = False
        if status:
            applied = page.filter_debt_by_status(status)
            time.sleep(1.0)
        tables = page.read_debt_tables()
        return {
            "url": url,
            "filter_options": options,
            "applied_filter": status if applied else "",
            "tables": tables,
            "table_count": len(tables),
            "total_rows": sum(t["row_count"] for t in tables),
        }

    def open_auto_tender_entry(self) -> Dict[str, Any]:
        """打开自动投标入口并捕获重定向（未开通托管时跳托管页）。"""
        return self.invest_pages.open_auto_tender_entry()
