# Copyright (C) 2026. All rights reserved.
"""会员中心页（/member/member/center）。

实测结构：

- 余额文本形如 ``78,000.00元``，出现在含「账户余额/可用余额」的小文本容器中；
- 「最近交易/最新交易」区块：小标题 + 交易记录表格；
- 顶栏未读消息数：``a[href*="/member/message/index"]`` 的文本（如 ``8``，
  未读为 0 时可能没有数字文本）；
- 已测评用户页面含「风险测评等级」文本。
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, Optional

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# 余额数字文本（如 78,000.00），上下文含「账户余额/可用余额」
_BALANCE_RE = re.compile(r"([\d,\.]+)\s*元")

# 会员中心余额结构：<div class="raw1"><p><em ng-bind>78,000.00</em>元</p>
# <p>账户余额</p></div>。余额数字由 AngularJS ng-bind 异步渲染，须先定位
# 文本恰为「账户余额」的叶子元素，再读其父容器，并轮询等待数字出现。
_BALANCE_TEXT_JS = (
    "var all = document.querySelectorAll('*');"
    "for (var i = 0; i < all.length; i++) {"
    "    var el = all[i];"
    "    var t = (el.textContent || '').trim();"
    "    if (t === '账户余额' && !el.children.length) {"
    "        var p = el.parentElement;"
    "        return p ? (p.textContent || '').trim() : t;"
    "    }"
    "}"
    "return null;"
)
# 兜底：容器包含「可用余额」文本（部分页面布局文案不同）
_BALANCE_CONTAINS_JS = (
    "var els = document.querySelectorAll('*');"
    "for (var i = 0; i < els.length; i++) {"
    "    var t = (els[i].textContent || '').trim();"
    "    if ((t.indexOf('账户余额') >= 0 || t.indexOf('可用余额') >= 0)"
    "        && t.length <= 60) { return t; }"
    "}"
    "return '';"
)

# 读取「最近交易/最新交易」区块表格的 JS（找不到区块时 found=False）
_READ_RECENT_TX_JS = (
    "function readTable(tbl) {"
    "    var headers = [];"
    "    var headRow = tbl.querySelector('thead tr') || tbl.querySelector('tr');"
    "    if (headRow) {"
    "        var cells = headRow.querySelectorAll('th,td');"
    "        for (var j = 0; j < cells.length; j++) {"
    "            var t = (cells[j].textContent || '').trim();"
    "            if (t) { headers.push(t); }"
    "        }"
    "    }"
    "    var rows = [];"
    "    var trs = tbl.querySelectorAll('tr');"
    "    for (var i = 0; i < trs.length; i++) {"
    "        var tds = trs[i].querySelectorAll('td');"
    "        if (!tds.length) { continue; }"
    "        var row = [];"
    "        var has = false;"
    "        for (var j = 0; j < tds.length; j++) {"
    "            var t = (tds[j].textContent || '').trim();"
    "            row.push(t);"
    "            if (t) { has = true; }"
    "        }"
    "        if (has) { rows.push(row); }"
    "    }"
    "    return {headers: headers, rows: rows};"
    "}"
    "function headerTextOf(tbl) {"
    "    var headRow = tbl.querySelector('thead tr') || tbl.querySelector('tr');"
    "    if (!headRow) { return ''; }"
    "    var cells = headRow.querySelectorAll('th,td');"
    "    var parts = [];"
    "    for (var j = 0; j < cells.length; j++) {"
    "        var tt = (cells[j].textContent || '').trim();"
    "        if (tt) { parts.push(tt); }"
    "    }"
    "    return parts.join('|');"
    "}"
    # 主路径：按表头特征选交易表（实测表头=时间/类型/存入/支出/冻结/解冻/余额/备注）。
    # 必须排除同页「资产/占比」资产分布表——其导航中也含「交易记录」链接，
    # 按标题向上找表会误选到它。
    "var tables = document.querySelectorAll('table');"
    "var tbl = null;"
    "for (var i = 0; i < tables.length; i++) {"
    "    var ht = headerTextOf(tables[i]);"
    "    if (ht.indexOf('时间') >= 0 && ht.indexOf('类型') >= 0"
    "        && (ht.indexOf('存入') >= 0 || ht.indexOf('支出') >= 0 || ht.indexOf('余额') >= 0)"
    "        && !(ht.indexOf('资产') >= 0 && ht.indexOf('占比') >= 0)) {"
    "        tbl = tables[i]; break;"
    "    }"
    "}"
    # 兜底路径：按区块标题向上找表（布局变体）
    "if (!tbl) {"
    "    var keywords = ['最近交易', '最新交易', '交易记录'];"
    "    var heading = null;"
    "    var cand = document.querySelectorAll('h1,h2,h3,h4,h5,span,b,strong,td,th,dt,em,p,label,a,div');"
    "    for (var i = 0; i < cand.length && !heading; i++) {"
    "        var t = (cand[i].textContent || '').trim();"
    "        if (t && t.length <= 20) {"
    "            for (var k = 0; k < keywords.length; k++) {"
    "                if (t.indexOf(keywords[k]) >= 0) { heading = cand[i]; break; }"
    "            }"
    "        }"
    "    }"
    "    if (heading) {"
    "        var node = heading;"
    "        for (var d = 0; d < 8 && node; d++) {"
    "            node = node.parentElement;"
    "            if (!node || !node.querySelector) { break; }"
    "            if (node.querySelector('table')) { tbl = node.querySelector('table'); break; }"
    "        }"
    "    }"
    "}"
    "if (!tbl) { return {headers: [], rows: [], found: false}; }"
    "var data = readTable(tbl);"
    "data.found = true;"
    "return data;"
)


class MemberCenterPage(BasePage):
    """会员中心总览页面对象。"""

    __center_url = BASE_URL + "/member/member/center"
    # 顶栏未读数链接为相对 href（a.msg 文本即数字），侧栏菜单链接为绝对 href（文本无数字）
    __message_link = (By.CSS_SELECTOR,
                      'a.msg[href*="message/index"], a[href*="/member/message/index"]')

    def open_url(self) -> None:
        """打开会员中心页。"""
        self.driver.get(self.__center_url)

    # ---- 余额 ----
    def read_balance_text(self, timeout: float = 10.0) -> Optional[float]:
        """读取账户余额并转为 float（轮询等待 ng-bind 数字渲染，失败返回 None）。"""
        raw = self._extract_balance_text(timeout=timeout)
        if not raw:
            return None
        try:
            return float(raw.replace(",", ""))
        except ValueError:
            return None

    def _extract_balance_text(self, timeout: float = 10.0) -> str:
        """轮询读取余额容器文本并提取数字部分（如 78,000.00）。

        优先用「账户余额」叶子元素定位父容器；超时后用包含匹配兜底一次。
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                text = self.driver.execute_script(_BALANCE_TEXT_JS)
                if text and any(ch.isdigit() for ch in str(text)):
                    match = _BALANCE_RE.search(str(text))
                    if match:
                        return match.group(1)
            except Exception:  # noqa: BLE001 - 渲染中 JS 可能读不到，轮询重试
                pass
            time.sleep(0.5)
        # 兜底：包含匹配（页面布局文案差异）
        try:
            text = self.driver.execute_script(_BALANCE_CONTAINS_JS) or ""
        except Exception:  # noqa: BLE001
            text = ""
        match = _BALANCE_RE.search(str(text))
        return match.group(1) if match else ""

    # ---- 最近交易 ----
    def read_recent_transactions(self, timeout: float = 8.0) -> Dict[str, Any]:
        """读取「最近交易/最新交易」区块表格（轮询等待区块渲染，找不到时空态）。"""
        deadline = time.time() + timeout
        data: Dict[str, Any] = {}
        while time.time() < deadline:
            try:
                data = self.driver.execute_script(_READ_RECENT_TX_JS) or {}
            except Exception:  # noqa: BLE001 - 渲染竞态读取失败后重试
                data = {}
            if data.get("found"):
                break
            time.sleep(0.5)
        headers = [str(h) for h in (data.get("headers") or [])]
        rows = [[str(c) for c in row] for row in (data.get("rows") or [])]
        joined = " ".join(" ".join(row) for row in rows)
        body_hint = self._body_has_empty_hint()
        empty_state = (not data.get("found")) or ("暂无" in joined) or (not rows and body_hint)
        return {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
            "empty_state": empty_state,
        }

    def _body_has_empty_hint(self) -> bool:
        """页面是否含空态提示文案（暂无记录/暂无数据）。"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:  # noqa: BLE001
            return False
        return ("暂无" in body) or ("暂无记录" in body)

    # ---- 顶栏未读消息数 ----
    def read_unread_count(self) -> int:
        """读取顶栏未读消息角标数（纯数字链接文本转 int，无数字返回 0）。

        角标数字由接口异步渲染，轮询等待其出现；侧栏「站内消息」菜单
        文本非纯数字，不会误匹配。
        """
        for _ in range(20):
            try:
                links = self.driver.find_elements(*self.__message_link)
            except Exception:  # noqa: BLE001
                links = []
            for link in links:
                match = re.fullmatch(r"\s*(\d+)\s*", link.text or "")
                if match:
                    return int(match.group(1))
            time.sleep(0.5)
        return 0

    # ---- 汇总 ----
    def read_center_info(self) -> Dict[str, Any]:
        """汇总读取：余额文本/数值、未读消息数、页面是否含「风险测评等级」。"""
        balance_text = self._extract_balance_text()
        balance = None
        if balance_text:
            try:
                balance = float(balance_text.replace(",", ""))
            except ValueError:
                balance = None
        return {
            "balance_text": balance_text,
            "balance": balance,
            "unread_count": self.read_unread_count(),
            "risk_level_present": self._has_risk_level_text(),
        }

    def _has_risk_level_text(self) -> bool:
        """页面是否含「风险测评等级」文本。"""
        try:
            return bool(
                self.driver.execute_script(
                    "var els = document.querySelectorAll('*');"
                    "for (var i = 0; i < els.length; i++) {"
                    "    var t = (els[i].textContent || '').trim();"
                    "    if (t.indexOf('风险测评等级') >= 0"
                    "        && t.replace(/\\s+/g, '').length <= 40) { return true; }"
                    "}"
                    "return false;"
                )
            )
        except Exception:  # noqa: BLE001
            return False
