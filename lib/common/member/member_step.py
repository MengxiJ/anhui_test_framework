# Copyright (C) 2026. All rights reserved.
"""member 域 Lib 入口：前台会员步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.member.utils.member_manager import MemberManager
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "member_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> MemberManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, MemberManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 MemberManager（浏览器由 reset_instances 统一退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


# ---- 登录 ----
def step_open_member_login_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开前台会员登录页。"""
    _get_core(device_id).open_login_page()
    return step_result("step_open_member_login_page", True, "已打开前台登录页", {"result": "login_page"})


def step_member_login(
    phone: str,
    password: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """前台会员登录（输入手机号、密码并提交）。"""
    _get_core(device_id).login(phone, password)
    return step_result(
        "step_member_login",
        True,
        f"已提交会员登录，手机号: {phone}",
        {"result": "submitted", "phone": phone},
    )


def step_get_member_login_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取登录后页面提示文本，结果放入 ``data.result``。"""
    text = _get_core(device_id).get_login_result_text()
    return step_result(
        "step_get_member_login_result_text",
        True,
        f"登录结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 注册 ----
def step_open_member_register_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开前台注册页。"""
    _get_core(device_id).open_register_page()
    return step_result("step_open_member_register_page", True, "已打开前台注册页", {"result": "register_page"})


def step_member_register(
    phone: str,
    password: str,
    verifycode: str = "8888",
    phone_code: str = "666666",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """前台会员注册（图形验证码固定 8888，短信验证码测试环境固定 666666）。"""
    _get_core(device_id).register(phone, password, verifycode, phone_code)
    return step_result(
        "step_member_register",
        True,
        f"已提交会员注册，手机号: {phone}",
        {"result": "submitted", "phone": phone},
    )


def step_get_member_register_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取注册结果文本。"""
    text = _get_core(device_id).get_register_result_text()
    return step_result(
        "step_get_member_register_result_text",
        True,
        f"注册结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 托管开户 ----
def step_open_trust_account(
    real_name: str,
    id_card: str,
    expect_success: bool = True,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """开通第三方资金托管账号。"""
    _get_core(device_id).open_account(real_name, id_card, expect_success=expect_success)
    return step_result(
        "step_open_trust_account",
        True,
        f"已提交托管开户申请，姓名: {real_name}",
        {"result": "submitted", "real_name": real_name},
    )


def step_get_trust_account_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取托管开户结果文本。"""
    text = _get_core(device_id).get_open_account_result_text()
    return step_result(
        "step_get_trust_account_result_text",
        True,
        f"开户结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 额度申请 ----
def step_apply_credit_limit(
    amount: str,
    detail_msg: str,
    img_code: str = "8888",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """前台提交借款额度申请。"""
    _get_core(device_id).credit_application(amount, detail_msg, img_code)
    return step_result(
        "step_apply_credit_limit",
        True,
        f"已提交额度申请，金额: {amount}",
        {"result": "submitted", "amount": str(amount)},
    )


def step_get_credit_apply_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取额度申请结果文本。"""
    text = _get_core(device_id).get_credit_application_result_text()
    return step_result(
        "step_get_credit_apply_result_text",
        True,
        f"额度申请结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 会员中心总览 ----
def step_get_member_center_summary(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开会员中心并读取总览：余额/未读消息数/测评等级文本是否存在。"""
    info = _get_core(device_id).get_center_summary()
    balance = info.get("balance")
    return step_result(
        "step_get_member_center_summary",
        True,
        f"会员中心总览：余额={balance}，未读消息={info.get('unread_count')}，"
        f"含测评等级文本={info.get('risk_level_present')}",
        dict(info),
    )


def step_get_recent_transactions(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取会员中心「最近交易」表格（表头/数据行/空态）。"""
    data = _get_core(device_id).get_recent_transactions()
    return step_result(
        "step_get_recent_transactions",
        True,
        f"最近交易：表头 {len(data.get('headers', []))} 列，"
        f"数据 {data.get('row_count', 0)} 行，空态={data.get('empty_state')}",
        dict(data),
    )


# ---- 站内消息 ----
def step_get_message_page_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开站内消息页，读取顶栏未读数与页面级未读数。"""
    info = _get_core(device_id).get_message_page_info()
    return step_result(
        "step_get_message_page_info",
        True,
        f"站内消息页：顶栏未读={info.get('topbar_unread')}，"
        f"页面未读={info.get('page_unread')}，进入前中心未读={info.get('center_unread')}",
        dict(info),
    )


def step_get_message_list_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开站内消息列表，读取顶栏未读数、列表未读条数与首封未读标题。"""
    info = _get_core(device_id).get_message_list_info()
    return step_result(
        "step_get_message_list_info",
        True,
        f"站内消息列表：共 {info.get('row_count')} 行，"
        f"未读 {info.get('list_unread')} 封，顶栏未读={info.get('topbar_unread')}，"
        f"首封未读标题={info.get('first_unread_title') or '（无）'}",
        dict(info),
    )


def step_open_first_unread_message(device_id: Optional[str] = None) -> Dict[str, Any]:
    """点开列表首封未读消息，返回详情文本与顶栏未读数变化（须先打开消息列表）。"""
    info = _get_core(device_id).open_first_unread_message()
    if info.get("opened"):
        message = (
            f"已打开未读消息「{info.get('title')}」，"
            f"顶栏未读 {info.get('topbar_before')} → {info.get('topbar_after')}"
        )
    else:
        message = "当前列表无未读消息，未执行读信"
    return step_result(
        "step_open_first_unread_message",
        True,
        message,
        dict(info),
    )


def step_get_message_relist_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读信后重新打开消息列表，读取列表未读条数前后变化。"""
    info = _get_core(device_id).get_message_relist_info()
    return step_result(
        "step_get_message_relist_info",
        True,
        f"重读消息列表：未读 {info.get('list_unread_before')} → "
        f"{info.get('list_unread_after')}（变化 {info.get('list_unread_delta')}），"
        f"顶栏未读={info.get('topbar_unread')}",
        dict(info),
    )


# ---- 账户管理杂项页 ----
def step_open_member_page(page: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开账户管理页面（credit 积分 / safe 安全设置 / bank 银行卡 / spread 推广）。"""
    info = _get_core(device_id).open_member_page(page)
    return step_result(
        "step_open_member_page",
        True,
        f"已打开页面 {page}，最终 URL: {info.get('final_url')}，"
        f"区块「{info.get('expected_head')}」存在={info.get('head_present')}",
        dict(info),
    )


# ---- 基础资料 ----
def step_read_member_profile(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开基础信息页并读取全部字段快照。"""
    profile = _get_core(device_id).read_profile()
    return step_result(
        "step_read_member_profile",
        True,
        f"已读取基础信息快照，共 {len(profile)} 个字段",
        {"profile": profile},
    )


def step_edit_member_profile_field(
    field: str,
    value: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """编辑单个基础资料字段并保存（进编辑态 → 改值 → 提交）。"""
    info = _get_core(device_id).edit_profile_field(field, value)
    return step_result(
        "step_edit_member_profile_field",
        bool(info.get("changed")),
        f"字段 {field}：{info.get('before')!r} → {value!r}，"
        f"保存按钮已点击={info.get('save_clicked')}，提示={info.get('save_result')!r}",
        dict(info),
    )


# ---- 提醒设置 ----
def step_read_remind_states(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开提醒设置页并读取全部复选框状态。"""
    states = _get_core(device_id).read_remind_states()
    return step_result(
        "step_read_remind_states",
        True,
        f"已读取提醒设置，共 {len(states)} 个复选框",
        {"states": states},
    )


def step_toggle_remind(
    checkbox_id: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """切换单个提醒复选框并提交，data.before 为切换前状态。"""
    info = _get_core(device_id).toggle_remind(checkbox_id)
    return step_result(
        "step_toggle_remind",
        bool(info.get("submitted")),
        f"复选框 {checkbox_id} 切换前={info.get('before')}，"
        f"提交={info.get('submitted')}，提示={info.get('result_text')!r}",
        dict(info),
    )
