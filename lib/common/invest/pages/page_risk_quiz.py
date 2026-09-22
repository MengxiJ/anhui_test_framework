# Copyright (C) 2026. All rights reserved.
"""风险测评答题页（/risk/answer/record）。

实测交互流：

1. 打开页面后先弹出「风险提示」xubox 模态框（内嵌只读 iframe ``/risk/answer/subject``，
   遮罩 ``#xubox_shade1`` 会拦截主文档点击），须先点击右上角关闭 ``a.xubox_close``；
2. 主文档为 10 道单选题表单（``form action=/risk/answer/record``），
   每题 radio 的 ``name`` 为题号 ``1``~``10``，选项数量各题不等；
3. 提交按钮为 ``input.btnbgoragne``（注意站点 class 拼写为 bgoragne，
   ``ng-click="ansSubmit()"``），提交成功后整页跳转 ``/risk/answer/introduce``。

已测评用户重新打开 record 页仍显示答题表单（可重新测评），
故「record 显示表单」不能作为未测评判据，测评状态以等级文本为准。
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL

QUESTION_COUNT = 10


class RiskQuizPage(BasePage):
    """风险测评答题页面对象。"""

    __quiz_url = BASE_URL + "/risk/answer/record"
    # xubox「风险提示」模态框关闭按钮（右上角 X）
    __modal_close = (By.CSS_SELECTOR, "a.xubox_close")
    # 每题 radio：name=题号
    __question_radio_fmt = 'input[type=radio][name="{qid}"]'
    # 提交按钮（站点 class 拼写为 btnbgoragne）
    __submit_candidates = (
        (By.CSS_SELECTOR, "input.btnbgoragne"),
        (By.CSS_SELECTOR, 'input[type=submit][value="提交"]'),
        (By.CSS_SELECTOR, "input[type=submit]"),
    )

    def open_url(self) -> None:
        """打开测评答题页。"""
        self.driver.get(self.__quiz_url)

    def close_risk_modal(self, timeout: float = 3.0) -> bool:
        """关闭打开页时的「风险提示」xubox 模态框（未弹出返回 False）。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                close_btns = self.driver.find_elements(*self.__modal_close)
                if close_btns:
                    self.driver.execute_script("arguments[0].click();", close_btns[0])
                    time.sleep(0.5)
                    return True
            except Exception:  # noqa: BLE001 - 模态框渲染中，轮询重试
                pass
            time.sleep(0.3)
        return False

    def answer_quiz(self, answers: Optional[List[int]] = None) -> Dict[str, Any]:
        """逐题作答。

        Args:
            answers: 每题选项索引（0 起）列表，长度应为 10；None 时每题选第一项。
                未提供的题号按第一项作答。

        Returns:
            {"answered": [题号...], "options": {题号: 选项索引}, "missing": [题号...]}
        """
        plan: Dict[int, int] = {}
        for qid in range(1, QUESTION_COUNT + 1):
            default = 0
            if answers and len(answers) >= qid and answers[qid - 1] is not None:
                default = int(answers[qid - 1])
            plan[qid] = default

        answered: List[int] = []
        options: Dict[str, int] = {}
        for qid, opt_index in plan.items():
            selector = self.__question_radio_fmt.format(qid=qid)
            radios = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if not radios:
                continue
            index = min(max(opt_index, 0), len(radios) - 1)
            radios[index].click()  # 原生 click 触发完整事件链（AngularJS 模型同步）
            answered.append(qid)
            options[str(qid)] = index
        missing = [q for q in range(1, QUESTION_COUNT + 1) if q not in answered]
        return {"answered": answered, "options": options, "missing": missing}

    def click_submit(self) -> None:
        """点击提交按钮（候选定位器依次尝试，点击失败抛异常由上层判定）。"""
        last_error: Optional[Exception] = None
        for by, value in self.__submit_candidates:
            try:
                btns = self.driver.find_elements(by, value)
                visible = next((b for b in btns if b.is_displayed()), None)
                if visible:
                    visible.click()
                    return
            except Exception as exc:  # noqa: BLE001 - 候选逐个尝试
                last_error = exc
        raise RuntimeError(f"测评提交按钮不可用（最后错误: {last_error}）")

    def is_on_introduce(self) -> bool:
        """当前是否已跳转到测评介绍/结果页。"""
        return "risk/answer/introduce" in str(self.driver.current_url)

    def get_level_text(self) -> Optional[str]:
        """读取页面上「风险测评等级」后的等级文本（无则 None）。

        等级可能位于标签元素的兄弟/父级节点（如「客户风险测评等级 ： 稳健型」），
        先按叶子元素匹配，再回退到含关键字的容器文本。
        """
        try:
            return self.driver.execute_script(
                "var els = document.querySelectorAll('*');"
                "for (var i = 0; i < els.length; i++) {"
                "    var t = (els[i].textContent || '').trim();"
                "    if (t.indexOf('风险测评等级') >= 0) {"
                "        var clean = t.replace(/\\s+/g, '');"
                "        if (clean.length <= 40) { return clean; }"
                "    }"
                "}"
                "return null;"
            )
        except Exception:  # noqa: BLE001 - 页面跳转中读取失败按无等级处理
            return None
