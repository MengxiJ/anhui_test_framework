# Copyright (C) 2026. All rights reserved.
"""invest 域 check 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_check
from lib.common.invest import invest_check as lib


@composer_check(
    name="check_risk_level_present",
    description="检查风险测评等级非空（含等级关键词；自包含重读会员中心/结果页）",
    category="invest",
)
def check_risk_level_present():
    """等级非空检查。"""
    return lib.check_risk_level_present()


@composer_check(
    name="check_risk_quiz_submitted",
    description="检查测评提交成功（跳转 introduce）且等级生效；submitted 缺省时自包含重读等级",
    category="invest",
    params={
        "submitted": {"name": "提交跳转标志", "type": "bool", "required": False,
                      "default": None,
                      "description": "提交节点返回的 submitted（${node.data.submitted} 引用）；缺省自包含判定"},
    },
)
def check_risk_quiz_submitted(submitted=None):
    """测评提交检查。"""
    return lib.check_risk_quiz_submitted(submitted=submitted)


@composer_check(
    name="check_invest_list_loaded",
    description="检查投资列表解析 ≥N 个标的且字段完整（loan_id 数字、可投金额 float）",
    category="invest",
    params={
        "min_count": {"name": "最少标的数", "type": "int", "required": False,
                      "default": 1, "description": "标的数量下限"},
    },
)
def check_invest_list_loaded(min_count=1):
    """列表加载检查。"""
    return lib.check_invest_list_loaded(min_count=min_count)


@composer_check(
    name="check_invest_list_filter_consistent",
    description="检查投资列表筛选标签应用成功（点击成功 + 筛后列表可解析，允许空结果）",
    category="invest",
    params={
        "filter_tag": {"name": "筛选标签", "type": "str", "required": True,
                       "description": "筛选时使用的标签文本"},
    },
)
def check_invest_list_filter_consistent(filter_tag):
    """筛选一致性检查。"""
    return lib.check_invest_list_filter_consistent(filter_tag=filter_tag)


@composer_check(
    name="check_loan_detail_reachable",
    description="检查标的详情页可达（双态：窗口期就绪=严格过；站点重定向回列表=降级过并说明）",
    category="invest",
)
def check_loan_detail_reachable():
    """详情可达性检查。"""
    return lib.check_loan_detail_reachable()


@composer_check(
    name="check_tender_submitted",
    description="检查投标生效：我的投资命中「标的名称+金额」记录；站点详情页拦截时降级通过并说明（双态）",
    category="invest",
    params={
        "loan_name": {"name": "标的名称", "type": "str", "required": False,
                      "default": "", "description": "投标选中标的名称（${node.data.loan_name} 引用）"},
        "amount": {"name": "投资金额", "type": "float", "required": False,
                   "default": None, "description": "投标金额（${node.data.amount} 引用）"},
        "amount_input": {"name": "金额输入成功", "type": "bool", "required": False,
                         "default": None, "description": "投标动作金额是否输入成功（${node.data.amount_input} 引用；False=站点拦截降级依据）"},
    },
)
def check_tender_submitted(loan_name="", amount=None, amount_input=None):
    """投标生效检查。"""
    return lib.check_tender_submitted(
        loan_name=loan_name, amount=amount, amount_input=amount_input
    )


@composer_check(
    name="check_my_tenders_table_loaded",
    description="检查我的投资表格结构（tab 存在 + 表头含 项目名称/投资金额/状态，空态允许）",
    category="invest",
    params={
        "tab": {"name": "状态 tab", "type": "str", "required": False,
                "default": "回款中", "description": "要核对的状态 tab 文本"},
    },
)
def check_my_tenders_table_loaded(tab="回款中"):
    """我的投资表格检查。"""
    return lib.check_my_tenders_table_loaded(tab=tab)


@composer_check(
    name="check_receive_plan_loaded",
    description="检查我的收款计划结构（表头含 应收/标题 列，空态允许）",
    category="invest",
)
def check_receive_plan_loaded():
    """收款计划检查。"""
    return lib.check_receive_plan_loaded()


@composer_check(
    name="check_debt_transfer_loaded",
    description="检查债权转让页结构（状态下拉存在 + 页面含表格）",
    category="invest",
)
def check_debt_transfer_loaded():
    """债权转让检查。"""
    return lib.check_debt_transfer_loaded()


@composer_check(
    name="check_auto_tender_intercepted",
    description="检查自动投标入口重定向（双态：重定向托管页=严格过；停留自动投标页=降级过；其他重定向=失败）",
    category="invest",
)
def check_auto_tender_intercepted():
    """自动投标拦截检查。"""
    return lib.check_auto_tender_intercepted()
