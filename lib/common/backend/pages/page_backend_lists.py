# -*- coding: utf-8 -*-
# Copyright (C) 2026. All rights reserved.
"""后台借款列表页面对象（帝友 dygrid 通用列表：初审标 / 满标待审 / 还款中等）。

列表页渲染在 #iframe_box 中；工具栏「审核」按钮打开 #xubox_iframe1 二级弹窗。
菜单结构（实测探测）：
借款管理 → {初审管理: [初审标 loan/verify/list, ...],
           满标管理: [满标待审 loan/full/list, 还款中 loan/fullpass/list, ...],
           借款中管理: [正在借款 loan/loaning/list, ...],
           借款列表: [所有借款 loan/loan/list, ...],
           额度管理: [额度列表 loan/amount/list, ...]}
"""
import time
from typing import Any, Dict

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage


class BackendListsPage(BasePage):
    """后台借款相关列表（搜索 / 读取 / 选中 / 审核弹窗）。"""

    __wait_short = 1.5
    __wait_load = 4

    __frame_box = (By.ID, "iframe_box")
    __frame_dialog = (By.CSS_SELECTOR, "#xubox_iframe1")

    __search_phone = (By.NAME, "userName")
    __search_title = (By.NAME, "name")
    __search_serial = (By.NAME, "serialNo")
    __search_member = (By.CSS_SELECTOR, "input[name='member_name'],input[name='memberName']")
    __search_btn = (By.CSS_SELECTOR, "li.srcbtn_box input.srcbtn")

    __top_navs = (By.CSS_SELECTOR, ".ace-nav-list a")

    __headers = (By.CSS_SELECTOR, "thead th.ui_th_column")
    __table = (By.CSS_SELECTOR, "table.ui_dygrid_htable")
    __rows = (By.CSS_SELECTOR, "tbody tr")
    __first_row = (By.XPATH, "//tbody/tr[1]")
    __audit_btn = (By.XPATH, '//a[contains(@ng-click,"editList")]/span[text()="审核"]')

    __dialog_radio = (By.CSS_SELECTOR, ".ace.ng-pristine")
    __dialog_radio_fallback = (By.CSS_SELECTOR, "input[type='radio']")
    __dialog_marker = (By.NAME, "marker_type")
    __dialog_note = (By.CSS_SELECTOR, "textarea")
    __dialog_img_code = (By.NAME, "valicode")
    __dialog_save = (By.CSS_SELECTOR, ".dybtn.dybtn-save")

    def __init__(self, driver):
        super().__init__(driver)
        self._active_top = "借款管理"

    def _ensure_top_menu(self, top_menu: str) -> None:
        """切换顶部一级菜单（借款管理 / 资金管理），相同则跳过避免重复点击。

        登录后首页 Angular 导航需要数秒渲染，轮询等待目标一级菜单出现。
        """
        if top_menu == self._active_top:
            return
        self.base_default_frame()
        nav = None
        for _ in range(20):
            for candidate in self.driver.find_elements(*self.__top_navs):
                if (candidate.text or "").strip() == top_menu:
                    nav = candidate
                    break
            if nav is not None:
                break
            time.sleep(0.5)
        if nav is None:
            raise RuntimeError(f"后台顶部一级菜单未找到: {top_menu}")
        self.driver.execute_script("arguments[0].click();", nav)
        time.sleep(self.__wait_load)
        self._active_top = top_menu

    # ---- 菜单导航 ----
    def open_group_item(self, group_text: str, item_rel: str,
                        top_menu: str = "借款管理") -> str:
        """展开指定分组并点击子菜单项（按 rel 定位，避免同名歧义）。

        top_menu 为顶部一级菜单（借款管理 / 资金管理），切换一级菜单后左侧
        手风琴整体重渲染。手风琴菜单在 iframe 导航后会短暂重绘，此时误点分组头
        会把 iframe_box 重置为默认仪表盘（/system/index/detect）。因此每次点击后
        轮询校验 iframe src 是否确实跳转到目标 rel，未跳转则重试；多次失败后
        直接将 iframe 指向目标 URL 兜底。成功后切入 iframe 并等待表格渲染。
        """
        self._ensure_top_menu(top_menu)
        last_src = ""
        for attempt in range(3):
            self.base_default_frame()
            item_loc = (By.XPATH, f'//a[@rel="{item_rel}"]')
            items = self.driver.find_elements(*item_loc)
            if items and items[0].is_displayed():
                self._js_click(item_loc)
            else:
                group_els = self.driver.find_elements(
                    By.XPATH, f'//span[text()="{group_text}"]')
                if group_els:
                    self.driver.execute_script("arguments[0].click();", group_els[0])
                time.sleep(self.__wait_short)
                self._js_click(item_loc)
            last_src = self._wait_iframe_src_contains(item_rel)
            if last_src:
                self.enter_list_frame()
                self._wait_table_ready()
                return last_src
        # 兜底：直接把列表 iframe 指向目标 URL（origin 取当前后台站点）
        origin = self.driver.execute_script("return location.origin")
        self.driver.execute_script(
            "document.getElementById('iframe_box').src = arguments[0];",
            f"{origin}/{item_rel}",
        )
        last_src = self._wait_iframe_src_contains(item_rel) or f"{origin}/{item_rel}"
        self.enter_list_frame()
        self._wait_table_ready()
        return last_src

    def _wait_iframe_src_contains(self, rel: str, timeout: float = 8.0) -> str:
        """轮询等待 iframe_box src 包含目标路径，命中则返回 src，超时返回空串。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.base_default_frame()
            src = self.driver.find_element(*self.__frame_box).get_attribute("src") or ""
            if rel in src and "system/index/detect" not in src:
                return src
            time.sleep(0.5)
        return ""

    def _wait_table_ready(self):
        """等待列表表格渲染完成（空表也渲染 table 元素）。"""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, self.default_timeout).until(
                EC.presence_of_element_located(self.__table)
            )
        except Exception:
            pass

    def _js_click(self, loc):
        elements = self.driver.find_elements(*loc)
        if not elements:
            raise RuntimeError(f"后台菜单元素未找到: {loc}")
        self.driver.execute_script("arguments[0].click();", elements[0])

    # ---- 列表读取（需已在 iframe_box 内） ----
    def enter_list_frame(self):
        """从默认内容切入列表 iframe。"""
        self.base_default_frame()
        self.base_switch_frame(self.__frame_box)

    def get_iframe_src(self) -> str:
        """读取当前 iframe src（默认内容下）。"""
        self.base_default_frame()
        return self.driver.find_element(*self.__frame_box).get_attribute("src") or ""

    def search_list(self, phone: str = "", title: str = "", serial_no: str = "",
                    member_keyword: str = ""):
        """按条件搜索当前列表（空条件跳过对应输入框）。

        member_keyword 用于资金管理类列表（账户/充值/提现/收支等），
        其搜索框为 member_name 或 memberName，与借款列表的 userName 不同。
        """
        if phone:
            self.base_input(self.__search_phone, phone)
        if title:
            self.base_input(self.__search_title, title)
        if serial_no:
            self.base_input(self.__search_serial, serial_no)
        if member_keyword:
            self.base_input(self.__search_member, member_keyword)
        self.base_click(self.__search_btn)
        time.sleep(self.__wait_short)

    def clear_search_inputs(self):
        """清空搜索条件（不清空下拉与日期）。"""
        for loc in (self.__search_phone, self.__search_title,
                    self.__search_serial, self.__search_member):
            elements = self.driver.find_elements(*loc)
            if elements:
                elements[0].clear()

    def read_headers(self):
        """读取表头文本列表。"""
        return [th.text.strip() for th in self.driver.find_elements(*self.__headers)]

    def get_row_count(self) -> int:
        """读取当前列表行数。"""
        return len(self.driver.find_elements(*self.__rows))

    def read_first_row(self):
        """读取首行数据：{loan_id, cells: {字段名: 文本}, texts: [单元格文本]}。"""
        rows = self.driver.find_elements(*self.__rows)
        if not rows:
            return {"loan_id": None, "cells": {}, "texts": [], "empty": True}
        cells = {}
        texts = []
        loan_id = None
        for td in rows[0].find_elements(By.TAG_NAME, "td"):
            cls = (td.get_attribute("class") or "").strip()
            text = (td.text or "").strip()
            if cls:
                cells[cls] = text
            texts.append(text)
            if loan_id is None:
                radios = td.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radios:
                    loan_id = radios[0].get_attribute("id")
        return {"loan_id": loan_id, "cells": cells, "texts": texts, "empty": False}

    def select_first_row(self):
        """选中首行（点击首行触发 radioBtn）。"""
        time.sleep(self.__wait_short)
        self.base_click(self.__first_row)

    # ---- 审核弹窗 ----
    def click_audit_button(self):
        """点击工具栏「审核」按钮，打开审核弹窗。"""
        self.base_click(self.__audit_btn)
        time.sleep(self.__wait_load)

    def submit_audit_dialog(self, note: str = "审核OK", img_code: str = "8888",
                            marker: str = "", decision: str = "pass") -> bool:
        """在审核弹窗中：选审核结论 → 填标签(初审必填) → 填备注 → 填验证码 → 保存。

        decision: pass=通过（初审 radio value=3 / 复审 value=1，取第一项）；
        reject=不通过（初审与复审 radio value 均为 -1）。
        初审弹窗存在必填「标签」(marker_type) 字段，缺失时前端校验拦截提交；
        满标复审弹窗无该字段。返回提交后弹窗是否已关闭（初审成功即关闭；
        满标复审因教学站接口缺陷滞留，作为提交是否生效的信号）。
        """
        self.base_switch_frame(self.__frame_dialog)
        if decision == "reject":
            self._click_radio_by_value("-1")
        else:
            self._click_pass_radio()
        if marker:
            self.base_input(self.__dialog_marker, marker)
        note_elements = self.driver.find_elements(*self.__dialog_note)
        if note_elements:
            note_elements[0].clear()
            note_elements[0].send_keys(note)
        self.base_input(self.__dialog_img_code, img_code)
        self.base_click(self.__dialog_save)
        time.sleep(self.__wait_load)
        return self.is_audit_dialog_closed()

    def is_audit_dialog_closed(self) -> bool:
        """检查审核弹窗是否已关闭（弹窗 iframe 位于列表 iframe 内）。"""
        self.base_default_frame()
        self.base_switch_frame(self.__frame_box)
        return not self.driver.find_elements(*self.__frame_dialog)

    def read_audit_dialog_form(self) -> Dict[str, Any]:
        """只读巡检审核弹窗表单（不提交）：审核结论 radio、备注、验证码、
        保存/取消按钮、标签字段是否存在。弹窗须已打开。"""
        self.base_switch_frame(self.__frame_dialog)
        radio_items = []
        for label in self.driver.find_elements(
                By.XPATH, "//label[input[@name='status' and @type='radio']]"):
            inputs = label.find_elements(
                By.CSS_SELECTOR, "input[name='status'][type='radio']")
            if inputs:
                radio_items.append({
                    "value": inputs[0].get_attribute("value") or "",
                    "text": (label.text or "").strip(),
                })
        note_els = self.driver.find_elements(*self.__dialog_note)
        code_els = self.driver.find_elements(*self.__dialog_img_code)
        marker_els = self.driver.find_elements(*self.__dialog_marker)
        save_els = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        cancel_els = self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']")
        return {
            "radios": radio_items,
            "radio_values": " ".join(r["value"] for r in radio_items),
            "radio_texts": " ".join(r["text"] for r in radio_items),
            "has_note": bool(note_els),
            "has_valicode": bool(code_els),
            "has_marker": bool(marker_els),
            "save_buttons": " ".join(
                (s.get_attribute("value") or "").strip() for s in save_els),
            "cancel_buttons": " ".join(
                (c.get_attribute("value") or "").strip() for c in cancel_els),
        }

    def close_audit_dialog(self) -> bool:
        """点击弹窗「取消」关闭（不保存任何数据），返回弹窗是否已关闭。"""
        # 读表单后 driver 可能已在弹窗 frame 内，先回顶层再经列表框架切入弹窗
        self.base_default_frame()
        self.base_switch_frame(self.__frame_box)
        self.base_switch_frame(self.__frame_dialog)
        cancel = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='button'][value='取消']")
        if not cancel:
            cancel = self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']")
        if not cancel:
            raise RuntimeError("审核弹窗未找到取消按钮")
        cancel[0].click()
        time.sleep(self.__wait_short)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            time.sleep(self.__wait_short)
        except Exception:  # noqa: BLE001 - 无确认弹窗属正常
            pass
        return self.is_audit_dialog_closed()

    def _click_pass_radio(self):
        """选择审核「通过」单选（优先 .ace 样式单选，回退原生 radio，JS 兜底）。"""
        for loc in (self.__dialog_radio, self.__dialog_radio_fallback):
            elements = self.driver.find_elements(*loc)
            if elements:
                try:
                    elements[0].click()
                    return
                except Exception:
                    self.driver.execute_script("arguments[0].click();", elements[0])
                    return
        raise RuntimeError("审核弹窗未找到「通过」单选按钮")

    def _click_radio_by_value(self, value: str):
        """按 value 精确选择审核结论单选（如 不通过 value=-1），JS 点击兜底。"""
        loc = (By.CSS_SELECTOR, f"input[name='status'][value='{value}']")
        elements = self.driver.find_elements(*loc)
        if not elements:
            elements = [
                r for r in self.driver.find_elements(*self.__dialog_radio_fallback)
                if (r.get_attribute("value") or "") == str(value)
            ]
        if not elements:
            raise RuntimeError(f"审核弹窗未找到 value={value} 的单选按钮")
        try:
            elements[0].click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", elements[0])
