# Copyright (C) 2026. All rights reserved.
"""提醒设置页（/member/remind/setremind）。

实测结构：

- 贷款者 / 投资者两组提醒，每组含 ``phone_notice`` 与多组
  ``message[]`` / ``email[]`` 复选框（id=message_1..17 / email_1..17）；
- 提交按钮文本「确认提交」（input[type=submit] 或按钮/a 标签均兼容）；
- 提交后可能弹原生 alert，本页统一接受并回填结果文本。
"""
from __future__ import annotations

import time
from typing import Dict, List

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# 提醒复选框（id 形如 message_1 / email_1，另有 phone_notice）
_CHECKBOX_CSS = 'input[type="checkbox"]'
# 提交按钮候选
_SUBMIT_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "确认提交")]'),
    (By.XPATH, '//input[contains(@value, "提 交")]'),
    (By.XPATH, '//input[@type="submit"]'),
    (By.XPATH, '//button[contains(text(), "确认提交")]'),
    (By.XPATH, '//button[contains(text(), "提交")]'),
    (By.XPATH, '//a[contains(text(), "确认提交")]'),
    (By.XPATH, '//a[contains(text(), "提交")]'),
)


class RemindPage(BasePage):
    """提醒设置页面对象。"""

    __remind_url = BASE_URL + "/member/remind/setremind"

    def open_url(self) -> None:
        """打开提醒设置页。"""
        self.driver.get(self.__remind_url)

    # ---- 读取 ----
    def read_checkbox_state(self, checkbox_id: str) -> bool:
        """读取单个复选框选中状态（元素不存在按未选中处理）。"""
        elements = self.driver.find_elements(By.ID, checkbox_id)
        if not elements:
            # 退而求其次：按 name 匹配（如 message[] 无法按 id 命中时）
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, f'input[type="checkbox"][name="{checkbox_id}"]'
            )
        if not elements:
            return False
        return bool(elements[0].is_selected())

    def read_all_states(self) -> Dict[str, bool]:
        """读取页面全部提醒复选框状态（id -> 是否选中；无 id 的用 name）。"""
        states: Dict[str, bool] = {}
        boxes = self.driver.find_elements(By.CSS_SELECTOR, _CHECKBOX_CSS)
        for box in boxes:
            key = (box.get_attribute("id") or box.get_attribute("name") or "").strip()
            if key:
                states[key] = bool(box.is_selected())
        return states

    # ---- 切换与提交 ----
    def toggle_checkbox(self, checkbox_id: str) -> bool:
        """切换指定复选框状态，返回切换前状态（元素不存在抛 ValueError）。"""
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

    def click_submit(self) -> bool:
        """点击「确认提交」并接受可能弹出的 alert（找不到按钮返回 False）。"""
        for by, value in _SUBMIT_CANDIDATES:
            try:
                visible = next(
                    (e for e in self.driver.find_elements(by, value) if e.is_displayed()),
                    None,
                )
                if visible:
                    visible.click()
                    self._accept_alert_if_present()
                    return True
            except Exception:  # noqa: BLE001 - 候选逐个尝试
                continue
        return False

    def read_submit_result(self) -> str:
        """读取提交后的提示（alert 文本优先，其次页面提示行）。"""
        alert_text = self._accept_alert_if_present()
        if alert_text:
            return alert_text
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:  # noqa: BLE001
            return ""
        for line in body.splitlines():
            line = line.strip()
            if line and len(line) <= 40 and ("成功" in line or "失败" in line):
                return line
        return ""

    def _accept_alert_if_present(self, timeout: float = 2.0) -> str:
        """读取并关闭可能弹出的 alert（无 alert 返回空串）。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                alert = self.driver.switch_to.alert
                text = (alert.text or "").strip()
                alert.accept()
                return text
            except Exception:  # noqa: BLE001 - alert 未弹出
                time.sleep(0.3)
        return ""
