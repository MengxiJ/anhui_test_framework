# Copyright (C) 2026. All rights reserved.
"""finance 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.finance import finance_step as lib


@composer_step(
    name="step_open_finance_recharge_page",
    description="打开前台充值页（汇付托管模拟通道）",
    category="finance",
)
def step_open_finance_recharge_page():
    """打开充值页。"""
    return lib.step_open_finance_recharge_page()


@composer_step(
    name="step_submit_finance_recharge",
    description="提交一笔充值：选通道/输金额/输验证码/提交，捕获 alert、新窗口、重定向证据（成败由记录/余额 check 判定）",
    category="finance",
    params={
        "amount": {"name": "充值金额", "type": "str", "required": True,
                   "default": "100", "description": "充值金额（元）"},
        "valicode": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "教学环境固定验证码"},
        "payment_type": {"name": "充值通道", "type": "str", "required": False,
                         "default": "chinapnrTrust", "description": "汇付托管通道 radio value"},
    },
)
def step_submit_finance_recharge(amount, valicode="8888", payment_type="chinapnrTrust"):
    """提交充值。"""
    return lib.step_submit_finance_recharge(amount, valicode=valicode, payment_type=payment_type)


@composer_step(
    name="step_get_finance_balance",
    description="打开会员中心读取账户余额（解析 78,000.00元 格式），数值放入 data.balance",
    category="finance",
)
def step_get_finance_balance():
    """读取账户余额。"""
    return lib.step_get_finance_balance()


@composer_step(
    name="step_get_finance_recharge_records",
    description="打开充值记录页读取表格，结果放入 data.headers / data.rows / data.row_count",
    category="finance",
)
def step_get_finance_recharge_records():
    """读取充值记录。"""
    return lib.step_get_finance_recharge_records()


@composer_step(
    name="step_get_finance_account_logs",
    description="打开交易明细页读取全部流水表格，结果放入 data.headers / data.rows / data.row_count",
    category="finance",
)
def step_get_finance_account_logs():
    """读取交易明细。"""
    return lib.step_get_finance_account_logs()


@composer_step(
    name="step_filter_finance_account_logs",
    description="交易明细按类型/日期区间筛选后读取表格（空参数跳过对应筛选）",
    category="finance",
    params={
        "log_type": {"name": "交易类型", "type": "str", "required": True,
                     "description": "交易分类可见文本（如“充值”）"},
        "start_date": {"name": "开始日期", "type": "str", "required": False,
                       "default": "", "description": "YYYY-MM-DD，空则不筛"},
        "end_date": {"name": "结束日期", "type": "str", "required": False,
                     "default": "", "description": "YYYY-MM-DD，空则不筛"},
    },
)
def step_filter_finance_account_logs(log_type, start_date="", end_date=""):
    """筛选交易明细。"""
    return lib.step_filter_finance_account_logs(
        log_type=log_type, start_date=start_date, end_date=end_date
    )


@composer_step(
    name="step_open_finance_withdraw_entry",
    description="打开提现入口并等待重定向稳定（未绑卡时强制跳银行卡页），最终 URL 放入 data.url",
    category="finance",
)
def step_open_finance_withdraw_entry():
    """打开提现入口。"""
    return lib.step_open_finance_withdraw_entry()


@composer_step(
    name="step_open_finance_trust_page",
    description="打开我的支付账户页（托管状态页）",
    category="finance",
)
def step_open_finance_trust_page():
    """打开我的支付账户页。"""
    return lib.step_open_finance_trust_page()


@composer_step(
    name="step_open_finance_bounty_page",
    description="打开我的红包页",
    category="finance",
)
def step_open_finance_bounty_page():
    """打开我的红包页。"""
    return lib.step_open_finance_bounty_page()
