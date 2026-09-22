# Copyright (C) 2026. All rights reserved.
"""前台会员域页面对象（注册 / 登录 / 开户 / 额度申请 / 中心总览 / 资料 / 提醒 / 杂项）。"""
from .page_credit_application import CreditApplicationPage
from .page_login import LoginPage
from .page_member_center import MemberCenterPage
from .page_member_info import MemberInfoPage
from .page_member_misc import MemberMiscPage, MessagePage
from .page_open_account import OpenAccountPage
from .page_register import RegisterPage
from .page_remind import RemindPage

__all__ = [
    "LoginPage",
    "RegisterPage",
    "OpenAccountPage",
    "CreditApplicationPage",
    "MemberCenterPage",
    "MemberInfoPage",
    "RemindPage",
    "MemberMiscPage",
    "MessagePage",
]
