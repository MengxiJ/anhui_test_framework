# Copyright (C) 2026. All rights reserved.
"""运营后台业务核心类（普通类，类内不做单例）。

组合 ``BackLoginPage`` / ``LoanManagerPage`` / ``BackendListsPage``，处理后台登录、
额度申请记录搜索、弹窗审核、借款列表（初审标 / 满标待审 / 还款中）导航、
搜索、读取与审核提交。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.backend.pages import BackLoginPage, BackendListsPage, LoanManagerPage


class BackendManager:
    """运营后台（登录 / 额度审核 / 借款列表审核）。"""

    def __init__(self, driver) -> None:
        self.driver = driver
        self._back_login_page: Optional[BackLoginPage] = None
        self._loan_page: Optional[LoanManagerPage] = None
        self._lists_page: Optional[BackendListsPage] = None

    @property
    def back_login_page(self) -> BackLoginPage:
        if self._back_login_page is None:
            self._back_login_page = BackLoginPage(self.driver)
        return self._back_login_page

    @property
    def loan_page(self) -> LoanManagerPage:
        if self._loan_page is None:
            self._loan_page = LoanManagerPage(self.driver)
        return self._loan_page

    @property
    def lists_page(self) -> BackendListsPage:
        if self._lists_page is None:
            self._lists_page = BackendListsPage(self.driver)
        return self._lists_page

    # ---- 后台登录 ----
    def open_back_login_page(self) -> None:
        self.back_login_page.open_back_url()

    def back_login(self, username: str, password: str, img_code: str = "8888") -> None:
        self.back_login_page.back_login(username, password, img_code)

    def get_back_login_result_text(self) -> str:
        return self.back_login_page.get_result_success_text()

    # ---- 额度审核 ----
    def open_review_menu(self) -> None:
        """进入 借款管理 → 额度管理 → 额度申请审核。"""
        self.loan_page.click_menu_manage()

    def search_loan_record(self, phone: str) -> None:
        """在 iframe 中按手机号搜索额度申请记录。"""
        self.loan_page.search_record(phone)

    def click_record_and_audit(self) -> None:
        """选中首条记录并打开审核弹窗。"""
        self.loan_page.click_record()

    def approve_loan(self, note: str = "审核OK", img_code: str = "8888") -> None:
        """在审核弹窗中选择通过、填写备注与验证码并保存。"""
        self.loan_page.approve_loan(note, img_code)

    def review_credit_application(self, phone: str, note: str = "审核OK", img_code: str = "8888") -> None:
        """额度申请审核完整流程（菜单 → 搜索 → 弹窗 → 提交）。"""
        self.loan_page.credit_application_review(phone, note, img_code)

    def query_application_record(self, phone: str, status: str = "通过") -> None:
        """查询额度申请记录（按状态筛选）。"""
        self.loan_page.click_app_rec(phone, status)

    def get_review_result_text(self) -> str:
        """读取审核记录列表中的审核状态文本。"""
        return self.loan_page.get_result_success_text()

    # ---- 借款列表（初审标 / 满标待审 / 还款中 / 资金管理各列表） ----
    def open_loan_group_item(self, group_text: str, item_rel: str,
                             top_menu: str = "借款管理") -> str:
        """展开分组并进入列表页，返回 iframe src（含 rel 路径）。"""
        return self.lists_page.open_group_item(group_text, item_rel, top_menu=top_menu)

    def search_current_loan_list(self, phone: str = "", title: str = "",
                                 serial_no: str = "", member_keyword: str = "") -> None:
        """在当前列表中按条件搜索（需先进入列表页）。"""
        self.lists_page.search_list(
            phone=phone, title=title, serial_no=serial_no, member_keyword=member_keyword)

    def clear_loan_list_search(self) -> None:
        """清空当前列表的搜索条件。"""
        self.lists_page.clear_search_inputs()

    def get_current_loan_list_info(self) -> Dict[str, Any]:
        """读取当前列表信息：src / 表头 / 行数 / 首行（读 src 后重新切入列表框架）。"""
        info = {"src": self.lists_page.get_iframe_src()}
        self.lists_page.enter_list_frame()
        info["headers"] = self.lists_page.read_headers()
        info["row_count"] = self.lists_page.get_row_count()
        info["first_row"] = self.lists_page.read_first_row()
        info["headers_text"] = " ".join(info["headers"])
        first = info["first_row"]
        info["first_loan_id"] = first.get("loan_id")
        info["first_serialno"] = first.get("cells", {}).get("serialno", "")
        # 资金类列表（账户/充值/收支等）用户名 td class 可能不是 member_name，
        # 取第二列文本（第一列为 ID）兜底
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
        """进入指定列表 → 搜索 → 读首行 → 选中 → 审核弹窗 → 提交审核结论。

        marker 为初审必填「标签」字段（满标复审弹窗无该字段，留空跳过）。
        decision=pass 提交通过，reject 提交「不通过」（radio value=-1）。
        返回 found 及首行信息，dialog_closed 表示提交后弹窗是否关闭
        （初审成功即关闭；满标复审因教学站接口缺陷滞留不关）。
        """
        self.lists_page.open_group_item(group_text, item_rel, top_menu=top_menu)
        self.lists_page.search_list(phone=phone, title=title, serial_no=serial_no)
        row_count = self.lists_page.get_row_count()
        if row_count < 1:
            return {"found": False, "row_count": 0, "src": self.lists_page.get_iframe_src()}
        first_row = self.lists_page.read_first_row()
        self.lists_page.select_first_row()
        self.lists_page.click_audit_button()
        dialog_closed = self.lists_page.submit_audit_dialog(
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
            "src": self.lists_page.get_iframe_src(),
        }

    def inspect_audit_dialog(self) -> Dict[str, Any]:
        """当前列表选中首行 → 打开审核弹窗 → 只读表单字段 → 点取消关闭（不提交）。

        用于充值/提现审核等不得产生数据变更的弹窗巡检。返回弹窗表单结构、
        弹窗是否成功关闭、关闭前后列表行数（核对数据无变化）。须已进入目标列表。
        """
        before = self.lists_page.get_row_count()
        if before < 1:
            return {"found": False, "before_row_count": 0,
                    "after_row_count": 0, "dialog_closed": None}
        self.lists_page.select_first_row()
        self.lists_page.click_audit_button()
        form = self.lists_page.read_audit_dialog_form()
        dialog_closed = self.lists_page.close_audit_dialog()
        self.lists_page.enter_list_frame()
        self.lists_page._wait_table_ready()  # noqa: SLF001 - 关闭后确认列表恢复
        after = self.lists_page.get_row_count()
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
        """重新进入指定列表并按条件搜索，返回行数与首行信息（审核后核验用）。"""
        self.lists_page.open_group_item(group_text, item_rel, top_menu=top_menu)
        self.lists_page.search_list(
            phone=phone, title=title, serial_no=serial_no, member_keyword=member_keyword)
        info = self.get_current_loan_list_info()
        return {
            "row_count": info["row_count"],
            "first_serialno": info["first_serialno"],
            "first_title": info["first_title"],
            "first_member": info["first_member"],
            "src": info["src"],
        }
