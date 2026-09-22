# Copyright (C) 2026. All rights reserved.
import time

from selenium.webdriver.common.by import By

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL


class BorrowPublishPage(BasePage):
    """前台借款发标页（品质理财 → 个人借款 → 立即借款 → loanview 表单）。"""

    __front_url = BASE_URL
    __wait_time = 2

    __borrow_now = (By.CSS_SELECTOR, "a.borrow-now")
    __form = (By.ID, "borrowPublish")
    __person_radio = (By.CSS_SELECTOR, "#borrowPublish input[value='-1']")
    __title = (By.CSS_SELECTOR, "#borrowPublish input[name='name']")
    __use = (By.CSS_SELECTOR, "#borrowPublish select[name='use']")
    __amount = (By.CSS_SELECTOR, "#borrowPublish input[name='amount']")
    __apr = (By.CSS_SELECTOR, "#borrowPublish input[name='apr']")
    __repay_type = (By.CSS_SELECTOR, "#borrowPublish select[name='repay_type']")
    __period = (By.CSS_SELECTOR, "#borrowPublish select[name='period']")
    __validate = (By.CSS_SELECTOR, "#borrowPublish select[name='validate']")
    __tender_min = (By.ID, "tender_amount_min")
    __tender_max = (By.ID, "tender_amount_max")
    __contents = (By.ID, "borrow_contents")
    __valicode = (By.CSS_SELECTOR, "#borrowPublish input[name='valicode']")
    __submit = (By.ID, "borrowForm")
    __body = (By.TAG_NAME, "body")

    def __init__(self, driver):
        super().__init__(driver)

    def open_loan_index(self):
        """打开「品质理财 → 个人借款」页。"""
        self.driver.get(self.__front_url.rstrip("/") + "/loan/loan/index")
        time.sleep(self.__wait_time)

    def click_borrow_now(self, index: int = 0):
        """点击第 index 张标种卡「立即借款」，进入 loanview 发标表单。"""
        buttons = self.driver.find_elements(*self.__borrow_now)
        if not buttons:
            raise RuntimeError("个人借款页未找到「立即借款」入口")
        buttons[min(index, len(buttons) - 1)].click()
        self.fd_element(self.__submit)  # 等待表单出现
        time.sleep(self.__wait_time)

    def fill_publish_form(
        self,
        title: str,
        use: str = "周转",
        amount: str = "200",
        apr: str = "5",
        repay_type: str = "等额本息",
        period: str = "1个月",
        validate: str = "3天",
        tender_min: str = "50元",
        tender_max: str = "不限",
        contents: str = "自动化测试借款标，到期还本付息。",
        valicode: str = "8888",
    ):
        """填写发标表单（不提交）。"""
        self.base_click_special(self.__person_radio)
        self.base_input(self.__title, title)
        self.base_select_list(self.__use, use)
        self.base_input(self.__amount, amount)
        self.base_input(self.__apr, apr)
        self.base_select_list(self.__repay_type, repay_type)
        self.base_select_list(self.__period, period)
        self.base_select_list(self.__validate, validate)
        self.base_select_list(self.__tender_min, tender_min)
        self.base_select_list(self.__tender_max, tender_max)
        self.base_input(self.__contents, contents)
        self.base_input(self.__valicode, valicode)

    def submit_publish(self):
        """提交发标表单。"""
        self.base_click(self.__submit)
        time.sleep(self.__wait_time + 1)

    def get_publish_result_text(self) -> str:
        """读取提交后页面文本（用于校验发布结果/错误提示）。"""
        time.sleep(self.__wait_time)
        return self.fd_element(self.__body).text
