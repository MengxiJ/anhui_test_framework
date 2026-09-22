# Copyright (C) 2026. All rights reserved.
"""账户管理杂项页：积分 / 安全设置 / 银行卡 / 推广 / 站内消息。

实测 URL 与关键区块：

- 积分记录 ``/member/credit/index``：区块标题「我的积分记录」（当前空态）；
- 安全设置 ``/member/member/safe``：标题「安全设置」+ 手机验证/邮箱认证/密码修改三区块；
- 银行卡信息 ``/member/funds/bank``：标题「银行卡信息」，未绑卡含温馨提示；
- 我的推广 ``/member/spread/myspread``：标题「推广管理」，含 username 搜索；
- 站内消息 ``/member/message/index``：站内信息列表，顶栏链接含未读数，
  页面标题/标签文本形如「站内信息(N)」。
"""
from __future__ import annotations

import re
import time
from typing import Dict, List, Optional

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

# page key -> (相对路径, 关键区块标题)
_PAGE_SPECS = {
    "credit": ("/member/credit/index", "我的积分记录"),
    "safe": ("/member/member/safe", "安全设置"),
    "bank": ("/member/funds/bank", "银行卡信息"),
    "spread": ("/member/spread/myspread", "推广管理"),
}

_MESSAGE_URL = BASE_URL + "/member/message/index"
# 顶栏未读数链接为相对 href（a.msg 文本即数字），侧栏菜单链接为绝对 href（文本无数字）
_MESSAGE_LINK_CSS = ('a.msg[href*="message/index"], '
                     'a[href*="/member/message/index"]')
_MSG_TITLE_CSS = "table tbody tr a.msg-read"
_MSG_UNREAD_CSS = "table tbody tr a.msg-read:not(.readed)"
# 读信后内联展开的详情区（站点源码 class 拼写为 sys-msg-detai）
_MSG_DETAIL_CSS = "div.sys-msg-detai"
# 页面级未读数文本（如 站内信息(8) / 站内信（8） / 未读信息 8）
_PAGE_COUNT_RE = re.compile(r"(?:站内信[息]?|未读信?息?)[^0-9]{0,6}(\d+)")
_DIGIT_RE = re.compile(r"\d+")


class MemberMiscPage(BasePage):
    """账户管理杂项页面对象（积分 / 安全 / 银行卡 / 推广）。"""

    def open_page(self, page: str) -> str:
        """按 page key 打开对应页面，返回最终 URL（可能被重定向）。"""
        spec = _PAGE_SPECS.get(page)
        if spec is None:
            raise ValueError(f"未知账户管理页面: {page}")
        self.driver.get(BASE_URL + spec[0])
        return self.driver.current_url

    def page_spec(self, page: str) -> Dict[str, str]:
        """返回页面规格（路径与关键区块标题）。"""
        path, head = _PAGE_SPECS[page]
        return {"path": path, "expected_head": head}

    def has_heading(self, expected_head: str) -> bool:
        """页面是否包含指定关键区块标题（h1-h4/td/legend/strong/b/span/a/div 文本精确包含）。"""
        try:
            return bool(
                self.driver.execute_script(
                    "var kw = arguments[0];"
                    "var cand = document.querySelectorAll("
                    "'h1,h2,h3,h4,h5,legend,td,th,strong,b,span,a,div,label');"
                    "for (var i = 0; i < cand.length; i++) {"
                    "  var t = (cand[i].textContent || '').trim();"
                    "  if (t && t.length <= 30 && t.indexOf(kw) >= 0) { return true; }"
                    "}"
                    "return false;",
                    expected_head,
                )
            )
        except Exception:  # noqa: BLE001 - 渲染竞态按不存在处理
            return False

    def read_page_info(self, page: str) -> Dict[str, object]:
        """打开页面并读取最终 URL、关键区块是否存在、空态提示是否存在。"""
        final_url = self.open_page(page)
        expected_head = _PAGE_SPECS[page][1]
        head_present = self.has_heading(expected_head)
        body_text = self._body_text()
        empty_state = ("暂无" in body_text) or ("温馨提示" in body_text)
        return {
            "page": page,
            "final_url": final_url,
            "expected_head": expected_head,
            "head_present": head_present,
            "empty_state": empty_state,
        }

    def _body_text(self) -> str:
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:  # noqa: BLE001
            return ""


