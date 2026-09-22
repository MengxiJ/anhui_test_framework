# Copyright (C) 2026. All rights reserved.
"""投资列表页（/loan/tender/index）。

实测结构：

- 每页约 20 个标的卡片 ``.loan-item``：``a.tit``（title/text=标的名称）、
  「可投：20,000.00元」文本、「马上投标」按钮（``a.btn``，href 含
  ``/common/loan/loaninfoview#?id=<loan_id>``）；
- 筛选标签 ``li.ui-filter-tag``（信用标/天标/担保标）与排序标签（利率/金额/期限）。
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# 「可投：20,000.00元」
_AVAILABLE_RE = re.compile(r"可投[:：]?\s*([\d,\.]+)\s*元")
# loaninfoview#?id=2927
_LOAN_ID_RE = re.compile(r"[?&]id=(\d+)")

# 卡片解析 JS：一次遍历返回全部标的（避免逐元素往返）
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


class InvestListPage(BasePage):
    """投资列表页面对象。"""

    __list_url = BASE_URL + "/loan/tender/index"
    __filter_tag = (By.CSS_SELECTOR, "li.ui-filter-tag")
    __tender_button = (By.XPATH, '//a[contains(text(), "马上投标")]')

    def open_url(self) -> None:
        """打开投资列表页。"""
        self.driver.get(self.__list_url)

    def wait_loaded(self, timeout: float = 10.0) -> None:
        """等待列表卡片渲染完成（.loan-item 至少 1 个）。"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".loan-item")
        )

    def read_loan_cards(self) -> List[Dict[str, Any]]:
        """解析全部标的卡片（JS 一次遍历）。

        Returns:
            [{"loan_id": int|None, "name": str, "available_text": str,
              "available_amount": float|None, "tender_href": str, "can_tender": bool}]
        """
        raw = self.driver.execute_script(_PARSE_LOANS_JS) or []
        loans: List[Dict[str, Any]] = []
        for item in raw:
            text = str(item.get("text", ""))
            href = str(item.get("tender_href", ""))
            m = _AVAILABLE_RE.search(text)
            amount_text = m.group(1) if m else ""
            amount = None
            if amount_text:
                try:
                    amount = float(amount_text.replace(",", ""))
                except ValueError:
                    amount = None
            loan_id = None
            m2 = _LOAN_ID_RE.search(href)
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
        """读取筛选/排序标签文本列表。"""
        tags = self.driver.find_elements(*self.__filter_tag)
        return [t.text.strip() for t in tags if t.text.strip()]

    def click_filter_tag(self, tag_text: str, timeout: float = 8.0) -> bool:
        """点击指定文本的筛选标签（精确匹配优先，包含匹配兜底，匹配则 True）。"""
        deadline = time.time() + timeout
        target = "".join(str(tag_text).split())
        tags = []
        while time.time() < deadline:
            tags = [t for t in self.driver.find_elements(*self.__filter_tag) if t.is_displayed()]
            texts = ["".join((t.text or "").split()) for t in tags]
            if any(t == target or (target and target in t) for t in texts):
                break
            time.sleep(0.5)
        for tag in tags:
            text = "".join((tag.text or "").split())
            if text == target or (target and target in text):
                tag.click()
                time.sleep(1.5)  # AngularJS 重渲染
                return True
        return False

    def click_tender_button(self, index: int = 0) -> Optional[str]:
        """点击第 index 个可见「马上投标」按钮，返回其 href（无可用按钮返回 None）。"""
        WebDriverWait(self.driver, 10).until(
            lambda d: next(
                (e for e in d.find_elements(*self.__tender_button) if e.is_displayed()),
                None,
            )
        )
        buttons = [
            e for e in self.driver.find_elements(*self.__tender_button) if e.is_displayed()
        ]
        if not buttons or index >= len(buttons):
            return None
        href = buttons[index].get_attribute("href") or ""
        buttons[index].click()
        return href
