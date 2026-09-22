# Copyright (C) 2026. All rights reserved.
"""backend 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.backend import admin_api_step as lib_admin
from lib.common.backend import backend_step as lib


# ---- 后台 8082 HTTP 接口 ----
@composer_step(
    name="step_backend_api_get_verifycode",
    description="获取后台登录图形验证码 GET /common/public/verifycode/{r}",
    category="backend",
)
def step_backend_api_get_verifycode():
    """后台登录图形验证码接口。"""
    return lib_admin.step_backend_api_get_verifycode()


@composer_step(
    name="step_backend_api_login",
    description="后台管理员 HTTP 登录 POST /system/public/verifyLogin（默认先取图形验证码）",
    category="backend",
    params={
        "username": {"name": "管理员", "type": "str", "required": True,
                     "default": "${custom_params.admin_username}", "description": "管理员账号"},
        "password": {"name": "密码", "type": "str", "required": True,
                     "default": "${custom_params.admin_password}", "description": "管理员密码"},
        "valicode": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
        "fetch_code": {"name": "先取验证码", "type": "bool", "required": False,
                       "default": True, "description": "提交前是否先在同会话拉取图形验证码"},
    },
)
def step_backend_api_login(username, password, valicode="8888", fetch_code=True):
    """后台管理员 HTTP 登录。"""
    return lib_admin.step_backend_api_login(
        username, password, valicode=valicode, fetch_code=fetch_code,
    )


@composer_step(
    name="step_open_backend_login_page",
    description="打开安汇智投运营后台登录页",
    category="backend",
)
def step_open_backend_login_page():
    """打开后台登录页。"""
    return lib.step_open_backend_login_page()


@composer_step(
    name="step_backend_login",
    description="运营后台管理员登录（用户名、密码、图形验证码）",
    category="backend",
    params={
        "username": {"name": "管理员", "type": "str", "required": True,
                     "default": "${custom_params.admin_username}", "description": "管理员账号"},
        "password": {"name": "密码", "type": "str", "required": True,
                     "default": "${custom_params.admin_password}", "description": "管理员密码"},
        "img_code": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
    },
)
def step_backend_login(username, password, img_code="8888"):
    """后台登录。"""
    return lib.step_backend_login(username, password, img_code)


@composer_step(
    name="step_get_backend_login_result_text",
    description="读取后台登录成功提示文本，结果放入 data.result",
    category="backend",
)
def step_get_backend_login_result_text():
    """读取后台登录结果文本。"""
    return lib.step_get_backend_login_result_text()


@composer_step(
    name="step_open_loan_review_menu",
    description="进入 借款管理 → 额度管理 → 额度申请审核 菜单",
    category="backend",
)
def step_open_loan_review_menu():
    """进入审核菜单。"""
    return lib.step_open_loan_review_menu()


@composer_step(
    name="step_search_loan_record",
    description="在审核页 iframe 中按会员手机号搜索额度申请记录",
    category="backend",
    params={"phone": {"name": "手机号", "type": "str", "required": True,
                      "default": "${custom_params.user_phone}", "description": "申请人手机号"}},
)
def step_search_loan_record(phone):
    """搜索申请记录。"""
    return lib.step_search_loan_record(phone)


@composer_step(
    name="step_open_loan_audit_dialog",
    description="选中首条申请记录并打开审核弹窗",
    category="backend",
)
def step_open_loan_audit_dialog():
    """打开审核弹窗。"""
    return lib.step_open_loan_audit_dialog()


@composer_step(
    name="step_submit_loan_audit",
    description="审核弹窗中选择通过、填写备注与验证码并保存",
    category="backend",
    params={
        "note": {"name": "审核备注", "type": "str", "required": False,
                 "default": "审核OK", "description": "审核意见"},
        "img_code": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
    },
)
def step_submit_loan_audit(note="审核OK", img_code="8888"):
    """提交审核。"""
    return lib.step_submit_loan_audit(note, img_code)


@composer_step(
    name="step_review_credit_application",
    description="额度申请审核完整流程（菜单 → 搜索 → 弹窗 → 提交通过）",
    category="backend",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True,
                  "default": "${custom_params.user_phone}", "description": "申请人手机号"},
        "note": {"name": "审核备注", "type": "str", "required": False,
                 "default": "审核OK", "description": "审核意见"},
        "img_code": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
    },
)
def step_review_credit_application(phone, note="审核OK", img_code="8888"):
    """额度审核完整流程。"""
    return lib.step_review_credit_application(phone, note, img_code)


@composer_step(
    name="step_query_loan_application_record",
    description="查询额度申请记录并按状态筛选",
    category="backend",
    params={
        "phone": {"name": "手机号", "type": "str", "required": True,
                  "default": "${custom_params.user_phone}", "description": "申请人手机号"},
        "status": {"name": "审核状态", "type": "str", "required": False,
                   "default": "通过", "enum": ["通过", "拒绝", ""], "description": "状态筛选"},
    },
)
def step_query_loan_application_record(phone, status="通过"):
    """查询审核记录。"""
    return lib.step_query_loan_application_record(phone, status)


@composer_step(
    name="step_get_loan_review_result_text",
    description="读取额度审核记录中的状态文本，结果放入 data.result",
    category="backend",
)
def step_get_loan_review_result_text():
    """读取审核结果文本。"""
    return lib.step_get_loan_review_result_text()


# ---- 借款列表（初审标 / 满标待审 / 还款中） ----
@composer_step(
    name="step_open_backend_loan_menu",
    description="展开指定一级菜单下分组并进入列表页（如 借款管理/初审管理 → 初审标），iframe src 放入 data.src",
    category="backend",
    params={
        "top_menu": {"name": "一级菜单", "type": "str", "required": False,
                     "default": "借款管理", "enum": ["借款管理", "资金管理"],
                     "description": "顶部一级菜单"},
        "group": {"name": "分组名", "type": "str", "required": True,
                  "enum": ["所有借款", "初审管理", "借款中管理", "满标管理", "额度管理",
                           "债权转让", "借贷记录", "资金管理", "充值管理", "账号管理",
                           "提现管理", "收支记录", "红包管理", "手动操作", "活动结算"],
                  "description": "一级菜单下的二级分组"},
        "item_rel": {"name": "子项rel", "type": "str", "required": True,
                     "enum": ["loan/loan/list", "loan/verify/list", "loan/loaning/list",
                              "loan/full/list", "loan/fullpass/list", "loan/amount/list",
                              "loan/tender/list", "loan/repayperiod/list", "loan/recover/list",
                              "finance/change/all", "finance/change/now",
                              "finance/change/cancle", "finance/change/success",
                              "finance/account/list",
                              "finance/recharge/list", "finance/recharge/verify",
                              "finance/recharge/success", "finance/recharge/fail",
                              "member/bank/list",
                              "finance/withdraw/list", "finance/withdraw/verify",
                              "finance/withdraw/success", "finance/withdraw/fail",
                              "finance/accountlog/web", "finance/accountlog/member",
                              "finance/bountytype/list", "finance/bounty/list",
                              "loan/newRewards/list"],
                     "description": "子菜单项 iframe 路径（rel 属性）"},
    },
)
def step_open_backend_loan_menu(group, item_rel, top_menu="借款管理"):
    """进入后台列表。"""
    return lib.step_open_backend_loan_menu(group, item_rel, top_menu=top_menu)


@composer_step(
    name="step_backend_loan_list_search",
    description="在当前后台借款列表按条件搜索（手机号 / 借款标题 / 借款编号）",
    category="backend",
    params={
        "phone": {"name": "用户名", "type": "str", "required": False,
                  "default": "", "description": "按手机号搜索"},
        "title": {"name": "借款标题", "type": "str", "required": False,
                  "default": "", "description": "按标题搜索"},
        "serial_no": {"name": "借款编号", "type": "str", "required": False,
                      "default": "", "description": "按借款编号搜索"},
        "member_keyword": {"name": "会员关键字", "type": "str", "required": False,
                           "default": "",
                           "description": "资金管理列表会员搜索框（member_name/memberName）"},
    },
)
def step_backend_loan_list_search(phone="", title="", serial_no="", member_keyword=""):
    """搜索当前列表。"""
    return lib.step_backend_loan_list_search(
        phone=phone, title=title, serial_no=serial_no, member_keyword=member_keyword)


@composer_step(
    name="step_backend_loan_list_clear_search",
    description="清空当前列表搜索条件并重新搜索（恢复完整列表）",
    category="backend",
)
def step_backend_loan_list_clear_search():
    """清空搜索条件。"""
    return lib.step_backend_loan_list_clear_search()


@composer_step(
    name="step_get_backend_loan_list_info",
    description="读取当前后台借款列表信息（iframe src / 表头 / 行数 / 首行），行数放入 data.row_count",
    category="backend",
)
def step_get_backend_loan_list_info():
    """读取列表信息。"""
    return lib.step_get_backend_loan_list_info()


@composer_step(
    name="step_backend_loan_list_review",
    description="后台借款列表审核完整流程（进入列表 → 搜索 → 选首行 → 审核弹窗 → 提交通过）",
    category="backend",
    params={
        "group": {"name": "分组名", "type": "str", "required": True,
                  "enum": ["初审管理", "满标管理"],
                  "description": "列表所属分组（初审管理=初审，满标管理=复审）"},
        "item_rel": {"name": "列表rel", "type": "str", "required": True,
                     "enum": ["loan/verify/list", "loan/full/list"],
                     "description": "列表 iframe 路径"},
        "phone": {"name": "用户名", "type": "str", "required": False,
                  "default": "", "description": "按手机号搜索目标标"},
        "title": {"name": "借款标题", "type": "str", "required": False,
                  "default": "", "description": "按标题搜索目标标"},
        "serial_no": {"name": "借款编号", "type": "str", "required": False,
                      "default": "", "description": "按编号搜索目标标"},
        "note": {"name": "审核备注", "type": "str", "required": False,
                 "default": "审核OK", "description": "审核意见"},
        "img_code": {"name": "图形验证码", "type": "str", "required": False,
                     "default": "8888", "description": "固定测试图形验证码"},
        "marker": {"name": "标签", "type": "str", "required": False,
                   "default": "", "description": "初审弹窗必填「标签」字段（复审弹窗无此字段，留空跳过）"},
        "top_menu": {"name": "一级菜单", "type": "str", "required": False,
                     "default": "借款管理", "enum": ["借款管理", "资金管理"],
                     "description": "顶部一级菜单（资金审核选 资金管理）"},
        "decision": {"name": "审核结论", "type": "str", "required": False,
                     "default": "pass", "enum": ["pass", "reject"],
                     "description": "pass=通过（radio 第一项），reject=不通过（radio value=-1）"},
    },
)
def step_backend_loan_list_review(group, item_rel, phone="", title="", serial_no="",
                                  note="审核OK", img_code="8888", marker="",
                                  top_menu="借款管理", decision="pass"):
    """列表审核完整流程。"""
    return lib.step_backend_loan_list_review(
        group, item_rel,
        phone=phone, title=title, serial_no=serial_no,
        note=note, img_code=img_code, marker=marker,
        top_menu=top_menu, decision=decision,
    )


@composer_step(
    name="step_backend_audit_dialog_inspect",
    description="当前审核列表选中首行打开审核弹窗，只读校验表单（结论/备注/验证码/保存/取消）后点取消关闭，不提交、不改变数据，返回 data.before_row_count/after_row_count",
    category="backend",
)
def step_backend_audit_dialog_inspect():
    """审核弹窗只读巡检（不提交）。"""
    return lib.step_backend_audit_dialog_inspect()


@composer_step(
    name="step_backend_loan_list_requery",
    description="重新进入指定后台列表并按条件搜索（审核后状态流转核验/资金列表复查），行数放入 data.row_count",
    category="backend",
    params={
        "top_menu": {"name": "一级菜单", "type": "str", "required": False,
                     "default": "借款管理", "enum": ["借款管理", "资金管理"],
                     "description": "顶部一级菜单"},
        "group": {"name": "分组名", "type": "str", "required": True,
                  "enum": ["所有借款", "初审管理", "借款中管理", "满标管理", "额度管理",
                           "债权转让", "借贷记录", "资金管理", "充值管理", "账号管理",
                           "提现管理", "收支记录", "红包管理", "活动结算"],
                  "description": "列表所属分组"},
        "item_rel": {"name": "列表rel", "type": "str", "required": True,
                     "enum": ["loan/loan/list", "loan/verify/list", "loan/loaning/list",
                              "loan/full/list", "loan/fullpass/list", "loan/amount/list",
                              "loan/verifyfail/list", "loan/reject/list",
                              "loan/tender/list", "loan/repayperiod/list", "loan/recover/list",
                              "finance/change/all", "finance/change/now",
                              "finance/change/cancle", "finance/change/success",
                              "finance/account/list",
                              "finance/recharge/list", "finance/recharge/verify",
                              "finance/recharge/success", "finance/recharge/fail",
                              "member/bank/list",
                              "finance/withdraw/list", "finance/withdraw/verify",
                              "finance/withdraw/success", "finance/withdraw/fail",
                              "finance/accountlog/web", "finance/accountlog/member",
                              "finance/bountytype/list", "finance/bounty/list",
                              "loan/newRewards/list"],
                     "description": "列表 iframe 路径"},
        "phone": {"name": "用户名", "type": "str", "required": False,
                  "default": "", "description": "按手机号搜索"},
        "title": {"name": "借款标题", "type": "str", "required": False,
                  "default": "", "description": "按标题搜索"},
        "serial_no": {"name": "借款编号", "type": "str", "required": False,
                      "default": "", "description": "按编号搜索"},
        "member_keyword": {"name": "会员关键字", "type": "str", "required": False,
                           "default": "", "description": "资金管理列表会员搜索框"},
    },
)
def step_backend_loan_list_requery(group, item_rel, phone="", title="", serial_no="",
                                   top_menu="借款管理", member_keyword=""):
    """复查列表。"""
    return lib.step_backend_loan_list_requery(
        group, item_rel,
        phone=phone, title=title, serial_no=serial_no,
        top_menu=top_menu, member_keyword=member_keyword,
    )
