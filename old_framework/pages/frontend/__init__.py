"""前台页面模块 - 用户注册、登录、申请等页面"""

from .page_login import LoginPage
from .page_register import RegisterPage
from .page_open_account import OpenAccountPage
from .page_credit_application import CreditApplicationPage

__all__ = [
    "LoginPage",
    "RegisterPage",
    "OpenAccountPage",
    "CreditApplicationPage",
]