class MessagePage(BasePage):
    """站内消息页面对象。"""

    def open_url(self) -> str:
        """打开站内消息页，返回最终 URL。"""
        self.driver.get(_MESSAGE_URL)
        return self.driver.current_url

    def read_topbar_unread(self) -> int:
        """读取顶栏站内消息角标中的未读数（无数字返回 0）。

        角标数字由接口异步渲染（进入消息页瞬间为空），轮询等待其出现。
        """
        for _ in range(20):
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, _MESSAGE_LINK_CSS)
            except Exception:  # noqa: BLE001
                links = []
            for link in links:
                match = _DIGIT_RE.fullmatch((link.text or "").strip())
                if match:
                    return int(match.group())
            time.sleep(0.5)
        return 0

    def read_page_unread(self) -> Optional[int]:
        """读取页面级未读数（标题/标签文本中的数字，识别不到返回 None）。"""
        try:
            text = self.driver.execute_script(
                r"""
                var cand = document.querySelectorAll(
                    'h1,h2,h3,h4,h5,legend,td,th,strong,b,span,a,label,li');
                var best = '';
                for (var i = 0; i < cand.length; i++) {
                    var t = (cand[i].textContent || '').trim();
                    if (t && t.length <= 30 && t.indexOf('信') >= 0) {
                        if (/\d/.test(t)) { return t; }
                        if (!best) { best = t; }
                    }
                }
                return best;
                """
            ) or ""
        except Exception:  # noqa: BLE001
            return None
        match = _PAGE_COUNT_RE.search(str(text))
        if match:
            return int(match.group(1))
        return None

    def read_message_info(self, center_unread: Optional[int] = None) -> Dict[str, object]:
        """打开消息页并汇总：顶栏未读数、页面级未读数、进入前中心未读数。"""
        final_url = self.open_url()
        return {
            "final_url": final_url,
            "topbar_unread": self.read_topbar_unread(),
            "page_unread": self.read_page_unread(),
            "center_unread": center_unread,
        }

    # ---- 读信业务链 ----
    def read_list_rows(self) -> List[Dict[str, object]]:
        """读取当前消息列表行：[{title, unread}]。

        标题链接 class 含 readed 表示已读（站点 ng-class 规则：status!='1' 已读）。
        """
        rows: List[Dict[str, object]] = []
        for a in self.driver.find_elements(By.CSS_SELECTOR, _MSG_TITLE_CSS):
            cls = a.get_attribute("class") or ""
            rows.append({
                "title": (a.text or "").strip(),
                "unread": "readed" not in cls,
            })
        return rows

    def read_list_unread_count(self) -> int:
        """当前列表页未读消息条数（class 不含 readed 的标题链接数）。"""
        return len(self.driver.find_elements(By.CSS_SELECTOR, _MSG_UNREAD_CSS))

    def read_list_info(self) -> Dict[str, object]:
        """打开消息列表页并汇总：顶栏未读数、列表条数、未读条数、首封未读标题。"""
        final_url = self.open_url()
        time.sleep(2)
        rows = self.read_list_rows()
        first_unread = next((r["title"] for r in rows if r["unread"]), "")
        return {
            "final_url": final_url,
            "topbar_unread": self.read_topbar_unread(),
            "row_count": len(rows),
            "list_unread": sum(1 for r in rows if r["unread"]),
            "first_unread_title": first_unread,
            "rows": rows,
        }

    def open_first_unread(self) -> Dict[str, object]:
        """点开列表中第一封未读消息（页内内联展开详情，不跳转、不弹层）。

        返回 opened/title/detail_text/topbar_before/topbar_after；
        无未读消息时 opened=False。
        """
        topbar_before = self.read_topbar_unread()
        unread = self.driver.find_elements(By.CSS_SELECTOR, _MSG_UNREAD_CSS)
        if not unread:
            return {
                "opened": False, "title": "", "detail_text": "",
                "topbar_before": topbar_before,
                "topbar_after": topbar_before,
                "topbar_delta": 0,
            }
        title = (unread[0].text or "").strip()
        self.driver.execute_script("arguments[0].click();", unread[0])
        # 轮询等待内联详情区展开（class 为站点源码拼写 sys-msg-detai）。
        # 页面可能存在多个同名容器（含工具栏残留文本），只认同时包含标题与
        # 「发件时间」的元素，多个命中时取文本最长者。
        detail_text = ""
        for _ in range(10):
            time.sleep(0.5)
            dets = self.driver.find_elements(By.CSS_SELECTOR, _MSG_DETAIL_CSS)
            candidates = [
                (d.text or "").strip()
                for d in dets
                if d.is_displayed()
                and title in (d.text or "")
                and "发件时间" in (d.text or "")
            ]
            if candidates:
                detail_text = max(candidates, key=len)
                break
        topbar_after = self.read_topbar_unread()
        return {
            "opened": True,
            "title": title,
            "detail_text": detail_text,
            "topbar_before": topbar_before,
            "topbar_after": topbar_after,
            "topbar_delta": topbar_before - topbar_after,
        }

    def read_list_info_after_read(self, before_list_unread: int) -> Dict[str, object]:
        """读信后重新打开列表，对比未读条数变化（before_list_unread 为读信前快照）。"""
        info = self.read_list_info()
        info["list_unread_before"] = before_list_unread
        info["list_unread_after"] = info["list_unread"]
        info["list_unread_delta"] = before_list_unread - int(info["list_unread"])
        return info
