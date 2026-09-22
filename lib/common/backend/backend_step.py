# Copyright (C) 2026. All rights reserved.
"""backend 域 Lib 入口：运营后台步骤（无装饰器，纯实现）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.backend.utils.backend_manager import BackendManager
from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "backend_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> BackendManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, BackendManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 BackendManager（浏览器由 reset_instances 统一退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


# ---- 后台登录 ----
def step_open_backend_login_page(device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开运营后台登录页。"""
    _get_core(device_id).open_back_login_page()
    return step_result("step_open_backend_login_page", True, "已打开后台登录页", {"result": "back_login_page"})


def step_backend_login(
    username: str,
    password: str,
    img_code: str = "8888",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """管理员登录后台。"""
    _get_core(device_id).back_login(username, password, img_code)
    return step_result(
        "step_backend_login",
        True,
        f"已提交后台登录，管理员: {username}",
        {"result": "submitted", "username": username},
    )


def step_get_backend_login_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取后台登录结果文本。"""
    text = _get_core(device_id).get_back_login_result_text()
    return step_result(
        "step_get_backend_login_result_text",
        True,
        f"后台登录结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 额度审核 ----
def step_open_loan_review_menu(device_id: Optional[str] = None) -> Dict[str, Any]:
    """进入额度申请审核菜单。"""
    _get_core(device_id).open_review_menu()
    return step_result("step_open_loan_review_menu", True, "已进入额度申请审核菜单", {"result": "review_menu"})


def step_search_loan_record(phone: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """按手机号搜索额度申请记录。"""
    _get_core(device_id).search_loan_record(phone)
    return step_result(
        "step_search_loan_record",
        True,
        f"已按手机号 {phone} 搜索额度申请记录",
        {"result": "searched", "phone": phone},
    )


def step_open_loan_audit_dialog(device_id: Optional[str] = None) -> Dict[str, Any]:
    """选中申请记录并打开审核弹窗。"""
    _get_core(device_id).click_record_and_audit()
    return step_result("step_open_loan_audit_dialog", True, "已打开额度审核弹窗", {"result": "audit_dialog"})


def step_submit_loan_audit(
    note: str = "审核OK",
    img_code: str = "8888",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """审核弹窗中选择通过并提交。"""
    _get_core(device_id).approve_loan(note, img_code)
    return step_result(
        "step_submit_loan_audit",
        True,
        f"已提交额度审核，备注: {note}",
        {"result": "submitted", "note": note},
    )


def step_review_credit_application(
    phone: str,
    note: str = "审核OK",
    img_code: str = "8888",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """额度申请审核完整流程（菜单 → 搜索 → 弹窗 → 提交）。"""
    _get_core(device_id).review_credit_application(phone, note, img_code)
    return step_result(
        "step_review_credit_application",
        True,
        f"已完成手机号 {phone} 的额度申请审核",
        {"result": "reviewed", "phone": phone},
    )


def step_query_loan_application_record(
    phone: str,
    status: str = "通过",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """查询额度申请记录并按状态筛选。"""
    _get_core(device_id).query_application_record(phone, status)
    return step_result(
        "step_query_loan_application_record",
        True,
        f"已查询手机号 {phone} 的额度申请记录，状态筛选: {status}",
        {"result": "queried", "phone": phone, "status": status},
    )


def step_get_loan_review_result_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取额度审核结果状态文本。"""
    text = _get_core(device_id).get_review_result_text()
    return step_result(
        "step_get_loan_review_result_text",
        True,
        f"额度审核结果文本: {text}",
        {"result": text, "text": text},
    )


# ---- 借款/资金列表（初审标 / 满标待审 / 还款中 / 账户 / 充值 / 提现 ...） ----
def step_open_backend_loan_menu(
    group: str,
    item_rel: str,
    top_menu: str = "借款管理",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """展开指定一级菜单下分组并进入列表页（如 初审管理/loan/verify/list）。"""
    src = _get_core(device_id).open_loan_group_item(group, item_rel, top_menu=top_menu)
    return step_result(
        "step_open_backend_loan_menu",
        True,
        f"已进入后台列表 {top_menu} → {group} → {item_rel}，iframe src: {src}",
        {"result": src, "src": src, "group": group, "item_rel": item_rel, "top_menu": top_menu},
    )


def step_backend_loan_list_search(
    phone: str = "",
    title: str = "",
    serial_no: str = "",
    member_keyword: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """在当前后台列表按条件搜索（手机号 / 标题 / 编号 / 会员关键字）。"""
    _get_core(device_id).search_current_loan_list(
        phone=phone, title=title, serial_no=serial_no, member_keyword=member_keyword)
    conditions = (
        f"手机号={phone or '-'}，标题={title or '-'}，"
        f"编号={serial_no or '-'}，会员={member_keyword or '-'}")
    return step_result(
        "step_backend_loan_list_search",
        True,
        f"已在当前列表搜索（{conditions}）",
        {"result": "searched", "phone": phone, "title": title,
         "serial_no": serial_no, "member_keyword": member_keyword},
    )


def step_backend_loan_list_clear_search(device_id: Optional[str] = None) -> Dict[str, Any]:
    """清空当前列表搜索条件并重新搜索（恢复完整列表）。"""
    core = _get_core(device_id)
    core.clear_loan_list_search()
    core.search_current_loan_list()
    return step_result(
        "step_backend_loan_list_clear_search",
        True,
        "已清空搜索条件并刷新列表",
        {"result": "cleared"},
    )


def step_get_backend_loan_list_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """读取当前后台借款列表信息（iframe src / 表头 / 行数 / 首行）。"""
    info = _get_core(device_id).get_current_loan_list_info()
    first = info["first_row"]
    message = (
        f"列表 src: {info['src']}，行数 {info['row_count']}，"
        f"首行: 编号={info['first_serialno'] or '（空）'}，"
        f"用户={info['first_member'] or '（空）'}，"
        f"标题={info['first_title'] or '（空）'}"
    )
    return step_result(
        "step_get_backend_loan_list_info",
        True,
        message,
        {
            "result": info["row_count"],
            "src": info["src"],
            "headers": info["headers"],
            "headers_text": info["headers_text"],
            "row_count": info["row_count"],
            "first_row": first,
            "first_loan_id": info["first_loan_id"],
            "first_serialno": info["first_serialno"],
            "first_member": info["first_member"],
            "first_title": info["first_title"],
            "first_amount": info["first_amount"],
        },
    )


def step_backend_loan_list_review(
    group: str,
    item_rel: str,
    phone: str = "",
    title: str = "",
    serial_no: str = "",
    note: str = "审核OK",
    img_code: str = "8888",
    marker: str = "",
    top_menu: str = "借款管理",
    decision: str = "pass",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """后台列表审核完整流程（进入列表 → 搜索 → 选首行 → 审核弹窗 → 提交结论）。

    适用于初审标初审通过/不通过（marker 必填，填入「标签」字段）、
    满标待审复审通过（无 marker 字段）、资金充值/提现审核（top_menu=资金管理）等场景。
    decision=pass 提交通过，reject 提交「不通过」。
    业务成败不由本节点判定：由后续复查行数 check 核对；
    dialog_closed 为 True 表示提交后弹窗已关闭（提交生效的前端信号）。
    """
    info = _get_core(device_id).review_first_loan_in_list(
        group_text=group,
        item_rel=item_rel,
        phone=phone,
        title=title,
        serial_no=serial_no,
        note=note,
        img_code=img_code,
        marker=marker,
        top_menu=top_menu,
        decision=decision,
    )
    decision_text = "不通过" if decision == "reject" else "通过"
    if info.get("found"):
        message = (
            f"已在 {group} 列表选中并提交审核{decision_text}："
            f"编号={info['serialno']}，用户={info['member']}，"
            f"标题={info['title']}，金额={info['amount']}，"
            f"弹窗已关闭={info.get('dialog_closed')}"
        )
    else:
        message = f"{group} 列表搜索结果为空，未执行审核（row_count=0）"
    return step_result(
        "step_backend_loan_list_review",
        True,
        message,
        {"result": info.get("found"), **info},
    )


def step_backend_audit_dialog_inspect(device_id: Optional[str] = None) -> Dict[str, Any]:
    """当前资金/借款审核列表：选中首行 → 打开审核弹窗 → 只读表单 → 取消关闭（不提交）。

    返回审核结论选项、备注/验证码/标签字段、保存与取消按钮是否齐备，
    以及弹窗关闭状态与关闭前后行数（核对零数据变更）。须已进入目标审核列表。
    """
    info = _get_core(device_id).inspect_audit_dialog()
    if info.get("found"):
        message = (
            f"审核弹窗只读巡检：结论选项[{info.get('radio_texts', '')}]，"
            f"备注={info.get('has_note')}，验证码={info.get('has_valicode')}，"
            f"标签字段={info.get('has_marker')}，"
            f"按钮[{info.get('save_buttons', '')}/{info.get('cancel_buttons', '')}]，"
            f"取消后弹窗关闭={info.get('dialog_closed')}，"
            f"行数 {info.get('before_row_count')} → {info.get('after_row_count')}"
        )
    else:
        message = "当前审核列表为空，未打开弹窗（before_row_count=0）"
    return step_result(
        "step_backend_audit_dialog_inspect",
        True,
        message,
        {"result": info.get("found"), **info},
    )


def step_backend_loan_list_requery(
    group: str,
    item_rel: str,
    phone: str = "",
    title: str = "",
    serial_no: str = "",
    top_menu: str = "借款管理",
    member_keyword: str = "",
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """重新进入指定后台列表并按条件搜索（审核后状态流转核验）。"""
    info = _get_core(device_id).requery_loan_list_count(
        group_text=group,
        item_rel=item_rel,
        phone=phone,
        title=title,
        serial_no=serial_no,
        top_menu=top_menu,
        member_keyword=member_keyword,
    )
    message = (
        f"复查 {group} 列表（src: {info['src']}）："
        f"匹配 {info['row_count']} 行，"
        f"首行编号={info['first_serialno'] or '（空）'}"
    )
    return step_result(
        "step_backend_loan_list_requery",
        True,
        message,
        {
            "result": info["row_count"],
            "row_count": info["row_count"],
            "first_serialno": info["first_serialno"],
            "first_title": info["first_title"],
            "first_member": info["first_member"],
            "src": info["src"],
        },
    )
