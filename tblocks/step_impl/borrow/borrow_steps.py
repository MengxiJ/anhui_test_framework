# Copyright (C) 2026. All rights reserved.
"""borrow 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.borrow import borrow_step as lib


@composer_step(
    name="step_open_loan_index",
    description="打开前台「品质理财 → 个人借款」页",
    category="borrow",
)
def step_open_loan_index():
    """打开个人借款页。"""
    return lib.step_open_loan_index()


@composer_step(
    name="step_publish_borrow",
    description="前台发标：立即借款 → 填写发标表单 → 提交",
    category="borrow",
    params={
        "title": {"name": "借款标题", "type": "str", "required": True,
                  "description": "借款标题（≤20 字）"},
        "use": {"name": "借款用途", "type": "str", "required": False,
                "default": "周转", "enum": ["其他", "买车", "买房", "装修", "旅游", "创业", "电商", "周转", "销售"],
                "description": "借款用途"},
        "amount": {"name": "借款金额", "type": "str", "required": False,
                   "default": "200", "description": "借款金额（100~200000，50 的倍数）"},
        "apr": {"name": "年利率", "type": "str", "required": False,
                "default": "5", "description": "年利率百分比（3~10）"},
        "repay_type": {"name": "还款方式", "type": "str", "required": False,
                       "default": "等额本息", "enum": ["等额本息", "到期还本还息", "按月付息"],
                       "description": "还款方式"},
        "period": {"name": "借款期限", "type": "str", "required": False,
                   "default": "1个月", "description": "借款期限"},
        "validate": {"name": "筹标期限", "type": "str", "required": False,
                     "default": "3天", "description": "筹标期限（1~256 天）"},
        "tender_min": {"name": "最低投资", "type": "str", "required": False,
                       "default": "50元", "description": "单笔最低投资金额"},
        "tender_max": {"name": "最高投资", "type": "str", "required": False,
                       "default": "不限", "description": "单笔最高投资金额"},
        "contents": {"name": "借款描述", "type": "str", "required": False,
                     "default": "自动化测试借款标，到期还本付息。", "description": "借款描述"},
        "valicode": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
    },
)
def step_publish_borrow(
    title,
    use="周转",
    amount="200",
    apr="5",
    repay_type="等额本息",
    period="1个月",
    validate="3天",
    tender_min="50元",
    tender_max="不限",
    contents="自动化测试借款标，到期还本付息。",
    valicode="8888",
):
    """前台发标。"""
    return lib.step_publish_borrow(
        title,
        use=use,
        amount=amount,
        apr=apr,
        repay_type=repay_type,
        period=period,
        validate=validate,
        tender_min=tender_min,
        tender_max=tender_max,
        contents=contents,
        valicode=valicode,
    )


@composer_step(
    name="step_get_borrow_result_text",
    description="读取发标提交结果页面文本，结果放入 data.result",
    category="borrow",
)
def step_get_borrow_result_text():
    """读取发标结果文本。"""
    return lib.step_get_borrow_result_text()
