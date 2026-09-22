# Copyright (C) 2026. All rights reserved.
"""invest 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.invest import invest_step as lib


@composer_step(
    name="step_get_risk_level",
    description="读取风险测评等级（会员中心优先，回退测评结果页），等级文本放入 data.level_text",
    category="invest",
)
def step_get_risk_level():
    """读取风险测评等级。"""
    return lib.step_get_risk_level()


@composer_step(
    name="step_submit_risk_quiz",
    description="完成一次风险测评：开页→关「风险提示」模态框→逐题作答→提交→跳转 introduce",
    category="invest",
    params={
        "answers": {"name": "作答索引列表", "type": "list", "required": False,
                    "default": None,
                    "description": "每题选项索引（0 起，长度 10）；缺省每题选第一项"},
    },
)
def step_submit_risk_quiz(answers=None):
    """提交风险测评。"""
    return lib.step_submit_risk_quiz(answers)


@composer_step(
    name="step_get_invest_list",
    description="打开投资列表解析标的卡片（loan_id/名称/可投金额），结果放入 data.loans / data.count",
    category="invest",
)
def step_get_invest_list():
    """读取投资列表。"""
    return lib.step_get_invest_list()


@composer_step(
    name="step_filter_invest_list",
    description="按筛选标签（信用标/天标/担保标等）筛选投资列表后重新读取",
    category="invest",
    params={
        "tag_text": {"name": "筛选标签", "type": "str", "required": True,
                     "description": "标签可见文本（如“信用标”）"},
    },
)
def step_filter_invest_list(tag_text):
    """筛选投资列表。"""
    return lib.step_filter_invest_list(tag_text)


@composer_step(
    name="step_open_loan_detail",
    description="从投资列表动态选标（可投≥min_available 中取最大）并进入详情页，窗口期读取详情信息（双态兼容站点重定向）",
    category="invest",
    params={
        "min_available": {"name": "最低可投金额", "type": "float", "required": False,
                          "default": 0.0, "description": "选标时标的可投金额下限（元）"},
    },
)
def step_open_loan_detail(min_available=0.0):
    """动态选标并进入详情页。"""
    return lib.step_open_loan_detail(min_available=min_available)


@composer_step(
    name="step_submit_tender",
    description="完整投标：动态选标→详情页窗口期输金额→提交（捕获拦截/提交证据，成败由我的投资/拦截 check 判定）",
    category="invest",
    params={
        "amount": {"name": "投资金额", "type": "str", "required": True,
                   "default": "1000", "description": "投标金额（元）"},
        "min_available": {"name": "最低可投金额", "type": "float", "required": False,
                          "default": 0.0, "description": "选标时标的可投金额下限（元）"},
    },
)
def step_submit_tender(amount, min_available=0.0):
    """提交投标。"""
    return lib.step_submit_tender(amount, min_available=min_available)


@composer_step(
    name="step_get_my_tenders",
    description="打开我的投资（可指定 tab：回款中/投标中/已结清/已流标）读取记录表格",
    category="invest",
    params={
        "tab": {"name": "状态 tab", "type": "str", "required": False,
                "default": "", "description": "tab 文本（空则取默认 tab）"},
    },
)
def step_get_my_tenders(tab=""):
    """读取我的投资。"""
    return lib.step_get_my_tenders(tab=tab)


@composer_step(
    name="step_get_my_tender_all_tabs",
    description="逐 tab（回款中/投标中/已结清/已流标）读取我的投资全部记录",
    category="invest",
)
def step_get_my_tender_all_tabs():
    """读取我的投资全部 tab。"""
    return lib.step_get_my_tender_all_tabs()


@composer_step(
    name="step_get_receive_plan",
    description="打开我的收款计划页（可选日期筛选）读取表格",
    category="invest",
    params={
        "start_date": {"name": "开始日期", "type": "str", "required": False,
                       "default": "", "description": "YYYY-MM-DD，空则不筛"},
        "end_date": {"name": "结束日期", "type": "str", "required": False,
                     "default": "", "description": "YYYY-MM-DD，空则不筛"},
    },
)
def step_get_receive_plan(start_date="", end_date=""):
    """读取收款计划。"""
    return lib.step_get_receive_plan(start_date=start_date, end_date=end_date)


@composer_step(
    name="step_get_debt_transfer_list",
    description="打开债权转让页（可选状态筛选：可以转让/转让中/转让成功/已撤销）读取表格与筛选项",
    category="invest",
    params={
        "status": {"name": "状态筛选", "type": "str", "required": False,
                   "default": "", "description": "下拉选项文本（空则不筛）"},
    },
)
def step_get_debt_transfer_list(status=""):
    """读取债权转让。"""
    return lib.step_get_debt_transfer_list(status=status)


@composer_step(
    name="step_open_auto_tender_entry",
    description="打开自动投标入口并捕获重定向（未开通托管时重定向托管页），最终 URL 放入 data.url",
    category="invest",
)
def step_open_auto_tender_entry():
    """打开自动投标入口。"""
    return lib.step_open_auto_tender_entry()
