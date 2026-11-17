# Copyright (C) 2026. All rights reserved.
"""运营后台业务核心类（普通类，类内不做单例）。

处理后台登录、额度申请记录搜索、弹窗审核、借款列表（初审标 / 满标待审 / 还款中）
导航、搜索、读取与审核提交。
"""
from __future__ import annotations

import time
from typing import Any, Dict

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BACK_URL


class BackendManager(BasePage):
    """运营后台（登录 / 额度审核 / 借款列表审核）。"""

    # ---- 通用等待 ----
    _wait_short = 1.5
    _wait_load = 4
    _wait_time = 1  # LoanManagerPage 用

    # ---- 后台登录页（原 BackLoginPage） ----
    _back_url = BACK_URL
    _back_username = (By.ID, "username")
    _back_password = (By.ID, "password")
    _back_img_code = (By.ID, "valicode")
    _back_login_btn = (By.CLASS_NAME, "login-button")
    _back_success_text = (By.XPATH, "//div[text()='欢迎光临,']")
    _back_fail_text = (By.ID, "errorMessage")

    # ---- 额度审核页（原 LoanManagerPage） ----
    _loan = (By.LINK_TEXT, "借款管理")
    _limit = (By.XPATH, '//span[text()="额度管理"]')
    _app_review = (By.LINK_TEXT, "额度申请审核")
    _frame1 = (By.ID, "iframe_box")
    _loan_username = (By.NAME, "member_name")
    _loan_search_btn = (By.CSS_SELECTOR, '[value="搜索"]')
    _loan_record = (By.XPATH, "//tbody/tr[1]/td[2]/span")
    _approve = (By.XPATH, '//span[text()="审核"]')
    _frame2 = (By.CSS_SELECTOR, "#xubox_iframe1")
    _loan_radio = (By.CSS_SELECTOR, ".ace.ng-pristine.ng-untouched.ng-valid")
    _loan_note = (By.CSS_SELECTOR, "tr:nth-child(6) > td:nth-child(2) > div > textarea")
    _loan_img_code = (By.NAME, "valicode")
    _loan_save = (By.CSS_SELECTOR, ".dybtn.dybtn-save")
    _app_rec = (By.LINK_TEXT, "额度申请记录")
    _app_status = (By.CSS_SELECTOR, "select[name='status']")
    _loan_success_text = (By.XPATH, "//tbody/tr[1]/td[7]/span")
    _loan_fail_text = (By.XPATH, "//*[@id='xubox_layer1']/div[1]/div/em")

    # ---- 借款列表页（原 BackendListsPage） ----
    _frame_box = (By.ID, "iframe_box")
    _frame_dialog = (By.CSS_SELECTOR, "#xubox_iframe1")

    _search_phone = (By.NAME, "userName")
    _search_title = (By.NAME, "name")
    _search_serial = (By.NAME, "serialNo")
    _search_member = (By.CSS_SELECTOR, "input[name='member_name'],input[name='memberName']")
    _search_btn = (By.CSS_SELECTOR, "li.srcbtn_box input.srcbtn")

    _top_navs = (By.CSS_SELECTOR, ".ace-nav-list a")

    _headers = (By.CSS_SELECTOR, "thead th.ui_th_column")
    _table = (By.CSS_SELECTOR, "table.ui_dygrid_htable")
    _rows = (By.CSS_SELECTOR, "tbody tr")
    _first_row = (By.XPATH, "//tbody/tr[1]")
    _audit_btn = (By.XPATH, '//a[contains(@ng-click,"editList")]/span[text()="审核"]')

    _dialog_radio = (By.CSS_SELECTOR, ".ace.ng-pristine")
    _dialog_radio_fallback = (By.CSS_SELECTOR, "input[type='radio']")
    _dialog_marker = (By.NAME, "marker_type")
    _dialog_note = (By.CSS_SELECTOR, "textarea")
    _dialog_img_code = (By.NAME, "valicode")
    _dialog_save = (By.CSS_SELECTOR, ".dybtn.dybtn-save")

    def __init__(self, driver) -> None:
        super().__init__(driver)
        self._active_top = "借款管理"

    # ============ 后台登录 ============
    def open_back_url(self) -> None:
        self.driver.get(self._back_url)

    def input_username(self, username: str) -> None:
        self.base_input(self._back_username, username)

    def input_password(self, password: str) -> None:
        self.base_input(self._back_password, password)

    def input_img_code(self, img_code: str = "8888") -> None:
        self.base_input(self._back_img_code, img_code)

    def click_login_btn(self) -> None:
        self.base_click(self._back_login_btn)

    def get_result_success_text(self) -> str:
        return self.fd_element(self._back_success_text).text

    def get_result_fail_text(self) -> str:
        return self.fd_element(self._back_fail_text).text

    def back_login(self, username: str, password: str, img_code: str = "8888") -> None:
        self.input_username(username)
        self.input_password(password)
        self.input_img_code(img_code)
        self.click_login_btn()

    # 对外高层接口
    def open_back_login_page(self) -> None:
        self.open_back_url()

    def get_back_login_result_text(self) -> str:
        return self.get_result_success_text()

    # ============ 额度审核 ============
    def click_menu_manage(self) -> None:
        self.base_click(self._loan)
        self.base_click(self._limit)
        self.base_click(self._app_review)

    def search_record(self, phone: str) -> None:
        self.base_switch_frame(self._frame1)
        self.base_input(self._loan_username, phone)
        self.base_click(self._loan_search_btn)

    def click_record(self) -> None:
        time.sleep(self._wait_time)
        self.base_click(self._loan_record)
        self.base_click(self._approve)

    def approve_loan(self, note: str = "审核OK", img_code: str = "8888") -> None:
        self.base_switch_frame(self._frame2)
        self.base_click_special(self._loan_radio)
        self.base_input(self._loan_note, note)
        self.base_input(self._loan_img_code, img_code)
        self.base_click(self._loan_save)

    def click_app_rec(self, phone: str, status: str = "通过") -> None:
        self.base_default_frame()
        self.base_click(self._app_rec)
        self.base_switch_frame(self._frame1)
        self.base_input(self._loan_username, phone)
        self.base_select_list(self._app_status, status)
        self.base_click(self._loan_search_btn)

    def get_loan_result_success_text(self) -> str:
        time.sleep(self._wait_time)
        return self.fd_element(self._loan_success_text).text

    def get_loan_result_fail_text(self) -> str:
        time.sleep(self._wait_time)
        self.base_switch_frame(self._frame2)
        return self.fd_element(self._loan_fail_text).text

    def credit_application_review(self, phone: str, note: str = "审核OK", img_code: str = "8888") -> None:
        self.click_menu_manage()
        self.search_record(phone)
        self.click_record()
        self.approve_loan(note, img_code)

    # 对外高层接口
    def open_review_menu(self) -> None:
        self.click_menu_manage()

    def search_loan_record(self, phone: str) -> None:
        self.search_record(phone)

    def click_record_and_audit(self) -> None:
        self.click_record()

    def review_credit_application(self, phone: str, note: str = "审核OK", img_code: str = "8888") -> None:
        self.credit_application_review(phone, note, img_code)

    def query_application_record(self, phone: str, status: str = "通过") -> None:
        self.click_app_rec(phone, status)

    def get_review_result_text(self) -> str:
        return self.get_loan_result_success_text()

    # ============ 借款列表导航 ============
    def _ensure_top_menu(self, top_menu: str) -> None:
        if top_menu == self._active_top:
            return
        self.base_default_frame()
        clicked = False
        for _ in range(20):
            try:
                for candidate in self.driver.find_elements(*self._top_navs):
                    if (candidate.text or "").strip() == top_menu:
                        self.driver.execute_script("arguments[0].click();", candidate)
                        clicked = True
                        break
            except StaleElementReferenceException:
                pass
            if clicked:
                break
            time.sleep(0.5)
        if not clicked:
            raise RuntimeError(f"后台顶部一级菜单未找到: {top_menu}")
        time.sleep(self._wait_load)
        self._active_top = top_menu

    def open_group_item(self, group_text: str, item_rel: str,
                        top_menu: str = "借款管理") -> str:
        self._ensure_top_menu(top_menu)
        last_src = ""
        for attempt in range(3):
            self.base_default_frame()
            try:
                item_loc = (By.XPATH, f'//a[@rel="{item_rel}"]')
                items = self.driver.find_elements(*item_loc)
                if items and items[0].is_displayed():
                    self._js_click(item_loc)
                else:
                    group_els = self.driver.find_elements(
                        By.XPATH, f'//span[text()="{group_text}"]')
                    if group_els:
                        self.driver.execute_script("arguments[0].click();", group_els[0])
                    time.sleep(self._wait_short)
                    self._js_click(item_loc)
            except StaleElementReferenceException:
                time.sleep(self._wait_load)
                continue
            last_src = self._wait_iframe_src_contains(item_rel)
            if last_src:
                self.enter_list_frame()
                self._wait_table_ready()
                return last_src
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
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.base_default_frame()
            src = self.driver.find_element(*self._frame_box).get_attribute("src") or ""
            if rel in src and "system/index/detect" not in src:
                return src
            time.sleep(0.5)
        return ""

    def _wait_table_ready(self):
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait
        try:
            WebDriverWait(self.driver, self.default_timeout).until(
                EC.presence_of_element_located(self._table)
            )
        except Exception:
            pass

    def _js_click(self, loc):
        for _ in range(3):
            elements = self.driver.find_elements(*loc)
            if not elements:
                raise RuntimeError(f"后台菜单元素未找到: {loc}")
            try:
                self.driver.execute_script("arguments[0].click();", elements[0])
                return
            except StaleElementReferenceException:
                time.sleep(self._wait_short)
        raise RuntimeError(f"后台菜单元素重渲染后仍不可点击: {loc}")

    # ============ 列表读取（需已在 iframe_box 内） ============
    def enter_list_frame(self):
        self.base_default_frame()
        self.base_switch_frame(self._frame_box)

    def get_iframe_src(self) -> str:
        self.base_default_frame()
        return self.driver.find_element(*self._frame_box).get_attribute("src") or ""

    def search_list(self, phone: str = "", title: str = "", serial_no: str = "",
                    member_keyword: str = ""):
        if phone:
            self.base_input(self._search_phone, phone)
        if title:
            self.base_input(self._search_title, title)
        if serial_no:
            self.base_input(self._search_serial, serial_no)
        if member_keyword:
            self.base_input(self._search_member, member_keyword)
        self.base_click(self._search_btn)
        time.sleep(self._wait_short)

    def clear_search_inputs(self):
        for loc in (self._search_phone, self._search_title,
                    self._search_serial, self._search_member):
            elements = self.driver.find_elements(*loc)
            if elements:
                elements[0].clear()

    def read_headers(self):
        return [th.text.strip() for th in self.driver.find_elements(*self._headers)]

    def get_row_count(self) -> int:
        return len(self.driver.find_elements(*self._rows))

    def read_first_row(self):
        rows = self.driver.find_elements(*self._rows)
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
        time.sleep(self._wait_short)
        self.base_click(self._first_row)

    # ============ 审核弹窗 ============
    def click_audit_button(self):
        self.base_click(self._audit_btn)
        time.sleep(self._wait_load)

    def submit_audit_dialog(self, note: str = "审核OK", img_code: str = "8888",
                            marker: str = "", decision: str = "pass") -> bool:
        self.base_switch_frame(self._frame_dialog)
        if decision == "reject":
            self._click_radio_by_value("-1")
        else:
            self._click_pass_radio()
        if marker:
            self.base_input(self._dialog_marker, marker)
        note_elements = self.driver.find_elements(*self._dialog_note)
        if note_elements:
            note_elements[0].clear()
            note_elements[0].send_keys(note)
        self.base_input(self._dialog_img_code, img_code)
        self.base_click(self._dialog_save)
        time.sleep(self._wait_load)
        return self.is_audit_dialog_closed()

    def is_audit_dialog_closed(self) -> bool:
        self.base_default_frame()
        self.base_switch_frame(self._frame_box)
        return not self.driver.find_elements(*self._frame_dialog)

    def read_audit_dialog_form(self) -> Dict[str, Any]:
        self.base_switch_frame(self._frame_dialog)
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
        note_els = self.driver.find_elements(*self._dialog_note)
        code_els = self.driver.find_elements(*self._dialog_img_code)
        marker_els = self.driver.find_elements(*self._dialog_marker)
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
        self.base_default_frame()
        self.base_switch_frame(self._frame_box)
        self.base_switch_frame(self._frame_dialog)
        cancel = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='button'][value='取消']")
        if not cancel:
            cancel = self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']")
        if not cancel:
            raise RuntimeError("审核弹窗未找到取消按钮")
        cancel[0].click()
        time.sleep(self._wait_short)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            time.sleep(self._wait_short)
        except Exception:
            pass
        return self.is_audit_dialog_closed()

    def _click_pass_radio(self):
        for loc in (self._dialog_radio, self._dialog_radio_fallback):
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
        loc = (By.CSS_SELECTOR, f"input[name='status'][value='{value}']")
        elements = self.driver.find_elements(*loc)
        if not elements:
            elements = [
                r for r in self.driver.find_elements(*self._dialog_radio_fallback)
                if (r.get_attribute("value") or "") == str(value)
            ]
        if not elements:
            raise RuntimeError(f"审核弹窗未找到 value={value} 的单选按钮")
        try:
            elements[0].click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", elements[0])

    # ============ 对外高层接口（借款列表） ============
    def open_loan_group_item(self, group_text: str, item_rel: str,
                             top_menu: str = "借款管理") -> str:
        return self.open_group_item(group_text, item_rel, top_menu=top_menu)

    def search_current_loan_list(self, phone: str = "", title: str = "",
                                 serial_no: str = "", member_keyword: str = "") -> None:
        self.search_list(phone=phone, title=title, serial_no=serial_no,
                         member_keyword=member_keyword)

    def clear_loan_list_search(self) -> None:
        self.clear_search_inputs()

    def get_current_loan_list_info(self) -> Dict[str, Any]:
        info = {"src": self.get_iframe_src()}
        self.enter_list_frame()
        info["headers"] = self.read_headers()
        info["row_count"] = self.get_row_count()
        info["first_row"] = self.read_first_row()
        info["headers_text"] = " ".join(info["headers"])
        first = info["first_row"]
        info["first_loan_id"] = first.get("loan_id")
        info["first_serialno"] = first.get("cells", {}).get("serialno", "")
        first_member = first.get("cells", {}).get("member_name", "")
        if not first_member and len(first.get("texts", [])) > 1:
            first_member = first["texts"][1]
        info["first_member"] = first_member
        info["first_title"] = first.get("cells", {}).get("name", "")
        info["first_amount"] = first.get("cells", {}).get("amount", "")
        return info

    def review_first_loan_in_list(
        self,
        group_text: str,
        item_rel: str,
        phone: str = "",
        title: str = "",
        serial_no: str = "",
        note: str = "审核OK",
        img_code: str = "8888",
        marker: str = "",
        top_menu: str = "借款管理",
        decision: str = "pass",
    ) -> Dict[str, Any]:
        self.open_group_item(group_text, item_rel, top_menu=top_menu)
        self.search_list(phone=phone, title=title, serial_no=serial_no)
        row_count = self.get_row_count()
        if row_count < 1:
            return {"found": False, "row_count": 0, "src": self.get_iframe_src()}
        first_row = self.read_first_row()
        self.select_first_row()
        self.click_audit_button()
        dialog_closed = self.submit_audit_dialog(
            note=note, img_code=img_code, marker=marker, decision=decision)
        return {
            "found": True,
            "row_count": row_count,
            "loan_id": first_row.get("loan_id"),
            "serialno": first_row.get("cells", {}).get("serialno", ""),
            "member": first_row.get("cells", {}).get("member_name", ""),
            "title": first_row.get("cells", {}).get("name", ""),
            "amount": first_row.get("cells", {}).get("amount", ""),
            "dialog_closed": dialog_closed,
            "src": self.get_iframe_src(),
        }

    def inspect_audit_dialog(self) -> Dict[str, Any]:
        before = self.get_row_count()
        if before < 1:
            return {"found": False, "before_row_count": 0,
                    "after_row_count": 0, "dialog_closed": None}
        self.select_first_row()
        self.click_audit_button()
        form = self.read_audit_dialog_form()
        dialog_closed = self.close_audit_dialog()
        self.enter_list_frame()
        self._wait_table_ready()
        after = self.get_row_count()
        return {
            "found": True,
            "before_row_count": before,
            "after_row_count": after,
            "dialog_closed": dialog_closed,
            **form,
        }

    def requery_loan_list_count(
        self,
        group_text: str,
        item_rel: str,
        phone: str = "",
        title: str = "",
        serial_no: str = "",
        top_menu: str = "借款管理",
        member_keyword: str = "",
    ) -> Dict[str, Any]:
        self.open_group_item(group_text, item_rel, top_menu=top_menu)
        self.search_list(
            phone=phone, title=title, serial_no=serial_no, member_keyword=member_keyword)
        info = self.get_current_loan_list_info()
        return {
            "row_count": info["row_count"],
            "first_serialno": info["first_serialno"],
            "first_title": info["first_title"],
            "first_member": info["first_member"],
            "src": info["src"],
        }
