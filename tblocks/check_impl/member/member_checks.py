# Copyright (C) 2026. All rights reserved.
"""member 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.member import member_check as lib


@composer_check(
    name="check_member_login_result_contains",
    description="检查前台登录后页面文本包含期望内容",
    category="member",
    params={"expected": {"name": "期望文本", "type": "str", "required": True,
                         "description": "登录成功页面应包含的文本"}},
)
def check_member_login_result_contains(expected):
    """登录结果文本检查。"""
    return lib.check_member_login_result_contains(expected)


@composer_check(
    name="check_member_register_result_contains",
    description="检查注册结果文本包含期望内容（如“注册成功”）",
    category="member",
    params={"expected": {"name": "期望文本", "type": "str", "required": True,
                         "default": "注册成功", "description": "注册成功提示"}},
)
def check_member_register_result_contains(expected="注册成功"):
    """注册结果文本检查。"""
    return lib.check_member_register_result_contains(expected)


@composer_check(
    name="check_credit_apply_result_contains",
    description="检查前台额度申请结果文本包含期望内容（如申请金额）",
    category="member",
    params={"expected": {"name": "期望文本", "type": "str", "required": True,
                         "description": "额度申请结果应包含的文本"}},
)
def check_credit_apply_result_contains(expected):
    """额度申请结果文本检查。"""
    return lib.check_credit_apply_result_contains(expected)


@composer_check(
    name="check_member_center_summary_loaded",
    description="检查会员中心总览：余额可解析为数值、未读数为非负整数",
    category="member",
)
def check_member_center_summary_loaded():
    """会员中心总览结构检查。"""
    return lib.check_member_center_summary_loaded()


@composer_check(
    name="check_recent_transactions_loaded",
    description="检查最近交易表格表头含时间/类型/金额等列，或呈现明确空态",
    category="member",
)
def check_recent_transactions_loaded():
    """最近交易表格检查。"""
    return lib.check_recent_transactions_loaded()


@composer_check(
    name="check_unread_count_consistent",
    description="检查站内消息未读数一致性（页面计数与顶栏，或中心页与消息页顶栏）",
    category="member",
)
def check_unread_count_consistent():
    """未读消息数一致性检查。"""
    return lib.check_unread_count_consistent()


@composer_check(
    name="check_member_page_loaded",
    description="检查账户管理页面关键区块标题存在（积分/安全/银行卡/推广）",
    category="member",
    params={
        "page": {"name": "页面标识", "type": "str", "required": True,
                 "description": "credit/safe/bank/spread 之一"},
        "expected_head": {"name": "区块标题", "type": "str", "required": False,
                          "default": "", "description": "期望出现的区块标题文本"},
    },
)
def check_member_page_loaded(page, expected_head=""):
    """账户管理页面区块检查。"""
    return lib.check_member_page_loaded(page, expected_head)


@composer_check(
    name="check_profile_field_updated",
    description="重新打开资料页回读字段，核对值等于提交值（忽略空白差异）",
    category="member",
    params={
        "field": {"name": "字段名", "type": "str", "required": True,
                  "description": "如 marryStatus"},
        "expected_value": {"name": "期望值", "type": "str", "required": True,
                           "description": "保存后回读应呈现的值"},
    },
)
def check_profile_field_updated(field, expected_value):
    """资料字段回读检查。"""
    return lib.check_profile_field_updated(field, expected_value)


@composer_check(
    name="check_remind_toggled",
    description="重新打开提醒页回读复选框，核对状态较切换前已翻转",
    category="member",
    params={
        "checkbox_id": {"name": "复选框标识", "type": "str", "required": True,
                        "description": "如 message_1"},
        "before": {"name": "切换前状态", "type": "bool", "required": True,
                   "description": "切换前选中状态（引用 step 的 data.before）"},
    },
)
def check_remind_toggled(checkbox_id, before):
    """提醒复选框翻转检查。"""
    return lib.check_remind_toggled(checkbox_id, before)
