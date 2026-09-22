# Copyright (C) 2026. All rights reserved.
"""member 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.member import member_step as lib


@composer_step(
    name="step_open_member_login_page",
    description="打开安汇智投前台会员登录页",
    category="member",
)
def step_open_member_login_page():
    """打开前台登录页。"""
    return lib.step_open_member_login_page()


@composer_step(
    name="step_member_login",
    description="前台会员登录：输入手机号、密码并提交（结果由后续 check 节点验证）",
    category="member",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True,
                  "default": "${custom_params.user_phone}", "description": "会员手机号"},
        "password": {"name": "密码", "type": "str", "required": True,
                     "default": "${custom_params.user_password}", "description": "登录密码"},
    },
)
def step_member_login(phone, password):
    """前台会员登录。"""
    return lib.step_member_login(phone, password)


@composer_step(
    name="step_get_member_login_result_text",
    description="读取登录后页面提示文本，结果放入 data.result",
    category="member",
)
def step_get_member_login_result_text():
    """读取登录结果文本。"""
    return lib.step_get_member_login_result_text()


@composer_step(
    name="step_open_member_register_page",
    description="打开前台会员注册页",
    category="member",
)
def step_open_member_register_page():
    """打开注册页。"""
    return lib.step_open_member_register_page()


@composer_step(
    name="step_member_register",
    description="前台会员注册（测试环境图形验证码 8888、短信验证码 666666）",
    category="member",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True, "description": "注册手机号"},
        "password": {"name": "密码", "type": "str", "required": True, "description": "登录密码"},
        "verifycode": {"name": "图形验证码", "type": "str", "required": False,
                       "default": "8888", "description": "固定测试图形验证码"},
        "phone_code": {"name": "短信验证码", "type": "str", "required": False,
                       "default": "666666", "description": "固定测试短信验证码"},
    },
)
def step_member_register(phone, password, verifycode="8888", phone_code="666666"):
    """前台会员注册。"""
    return lib.step_member_register(phone, password, verifycode, phone_code)


@composer_step(
    name="step_get_member_register_result_text",
    description="读取注册结果文本，结果放入 data.result",
    category="member",
)
def step_get_member_register_result_text():
    """读取注册结果文本。"""
    return lib.step_get_member_register_result_text()


@composer_step(
    name="step_open_trust_account",
    description="开通第三方资金托管账号（填写真实姓名、身份证并确认）",
    category="member",
    params={
        "real_name": {"name": "真实姓名", "type": "str", "required": True,
                      "default": "${custom_params.test_name}", "description": "实名姓名"},
        "id_card": {"name": "身份证号", "type": "str", "required": True,
                    "default": "${custom_params.test_id_card}", "description": "身份证号码"},
        "expect_success": {"name": "预期成功", "type": "bool", "required": False,
                           "default": True, "description": "是否继续确认开通弹窗"},
    },
)
def step_open_trust_account(real_name, id_card, expect_success=True):
    """托管开户。"""
    return lib.step_open_trust_account(real_name, id_card, expect_success=expect_success)


@composer_step(
    name="step_get_trust_account_result_text",
    description="读取托管开户结果文本（新窗口），结果放入 data.result",
    category="member",
)
def step_get_trust_account_result_text():
    """读取开户结果文本。"""
    return lib.step_get_trust_account_result_text()


@composer_step(
    name="step_apply_credit_limit",
    description="前台提交借款额度申请（金额、详情、图形验证码）",
    category="member",
    params={
        "amount": {"name": "申请额度", "type": "str", "required": True,
                   "default": "100000", "description": "申请金额"},
        "detail_msg": {"name": "申请详情", "type": "str", "required": True,
                       "default": "额度申请详情信息", "description": "申请说明"},
        "img_code": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
    },
)
def step_apply_credit_limit(amount, detail_msg, img_code="8888"):
    """额度申请。"""
    return lib.step_apply_credit_limit(amount, detail_msg, img_code)


@composer_step(
    name="step_get_credit_apply_result_text",
    description="读取前台额度申请结果文本，结果放入 data.result",
    category="member",
)
def step_get_credit_apply_result_text():
    """读取额度申请结果文本。"""
    return lib.step_get_credit_apply_result_text()


@composer_step(
    name="step_get_member_center_summary",
    description="打开会员中心并读取总览：余额/未读消息数/测评等级文本",
    category="member",
)
def step_get_member_center_summary():
    """读取会员中心总览。"""
    return lib.step_get_member_center_summary()


@composer_step(
    name="step_get_recent_transactions",
    description="读取会员中心「最近交易」表格（表头/数据行/空态）",
    category="member",
)
def step_get_recent_transactions():
    """读取最近交易表格。"""
    return lib.step_get_recent_transactions()


@composer_step(
    name="step_get_message_page_info",
    description="打开站内消息页，读取顶栏未读数与页面级未读数",
    category="member",
)
def step_get_message_page_info():
    """读取站内消息页信息。"""
    return lib.step_get_message_page_info()


@composer_step(
    name="step_get_message_list_info",
    description="打开站内消息列表，读取顶栏未读数、列表未读条数与首封未读标题（data.list_unread/topbar_unread）",
    category="member",
)
def step_get_message_list_info():
    """读取站内消息列表信息。"""
    return lib.step_get_message_list_info()


@composer_step(
    name="step_open_first_unread_message",
    description="点开列表首封未读消息（页内内联展开详情），返回详情文本与顶栏未读数变化 data.topbar_delta",
    category="member",
)
def step_open_first_unread_message():
    """读首封未读站内信。"""
    return lib.step_open_first_unread_message()


@composer_step(
    name="step_get_message_relist_info",
    description="读信后重新打开消息列表，读取列表未读条数前后变化 data.list_unread_delta",
    category="member",
)
def step_get_message_relist_info():
    """读信后重读列表核对未读变化。"""
    return lib.step_get_message_relist_info()


@composer_step(
    name="step_open_member_page",
    description="打开账户管理页面（credit 积分/safe 安全设置/bank 银行卡/spread 推广）并读区块",
    category="member",
    params={
        "page": {"name": "页面标识", "type": "str", "required": True,
                 "description": "credit/safe/bank/spread 之一"},
    },
)
def step_open_member_page(page):
    """打开账户管理页面。"""
    return lib.step_open_member_page(page)


@composer_step(
    name="step_read_member_profile",
    description="打开基础信息页并读取全部字段快照",
    category="member",
)
def step_read_member_profile():
    """读取基础信息快照。"""
    return lib.step_read_member_profile()


@composer_step(
    name="step_edit_member_profile_field",
    description="编辑单个基础资料字段并保存（进编辑态→改值→提交）",
    category="member",
    params={
        "field": {"name": "字段名", "type": "str", "required": True,
                  "description": "如 marryStatus / educationalBackground"},
        "value": {"name": "目标值", "type": "str", "required": True,
                  "description": "下拉选项可见文本或输入框值"},
    },
)
def step_edit_member_profile_field(field, value):
    """编辑基础资料字段。"""
    return lib.step_edit_member_profile_field(field, value)


@composer_step(
    name="step_read_remind_states",
    description="打开提醒设置页并读取全部复选框状态",
    category="member",
)
def step_read_remind_states():
    """读取提醒设置快照。"""
    return lib.step_read_remind_states()


@composer_step(
    name="step_toggle_remind",
    description="切换单个提醒复选框并提交，data.before 为切换前状态",
    category="member",
    params={
        "checkbox_id": {"name": "复选框标识", "type": "str", "required": True,
                        "description": "如 message_1 / email_1 / phone_notice"},
    },
)
def step_toggle_remind(checkbox_id):
    """切换提醒复选框。"""
    return lib.step_toggle_remind(checkbox_id)
