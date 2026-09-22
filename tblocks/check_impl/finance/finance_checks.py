# Copyright (C) 2026. All rights reserved.
"""finance 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.finance import finance_check as lib


@composer_check(
    name="check_finance_balance_increased_at_least",
    description="检查当前余额较前值增加不少于 N（实时打开会员中心读取）",
    category="finance",
    params={
        "previous_balance": {"name": "前值余额", "type": "float", "required": True,
                             "description": "充值前读取的余额（${step_x.data.balance} 引用）"},
        "min_increase": {"name": "最小增量", "type": "float", "required": False,
                         "default": 0.0, "description": "余额增量下限（默认 0）"},
    },
)
def check_finance_balance_increased_at_least(previous_balance, min_increase=0.0):
    """余额增量检查。"""
    return lib.check_finance_balance_increased_at_least(previous_balance, min_increase=min_increase)


@composer_check(
    name="check_finance_recharge_record_exists",
    description="检查充值记录中存在「金额相等 + 时间窗口内 + 状态关键字」的记录行",
    category="finance",
    params={
        "amount": {"name": "充值金额", "type": "str", "required": True,
                   "description": "待核对的充值金额（元）"},
        "status_contains": {"name": "状态关键字", "type": "str", "required": False,
                            "default": "充值成功", "description": "状态列应包含的文本"},
        "time_window": {"name": "时间窗口(秒)", "type": "float", "required": False,
                        "default": 900.0, "description": "记录时间与当前时间的允许偏差"},
    },
)
def check_finance_recharge_record_exists(amount, status_contains="充值成功", time_window=900.0):
    """充值记录存在检查。"""
    return lib.check_finance_recharge_record_exists(
        amount, status_contains=status_contains, time_window=time_window
    )


@composer_check(
    name="check_finance_account_log_exists",
    description="检查交易明细中存在「金额相等 + 时间窗口内（+ 类型关键字）」的流水行",
    category="finance",
    params={
        "amount": {"name": "交易金额", "type": "str", "required": True,
                   "description": "待核对的交易金额（元）"},
        "type_contains": {"name": "类型关键字", "type": "str", "required": False,
                          "default": "", "description": "类型列应包含的文本（空则不校验类型）"},
        "time_window": {"name": "时间窗口(秒)", "type": "float", "required": False,
                        "default": 900.0, "description": "记录时间与当前时间的允许偏差"},
    },
)
def check_finance_account_log_exists(amount, type_contains="", time_window=900.0):
    """交易明细存在检查。"""
    return lib.check_finance_account_log_exists(
        amount, type_contains=type_contains, time_window=time_window
    )


@composer_check(
    name="check_finance_account_log_filter_consistent",
    description="检查当前（已筛选）交易明细的类型列与筛选条件一致；空结果时校验空态文案",
    category="finance",
    params={
        "expected_type": {"name": "期望类型", "type": "str", "required": True,
                          "description": "筛选时使用的交易类型文本"},
    },
)
def check_finance_account_log_filter_consistent(expected_type):
    """筛选结果类型一致性检查。"""
    return lib.check_finance_account_log_filter_consistent(expected_type)


@composer_check(
    name="check_finance_withdraw_intercepted",
    description="检查提现入口前置拦截：未绑卡重定向银行卡页；已绑卡降级为提现页可达（双态兼容）",
    category="finance",
)
def check_finance_withdraw_intercepted():
    """提现拦截检查。"""
    return lib.check_finance_withdraw_intercepted()


@composer_check(
    name="check_finance_trust_page_blocks_visible",
    description="检查我的支付账户页关键区块可见（默认「账户托管」「授权设置」）",
    category="finance",
    params={
        "blocks": {"name": "区块文本列表", "type": "list", "required": False,
                   "default": ["账户托管", "授权设置"], "description": "页面应包含的区块文本"},
    },
)
def check_finance_trust_page_blocks_visible(blocks=None):
    """托管页区块检查。"""
    return lib.check_finance_trust_page_blocks_visible(blocks)


@composer_check(
    name="check_finance_bounty_page_loaded",
    description="检查我的红包页可达且含红包相关内容",
    category="finance",
)
def check_finance_bounty_page_loaded():
    """红包页检查。"""
    return lib.check_finance_bounty_page_loaded()
