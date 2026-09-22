# Copyright (C) 2026. All rights reserved.
"""前台资金记录页面：充值记录 + 交易明细（筛选交互）。"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from lib.core.page_base import BasePage
from lib.core.project_config import BASE_URL


class RechargeLogPage(BasePage):
    """充值记录页（订单号/支付方式/充值金额/充值时间/状态/管理备注）。"""

    __page_url = BASE_URL + "/finance/recharge/log"

    def open_url(self):
        """打开充值记录页"""
        self.driver.get(self.__page_url)


class AccountLogPage(BasePage):
    """交易明细页（交易分类筛选 + 日期区间筛选）。"""

    __page_url = BASE_URL + "/finance/accountlog/index"

    __start_time = (By.ID, "startTime")
    __end_time = (By.ID, "endTime")

    # 交易分类下拉候选定位器（实测无 name/id，class=sm-select search；选项文本如“充值成功”）
    __type_select_candidates = (
        (By.CSS_SELECTOR, "select[name='type']"),
        (By.ID, "type"),
        (By.CSS_SELECTOR, "select.sm-select"),
        (By.CSS_SELECTOR, "select"),
    )

    # 筛选按钮候选定位器
    __filter_btn_candidates = (
        (By.XPATH, '//button[contains(normalize-space(.), "筛选")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "筛选")]'),
        (By.XPATH, '//input[@value="筛选"]'),
        (By.XPATH, '//button[contains(normalize-space(.), "搜索")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "搜索")]'),
    )

    def open_url(self):
        """打开交易明细页"""
        self.driver.get(self.__page_url)

    def select_log_type(self, text):
        """按可见文本选择交易分类。

        实测选项为长文案（如传入「充值」，实际选项文本为「充值成功」），
        因此精确匹配失败时回退到首个文本包含传入值的选项。
        """
        element = self._find_first_visible(self.__type_select_candidates)
        if element is None:
            raise ValueError("未找到交易分类下拉框")
        target = str(text)
        select = Select(element)
        try:
            select.select_by_visible_text(target)
            return
        except Exception:
            pass
        for option in select.options:
            option_text = (option.text or "").strip()
            if target and target in option_text:
                select.select_by_visible_text(option_text)
                return
        raise ValueError(f"交易分类下拉中无匹配选项: {target}")

    def input_date_range(self, start_date=None, end_date=None):
        """输入日期区间（格式 YYYY-MM-DD，None/空跳过对应项）"""
        if start_date:
            self.base_input(self.__start_time, str(start_date))
        if end_date:
            self.base_input(self.__end_time, str(end_date))

    def click_filter(self):
        """点击筛选按钮"""
        element = self._find_first_visible(self.__filter_btn_candidates)
        if element is None:
            raise ValueError("未找到筛选按钮")
        element.click()

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
