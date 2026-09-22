# Copyright (C) 2026. All rights reserved.
"""标的详情页（/common/loan/loaninfoview#?id=xx）——窗口期交互设计。

实测站点行为：详情页在数据加载完成后（约 1~2 秒）会被站点 JS 重定向回投资列表
（headless / 有头、测评前后均复现，CDP 探测受环境限制无法进一步定位根因）。
因此本页全部读取/输入操作基于「窗口期」完成：

- 点击「马上投标」后立即轮询关键元素（``#tender_id`` 渲染出值 = 数据就绪）；
- 就绪后尽快读取详情上下文 / 输入金额 / 点击投标；
- 任何一步遇到 ``StaleElementReferenceException`` / URL 已回列表，视为站点拦截，
  返回明确状态由 check 做降级双态判定（reachable=严格 / redirected=降级）。

已探明元素：``#money``（name=tz-cash，ng-model=money，投资金额输入框）、
``#tender_id``（标的 id 隐藏域，渲染后有值）。

投标为**两段式确认交互**（2026-09-19 实测，此前因站点窗口期从未走通）：

1. 详情页右侧橙色 ``input[type=submit]``（``ng-click="tender_it(...)"``，文案
   「确认投标」）——点击后弹出 xubox 弹窗，内容是同源 iframe
   ``#xubox_iframe1``（``/loan/tender/investview#?id=xx&amount=xx``）；
2. 真正下单按钮在该 iframe 内：``#tender_new_submit``（蓝色「马上投标」），
   点击后成功路径无 JS alert，订单直接生成（「我的投资-投标中」可查）。
   必须 ``switch_to.frame`` 后再点击，主文档内无法命中该元素。
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from lib.core.page_base import BasePage

# 「最低投标金额:100.00元」「可投金额 20,000.00元」等上下文提取
_MIN_AMOUNT_RE = re.compile(r"最低投标金额[:：]?\s*([\d,\.]+)")
_AVAILABLE_RE = re.compile(r"可投金额[:：]?\s*([\d,\.]+)")
_BALANCE_RE = re.compile(r"可用余额[:：]?\s*([\d,\.]+)")


class LoanDetailPage(BasePage):
    """标的详情页面对象（窗口期交互）。"""

    __money_input = (By.ID, "money")
    __tender_id = (By.ID, "tender_id")
    # 第一段「确认投标」：优先真正带 ng-click=tender_it 的提交控件；
    # 早期候选里 //a[contains(text(),"投标")] 会误中隐藏导航锚点，已降权。
    __tender_outer_confirm = (
        By.CSS_SELECTOR,
        'input[type="submit"][ng-click*="tender_it"]',
    )
    __tender_submit_candidates = (
        (By.CSS_SELECTOR, "input.btnbgoragne"),
        (By.XPATH, '//input[@type="submit"]'),
        (By.XPATH, '//a[contains(text(), "立即投资")]'),
    )
    # 第二段：xubox 弹窗 iframe 与其中真正的下单按钮
    __confirm_iframe = (By.ID, "xubox_iframe1")
    __confirm_submit = (By.ID, "tender_new_submit")

    @staticmethod
    def is_detail_url(url: str) -> bool:
        """URL 是否为标的详情页。"""
        return "loaninfoview" in url

    def current_url(self) -> str:
        """读取当前 URL。"""
        return str(self.driver.current_url)

    def wait_detail_ready(self, nav_timeout: float = 8.0, ready_timeout: float = 6.0) -> bool:
        """等待导航进入详情页并等待数据就绪（``#tender_id`` 渲染出值）。

        阶段1（nav_timeout）：点击「马上投标」后等待 URL 进入详情页
        （eager 模式下导航也可能有延迟；超时说明未导航或已被重定向回列表）；
        阶段2（ready_timeout）：轮询 ``#tender_id`` 渲染出值——AngularJS 数据
        渲染慢于 DOMContentLoaded（实测 1~5s），而站点重定向发生在数据加载
        完成后 1~2 秒，因此「URL 仍在详情页」意味着重定向尚未发生，继续
        等待是安全的；一旦发现 URL 离开详情页立即返回 False。
        """
        nav_deadline = time.time() + nav_timeout
        while time.time() < nav_deadline:
            if self.is_detail_url(self.current_url()):
                break
            time.sleep(0.15)
        else:
            return False  # nav_timeout 内未到达详情页
        deadline = time.time() + ready_timeout
        while time.time() < deadline:
            if not self.is_detail_url(self.current_url()):
                return False
            try:
                ids = self.driver.find_elements(*self.__tender_id)
                if ids and (ids[0].get_attribute("value") or "").strip():
                    return True
            except Exception:  # noqa: BLE001 - 窗口期元素竞态，轮询重试
                pass
            time.sleep(0.15)
        return False

    def read_detail_info(self) -> Dict[str, Any]:
        """窗口期内读取详情信息（tender_id / 最低投标金额 / 可投金额 / 可用余额）。"""
        try:
            tid = self.driver.find_elements(*self.__tender_id)
            tender_id = (tid[0].get_attribute("value") if tid else "") or ""
        except Exception:  # noqa: BLE001
            tender_id = ""
        try:
            body = self.driver.execute_script(
                "return document.body ? document.body.textContent : '';"
            ) or ""
        except Exception:  # noqa: BLE001
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
            money_input_present = bool(self.driver.find_elements(*self.__money_input))
        except Exception:  # noqa: BLE001
            money_input_present = False
        return {
            "tender_id": tender_id,
            "min_amount": _num(_MIN_AMOUNT_RE),
            "available_amount": _num(_AVAILABLE_RE),
            "balance": _num(_BALANCE_RE),
            "money_input_present": money_input_present,
        }

    def input_amount(self, amount: Any) -> bool:
        """窗口期内向 ``#money`` 输入投资金额（成功 True；被拦截/元素失效 False）。"""
        try:
            if not self.is_detail_url(self.current_url()):
                return False
            WebDriverWait(self.driver, 1.5).until(
                lambda d: next(
                    (e for e in d.find_elements(*self.__money_input) if e.is_displayed()),
                    None,
                )
            )
            inputs = self.driver.find_elements(*self.__money_input)
            if not inputs:
                return False
            inputs[0].clear()
            inputs[0].send_keys(str(amount))
            return True
        except Exception:  # noqa: BLE001 - 窗口期竞态（跳页/元素失效）
            return False

    def click_tender_submit(self, modal_timeout: float = 8.0) -> Dict[str, Any]:
        """两段式投标提交（窗口期内执行）。

        1. 点击详情页右侧「确认投标」（``tender_it``），唤起 xubox iframe 弹窗；
        2. 切入 ``#xubox_iframe1`` 点击真正的下单按钮 ``#tender_new_submit``
           （「马上投标」），随后切回主文档。

        Returns:
            ``{"outer_clicked": 第一段是否点中,
               "confirm_modal": iframe 弹窗是否出现,
               "confirm_clicked": 第二段下单按钮是否点中}``
            站点窗口期拦截（URL 跳走）任一步为 False，由上层做降级判定。
        """
        status = {"outer_clicked": False, "confirm_modal": False, "confirm_clicked": False}
        try:
            if not self.is_detail_url(self.current_url()):
                return status
            # ---- 第一段：确认投标（优先精确的 tender_it 控件，失败再走候选）----
            outer = next(
                (
                    e
                    for e in self.driver.find_elements(*self.__tender_outer_confirm)
                    if e.is_displayed()
                ),
                None,
            )
            if outer is None:
                for by, value in self.__tender_submit_candidates:
                    try:
                        outer = next(
                            (e for e in self.driver.find_elements(by, value) if e.is_displayed()),
                            None,
                        )
                        if outer is not None:
                            break
                    except Exception:  # noqa: BLE001 - 候选逐个尝试
                        continue
            if outer is None:
                return status
            outer.click()
            status["outer_clicked"] = True

            # ---- 等待 xubox iframe 弹窗（窗口期跳走则提前放弃）----
            deadline = time.time() + modal_timeout
            iframe_el = None
            while time.time() < deadline:
                if not self.is_detail_url(self.current_url()):
                    return status
                frames = self.driver.find_elements(*self.__confirm_iframe)
                if frames and frames[0].is_displayed():
                    iframe_el = frames[0]
                    break
                time.sleep(0.2)
            if iframe_el is None:
                return status
            status["confirm_modal"] = True

            # ---- 第二段：iframe 内点「马上投标」----
            try:
                self.driver.switch_to.frame(iframe_el)
                inner_deadline = time.time() + modal_timeout
                while time.time() < inner_deadline:
                    buttons = self.driver.find_elements(*self.__confirm_submit)
                    visible = next((e for e in buttons if e.is_displayed()), None)
                    if visible is not None:
                        visible.click()
                        status["confirm_clicked"] = True
                        break
                    time.sleep(0.2)
            finally:
                # 无论成功与否必须切回主文档，避免后续页面操作上下文残留在 iframe
                self.driver.switch_to.default_content()
            return status
        except Exception:  # noqa: BLE001 - 窗口期竞态（跳页/元素失效/iframe 切换失败）
            try:
                self.driver.switch_to.default_content()
            except Exception:  # noqa: BLE001
                pass
            return status
