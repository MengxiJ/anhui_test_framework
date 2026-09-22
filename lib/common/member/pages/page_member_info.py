# Copyright (C) 2026. All rights reserved.
"""个人基础信息页（/member/info/index）。

实测结构：

- 页面有「个人信息/企业信息」两个子 tab（/member/info/index 与 /member/info/job），
  h2 标题「个人基础信息」；
- 表单字段：select name=educationalBackground（学历）、input name=graduated（毕业院校）、
  select name=marryStatus（婚姻状况，可逆编辑字段）、select name=companyIndustry/
  companyScale/companyOffice/monthlyIncome、select name=hometownProvince/hometownCity/
  hometownArea、input id=address（通讯地址）；
- 编辑按钮为 input[type=button]（value 含「编」，实际文本「编  辑」带空格）；
  编辑交互存在「select 已可直接操作」与「需先点编辑」两种形态，本页两种都兼容；
- 保存按钮在编辑态出现（候选：input[type=submit] 或含「保存/确认/提交」文本的按钮）。
"""
from __future__ import annotations

import time
from typing import Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# 全部已知资料字段（select 按 name 定位）
_PROFILE_SELECT_FIELDS = (
    "educationalBackground",
    "marryStatus",
    "companyIndustry",
    "companyScale",
    "companyOffice",
    "monthlyIncome",
    "hometownProvince",
    "hometownCity",
    "hometownArea",
)
# 全部已知资料字段（input 按 name/id 定位）
_PROFILE_INPUT_FIELDS = ("graduated", "address")

# 编辑按钮候选（value/文本含「编」）
_EDIT_BUTTON_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "编")]'),
    (By.XPATH, '//button[contains(text(), "编")]'),
)
# 保存按钮候选（编辑态出现）
_SAVE_BUTTON_CANDIDATES = (
    (By.XPATH, '//input[contains(@value, "保存")]'),
    (By.XPATH, '//input[contains(@value, "确认")]'),
    (By.XPATH, '//input[contains(@value, "提交")]'),
    (By.XPATH, '//button[contains(text(), "保存")]'),
    (By.XPATH, '//button[contains(text(), "确认")]'),
    (By.XPATH, '//button[contains(text(), "提交")]'),
    (By.CSS_SELECTOR, "input[type=submit]"),
)
# 保存结果文本线索关键词
_SAVE_RESULT_KEYWORDS = ("成功", "失败", "保存", "修改")


class MemberInfoPage(BasePage):
    """个人基础信息页面对象。"""

    __info_url = BASE_URL + "/member/info/index"

    def open_url(self) -> None:
        """打开个人基础信息页（个人信息 tab）。"""
        self.driver.get(self.__info_url)

    # ---- 读取 ----
    def read_profile_field(self, field_name: str, timeout: float = 8.0) -> str:
        """读取单个资料字段当前值（select 取选中项文本，input 取 value）。

        AngularJS 的 ng-options 渲染与 model 回填存在窗口期：渲染完成前
        select 的选中项恒为占位「请选择」。因此 select 字段需轮询等待
        选项渲染且选中值稳定；字段本身确实未选（一直占位）时超时返回当前值。
        """
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
                except Exception:  # noqa: BLE001 - 选项尚未渲染
                    options = []
                    text = ""
                if len(options) > 1 and text and text != "请选择":
                    return text
                if time.time() >= deadline:
                    return text  # 可能确实未选择（占位态）
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
        """读取全部资料字段当前值（元素不存在的字段返回空串）。"""
        profile: Dict[str, str] = {}
        for field in _PROFILE_SELECT_FIELDS:
            profile[field] = self.read_profile_field(field)
        for field in _PROFILE_INPUT_FIELDS:
            profile[field] = self.read_profile_field(field)
        return profile

    # ---- 编辑与保存 ----
    def click_edit(self) -> bool:
        """点击「编辑」按钮进入编辑态（找不到按钮返回 False，不报错）。"""
        return self._click_first_visible(_EDIT_BUTTON_CANDIDATES)

    def edit_profile_field(self, field_name: str, value: str) -> bool:
        """修改单个资料字段（字段处于 dy-disabled 态时先点「编辑」并等待可操作）。

        实测 AngularJS 表单 basicForm 的 select 默认带 ``dy-disabled``，
        必须先触发 ``formClick.edit()``；编辑按钮是开关型，不可重复点击，
        故只在字段确实禁用时点一次，并轮询等待字段 enable 后再改值。
        """
        if self._is_field_disabled(field_name):
            self.click_edit()
            self._wait_field_enabled(field_name)
        return self._do_edit_field(field_name, value)

    def _is_field_disabled(self, field_name: str) -> bool:
        """字段当前是否处于禁用态（元素缺失视为非禁用，交给后续操作判错）。"""
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            f'select[name="{field_name}"],input[name="{field_name}"],input#{field_name}',
        )
        if not elements:
            return False
        return not elements[0].is_enabled()

    def _wait_field_enabled(self, field_name: str, timeout: float = 6.0) -> bool:
        """轮询等待字段进入可编辑态。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self._is_field_disabled(field_name):
                # select 还需等待 ng-options 渲染出可选项
                selects = self.driver.find_elements(
                    By.CSS_SELECTOR, f'select[name="{field_name}"]'
                )
                if not selects or len(Select(selects[0]).options) > 1:
                    return True
            time.sleep(0.3)
        return False

    def click_save(self, wait_field: str = "marryStatus", timeout: float = 8.0) -> bool:
        """点击保存按钮并等待保存生效。

        判定生效的信号（先到先得）：原生 alert 弹出 / 表单退回禁用态
        （dy-disabled 重新挂回）/ 出现成功类提示。超时不判失败（业务结果
        由调用方回读核对），但保证不抢跑。
        """
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
        """读取保存后的页面文本线索（alert 文本或页面提示行，无线索返回空串）。"""
        alert_text = self._accept_alert_if_present()
        if alert_text:
            return alert_text
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:  # noqa: BLE001
            return ""
        for line in (body or "").splitlines():
            line = line.strip()
            if line and len(line) <= 40 and any(kw in line for kw in _SAVE_RESULT_KEYWORDS):
                return line
        return ""

    # ---- 内部工具 ----
    def _do_edit_field(self, field_name: str, value: str) -> bool:
        """直接操作字段元素（select 按可见文本选择，input 清空后输入）。"""
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
        """下拉选择（先精确匹配可见文本，失败后回退包含匹配）。"""
        select = Select(element)
        try:
            select.select_by_visible_text(value)
        except Exception:  # noqa: BLE001 - 选项文本可能带空格，回退包含匹配
            for option in select.options:
                if value and value in (option.text or "").strip():
                    select.select_by_visible_text(option.text)
                    return
            raise

    def _click_first_visible(self, candidates) -> bool:
        """按候选定位器依次尝试点击第一个可见元素。"""
        for by, value in candidates:
            try:
                elements = self.driver.find_elements(by, value)
                visible = next((e for e in elements if e.is_displayed()), None)
                if visible:
                    visible.click()
                    return True
            except Exception:  # noqa: BLE001 - 候选逐个尝试
                continue
        return False

    def _accept_alert_if_present(self, timeout: float = 2.0) -> str:
        """读取并关闭可能弹出的 alert（无 alert 返回空串）。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                alert = self.driver.switch_to.alert
                text = (alert.text or "").strip()
                alert.accept()
                return text
            except Exception:  # noqa: BLE001 - alert 未弹出，稍后重试
                time.sleep(0.3)
        return ""
