# Copyright (C) 2026. All rights reserved.
"""前台借款业务核心类（普通类，类内不做单例）。

组合 ``BorrowPublishPage``，处理发标全流程：
打开个人借款页 → 点击立即借款 → 填写发标表单 → 提交 → 读取结果文本。
"""
from __future__ import annotations

from typing import Dict, Optional

from lib.common.borrow.pages import BorrowPublishPage


class BorrowManager:
    """前台借款（发标）。"""

    def __init__(self, driver) -> None:
        self.driver = driver
        self._publish_page: Optional[BorrowPublishPage] = None

    @property
    def publish_page(self) -> BorrowPublishPage:
        if self._publish_page is None:
            self._publish_page = BorrowPublishPage(self.driver)
        return self._publish_page

    # ---- 发标 ----
    def open_loan_index(self) -> None:
        """打开「品质理财 → 个人借款」页。"""
        self.publish_page.open_loan_index()

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
        page = self.publish_page
        page.click_borrow_now()
        page.fill_publish_form(
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
        page.submit_publish()
        return {
            "title": title,
            "amount": amount,
            "submitted": True,
        }

    def get_publish_result_text(self) -> str:
        """读取发标提交后的页面文本（含成功/失败提示）。"""
        return self.publish_page.get_publish_result_text()
