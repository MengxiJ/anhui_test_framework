# Copyright (C) 2026. All rights reserved.
"""前台借款业务核心类（普通类，类内不做单例）。

处理发标全流程：
打开个人借款页 → 点击立即借款 → 填写发标表单 → 提交 → 读取结果文本。
"""
from __future__ import annotations

import time
from typing import Dict

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL


class BorrowManager(BasePage):
    """前台借款（发标）。"""

    _front_url = BASE_URL
    _wait_time = 2

    _borrow_now = (By.CSS_SELECTOR, "a.borrow-now")
    _form = (By.ID, "borrowPublish")
    _person_radio = (By.CSS_SELECTOR, "#borrowPublish input[value='-1']")
    _title = (By.CSS_SELECTOR, "#borrowPublish input[name='name']")
    _use = (By.CSS_SELECTOR, "#borrowPublish select[name='use']")
    _amount = (By.CSS_SELECTOR, "#borrowPublish input[name='amount']")
    _apr = (By.CSS_SELECTOR, "#borrowPublish input[name='apr']")
    _repay_type = (By.CSS_SELECTOR, "#borrowPublish select[name='repay_type']")
    _period = (By.CSS_SELECTOR, "#borrowPublish select[name='period']")
    _validate = (By.CSS_SELECTOR, "#borrowPublish select[name='validate']")
    _tender_min = (By.ID, "tender_amount_min")
    _tender_max = (By.ID, "tender_amount_max")
    _contents = (By.ID, "borrow_contents")
    _valicode = (By.CSS_SELECTOR, "#borrowPublish input[name='valicode']")
    _submit = (By.ID, "borrowForm")
    _body = (By.TAG_NAME, "body")

    def __init__(self, driver) -> None:
        super().__init__(driver)

    # ---- 发标 ----
    def open_loan_index(self) -> None:
        """打开「品质理财 → 个人借款」页。"""
        self.driver.get(self._front_url.rstrip("/") + "/loan/loan/index")
        time.sleep(self._wait_time)

    def click_borrow_now(self, index: int = 0) -> None:
        """点击第 index 张标种卡「立即借款」，进入 loanview 发标表单。"""
        buttons = self.driver.find_elements(*self._borrow_now)
        if not buttons:
            raise RuntimeError("个人借款页未找到「立即借款」入口")
        buttons[min(index, len(buttons) - 1)].click()
        self.fd_element(self._submit)
        time.sleep(self._wait_time)

    def fill_publish_form(
        self,
        title: str,
        use: str = "周转",
        amount: str = "200",
        apr: str = "5",
        repay_type: str = "等额本息",
        period: str = "1个月",
        validate: str = "3天",
        tender_min: str = "50元",
        tender_max: str = "不限",
        contents: str = "自动化测试借款标，到期还本付息。",
        valicode: str = "8888",
    ) -> None:
        """填写发标表单（不提交）。"""
        self.base_click_special(self._person_radio)
        self.base_input(self._title, title)
        self.base_select_list(self._use, use)
        self.base_input(self._amount, amount)
        self.base_input(self._apr, apr)
        self.base_select_list(self._repay_type, repay_type)
        self.base_select_list(self._period, period)
        self.base_select_list(self._validate, validate)
        self.base_select_list(self._tender_min, tender_min)
        self.base_select_list(self._tender_max, tender_max)
        self.base_input(self._contents, contents)
        self.base_input(self._valicode, valicode)

    def submit_publish(self) -> None:
        """提交发标表单。"""
        self.base_click(self._submit)
        time.sleep(self._wait_time + 1)

    def publish_loan(
        self,
        title: str,
        use: str = "周转",
        amount: str = "200",
        apr: str = "5",
        repay_type: str = "等额本息",
        period: str = "1个月",
        validate: str = "3天",
        tender_min: str = "50元",
        tender_max: str = "不限",
        contents: str = "自动化测试借款标，到期还本付息。",
        valicode: str = "8888",
    ) -> Dict[str, any]:
        """发标完整流程（进入表单 → 填写 → 提交）。"""
        self.click_borrow_now()
        self.fill_publish_form(
            title=title,
            use=use,
            amount=amount,
            apr=apr,
            repay_type=repay_type,
            period=period,
            validate=validate,
            tender_min=tender_min,
            tender_max=tender_max,
            contents=contents,
            valicode=valicode,
        )
        self.submit_publish()
        return {
            "title": title,
            "amount": amount,
            "submitted": True,
        }

    def get_publish_result_text(self) -> str:
        """读取发标提交后的页面文本（含成功/失败提示）。"""
        time.sleep(self._wait_time)
        return self.fd_element(self._body).text
