# Copyright (C) 2026. All rights reserved.
"""前台充值页面（汇付托管模拟通道）。"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL


class RechargePage(BasePage):
    """充值页：选通道 / 输金额 / 输验证码 / 提交。"""

    __page_url = BASE_URL + "/finance/recharge/index"

    __money_input = (By.ID, "money")
    __valicode_input = (By.ID, "valicode")

    # 提交控件候选定位器。
    # 实测充值表单 form[name=reForm] 内真实提交控件为
    # ``input.recharge[type=submit]``（ng-click="rechargeSubmit()"，
    # value 为带空格的「充  值」）。
    # 注意两个陷阱：
    # 1. 左侧导航文本「充值」的 <a> href 即当前页，点它只触发 GET 重载；
    # 2. #right-tool-form 是隐藏的借款计算器，其 submit 为「开始计算」。
    __submit_candidates = (
        (By.CSS_SELECTOR, 'form[name="reForm"] input[type=submit].recharge'),
        (By.CSS_SELECTOR, "input.recharge[type=submit]"),
        (By.CSS_SELECTOR, 'form[name="reForm"] input[type=submit]'),
        (By.CSS_SELECTOR, "button.btnbgorange"),
        (By.CSS_SELECTOR, "input.btnbgorange"),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
    )

    # 页面提示/错误文案候选容器（提交后失败诊断用）
    __message_candidates = (
        (By.CSS_SELECTOR, ".validation-invalid"),
        (By.CSS_SELECTOR, "[class*='error']"),
        (By.CSS_SELECTOR, "[class*='tip']"),
    )

    def open_url(self):
        """打开充值页面"""
        self.driver.get(self.__page_url)

    def select_payment_type(self, payment_type="chinapnrTrust"):
        """选择充值通道 radio（value=chinapnrTrust 为站点唯一通道，默认选中）"""
        locator = (By.XPATH, f'//input[@name="paymentType" and @value="{payment_type}"]')
        self.base_click_special(locator)

    def input_money(self, amount):
        """输入充值金额"""
        self.base_input(self.__money_input, str(amount))

    def input_valicode(self, valicode):
        """输入图形验证码（教学环境固定 8888）"""
        self.base_input(self.__valicode_input, str(valicode))

    def click_submit(self):
        """点击提交按钮（候选定位器逐个尝试，等待任一可见后点击）"""
        element = WebDriverWait(self.driver, self.default_timeout).until(
            lambda d: self._find_first_visible(self.__submit_candidates)
        )
        element.click()

    def get_page_message(self):
        """读取页面提示/错误文案（拼接候选容器中的非空文本，用于失败诊断）。"""
        texts = []
        for by, value in self.__message_candidates:
            try:
                for element in self.driver.find_elements(by, value):
                    text = (element.text or "").strip()
                    if text and text not in texts:
                        texts.append(text)
            except Exception:
                continue
        return " | ".join(texts)

    def _find_first_visible(self, candidates):
        """在候选定位器中找第一个可见元素，找不到返回 None。"""
        for by, value in candidates:
            try:
                for element in self.driver.find_elements(by, value):
                    if element.is_displayed():
                        return element
            except Exception:
                continue
        return None
