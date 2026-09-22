# Copyright (C) 2026. All rights reserved.
"""前台会员业务核心类（普通类，类内不做单例）。

组合前台各 PageObject，页面对象与 WebDriver 同生命周期；
本类不负责浏览器创建与退出，只负责业务编排。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.member.pages import (
    CreditApplicationPage,
    LoginPage,
    MemberCenterPage,
    MemberInfoPage,
    MemberMiscPage,
    MessagePage,
    OpenAccountPage,
    RegisterPage,
    RemindPage,
)


class MemberManager:
    """前台会员业务（登录 / 注册 / 开户 / 额度申请 / 中心总览 / 资料 / 提醒 / 杂项页）。"""

    def __init__(self, driver) -> None:
        self.driver = driver
        self._login_page: Optional[LoginPage] = None
        self._register_page: Optional[RegisterPage] = None
        self._open_account_page: Optional[OpenAccountPage] = None
        self._credit_page: Optional[CreditApplicationPage] = None
        self._center_page: Optional[MemberCenterPage] = None
        self._info_page: Optional[MemberInfoPage] = None
        self._remind_page: Optional[RemindPage] = None
        self._misc_page: Optional[MemberMiscPage] = None
        self._message_page: Optional[MessagePage] = None
        # 跨节点状态：会员中心读到的顶栏未读数（供消息页一致性 check 使用）
        self._center_unread: Optional[int] = None
        # 跨节点状态：读信前列表未读条数（供读信后回列表 delta check 使用）
        self._message_list_unread: int = 0

    # ---- 页面对象懒加载（与 driver 绑定，随实例复用） ----
    @property
    def login_page(self) -> LoginPage:
        if self._login_page is None:
            self._login_page = LoginPage(self.driver)
        return self._login_page

    @property
    def register_page(self) -> RegisterPage:
        if self._register_page is None:
            self._register_page = RegisterPage(self.driver)
        return self._register_page

    @property
    def open_account_page(self) -> OpenAccountPage:
        if self._open_account_page is None:
            self._open_account_page = OpenAccountPage(self.driver)
        return self._open_account_page

    @property
    def credit_page(self) -> CreditApplicationPage:
        if self._credit_page is None:
            self._credit_page = CreditApplicationPage(self.driver)
        return self._credit_page

    @property
    def center_page(self) -> MemberCenterPage:
        if self._center_page is None:
            self._center_page = MemberCenterPage(self.driver)
        return self._center_page

    @property
    def info_page(self) -> MemberInfoPage:
        if self._info_page is None:
            self._info_page = MemberInfoPage(self.driver)
        return self._info_page

    @property
    def remind_page(self) -> RemindPage:
        if self._remind_page is None:
            self._remind_page = RemindPage(self.driver)
        return self._remind_page

    @property
    def misc_page(self) -> MemberMiscPage:
        if self._misc_page is None:
            self._misc_page = MemberMiscPage(self.driver)
        return self._misc_page

    @property
    def message_page(self) -> MessagePage:
        if self._message_page is None:
            self._message_page = MessagePage(self.driver)
        return self._message_page

    # ---- 登录 ----
    def open_login_page(self) -> None:
        self.login_page.open_url()

    def login(self, phone: str, password: str) -> None:
        """填写手机号/密码并点击登录（不含结果断言）。"""
        self.login_page.login(phone, password)

    def get_login_result_text(self) -> str:
        return self.login_page.get_result_success_text()

    # ---- 注册 ----
    def open_register_page(self) -> None:
        self.register_page.open_url()

    def register(
        self,
        phone: str,
        password: str,
        verifycode: str = "8888",
        phone_code: str = "666666",
    ) -> None:
        self.register_page.register(phone, password, verifycode, phone_code)

    def get_register_result_text(self) -> str:
        return self.register_page.get_result_success_text()

    # ---- 托管开户 ----
    def open_account(self, real_name: str, id_card: str, expect_success: bool = True) -> None:
        """开通第三方资金托管账号。"""
        self.open_account_page.open_account(real_name, id_card, expect_success=expect_success)

    def get_open_account_result_text(self) -> str:
        return self.open_account_page.get_result_success_text()

    # ---- 额度申请 ----
    def credit_application(self, amount: str, detail_msg: str, img_code: str = "8888") -> None:
        """借款额度申请（切换借款账户 → 填写金额/详情/验证码 → 提交）。"""
        self.credit_page.credit_application(amount, detail_msg, img_code)

    def get_credit_application_result_text(self) -> str:
        return self.credit_page.get_result_success_text()

    # ---- 会员中心总览 ----
    def open_center(self) -> None:
        """打开会员中心总览页。"""
        self.center_page.open_url()

    def get_center_summary(self) -> Dict[str, Any]:
        """读取会员中心总览（余额/未读数/测评等级文本），并缓存顶栏未读数。"""
        self.center_page.open_url()
        info = self.center_page.read_center_info()
        self._center_unread = info.get("unread_count")
        return info

    def get_recent_transactions(self) -> Dict[str, Any]:
        """读取会员中心「最近交易」表格（须先在会员中心页）。"""
        return self.center_page.read_recent_transactions()

    # ---- 站内消息 ----
    def get_message_page_info(self) -> Dict[str, Any]:
        """打开站内消息页，读取顶栏未读数与页面级未读数。"""
        return self.message_page.read_message_info(center_unread=self._center_unread)

    def get_message_list_info(self) -> Dict[str, Any]:
        """打开站内消息列表，读取顶栏未读数、列表未读条数与行快照，并缓存未读条数。"""
        info = self.message_page.read_list_info()
        self._message_list_unread = int(info.get("list_unread", 0))
        return info

    def open_first_unread_message(self) -> Dict[str, Any]:
        """点开列表首封未读消息（须先打开列表），返回标题、详情文本与顶栏未读变化。"""
        return self.message_page.open_first_unread()

    def get_message_relist_info(self) -> Dict[str, Any]:
        """读信后重新打开列表，返回列表未读条数前后对比（与缓存的读信前快照对比）。"""
        before = getattr(self, "_message_list_unread", 0)
        return self.message_page.read_list_info_after_read(before)

    # ---- 账户管理杂项页 ----
    def open_member_page(self, page: str) -> Dict[str, Any]:
        """打开积分/安全/银行卡/推广页并读取关键区块与最终 URL。"""
        return self.misc_page.read_page_info(page)

    # ---- 基础资料 ----
    def read_profile(self) -> Dict[str, str]:
        """打开基础信息页并读取全部字段快照。"""
        self.info_page.open_url()
        return self.info_page.read_all_profile()

    def read_profile_field(self, field: str) -> str:
        """打开基础信息页并读取单个字段当前值（供回读核对）。"""
        self.info_page.open_url()
        return self.info_page.read_profile_field(field)

    def edit_profile_field(self, field: str, value: str) -> Dict[str, Any]:
        """打开资料页 → 改字段（page 按禁用态自动进编辑态）→ 保存，返回前值与结果。"""
        self.info_page.open_url()
        before = self.info_page.read_profile_field(field)
        changed = self.info_page.edit_profile_field(field, value)
        save_clicked = self.info_page.click_save(wait_field=field) if changed else False
        save_result = self.info_page.read_save_result() if save_clicked else ""
        return {
            "field": field,
            "value": value,
            "before": before,
            "changed": changed,
            "save_clicked": save_clicked,
            "save_result": save_result,
        }

    # ---- 提醒设置 ----
    def read_remind_states(self) -> Dict[str, bool]:
        """打开提醒设置页并读取全部复选框状态。"""
        self.remind_page.open_url()
        return self.remind_page.read_all_states()

    def read_remind_state(self, checkbox_id: str) -> bool:
        """打开提醒设置页并读取单个复选框状态（供回读核对）。"""
        self.remind_page.open_url()
        return self.remind_page.read_checkbox_state(checkbox_id)

    def toggle_remind(self, checkbox_id: str) -> Dict[str, Any]:
        """打开提醒页 → 切换复选框 → 提交，返回切换前状态。"""
        self.remind_page.open_url()
        before = self.remind_page.toggle_checkbox(checkbox_id)
        submitted = self.remind_page.click_submit()
        result_text = self.remind_page.read_submit_result() if submitted else ""
        return {
            "checkbox_id": checkbox_id,
            "before": before,
            "submitted": submitted,
            "result_text": result_text,
        }
