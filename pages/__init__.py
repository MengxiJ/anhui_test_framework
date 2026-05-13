"""
pages包 - 存储所有页面对象
统一导出页面类，简化导入
"""
from .frontend import LoginPage, RegisterPage, OpenAccountPage, CreditApplicationPage
from .backend import BackLoginPage, LoanManagerPage

__all__ = [
    "LoginPage",
    "RegisterPage",
    "OpenAccountPage",
    "CreditApplicationPage",
    "BackLoginPage",
    "LoanManagerPage",
]
