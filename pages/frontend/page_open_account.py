from selenium.webdriver.common.by import By
from base.page_base import BasePage
from config import NAME, CARD


class OpenAccountPage(BasePage):
    """开通托管资金账号页面 - 资金托管功能"""

    __click_open = (By.LINK_TEXT, "立即开通")
    __real_name = (By.NAME, "realname")
    __id_card = (By.NAME, "card_id")
    __confirm_btn = (By.CSS_SELECTOR, '[value="确认提交"]')
    __act_now = (By.CSS_SELECTOR, ".btn.ng-scope")
    __success_text = (By.CSS_SELECTOR, "body")
    __fail_text = (By.CLASS_NAME, "validation-invalid")

    def __init__(self, driver):
        """初始化托管账号页面"""
        super().__init__(driver)

    def click_account(self):
        """点击立即开通"""
        self.base_click(self.__click_open)

    def input_real_name(self, real_name=NAME):
        """输入真实姓名"""
        self.base_input(self.__real_name, real_name)

    def input_id_card(self, id_card=CARD):
        """输入身份证号"""
        self.base_input(self.__id_card, id_card)

    def click_confirm(self):
        """点击确认提交"""
        self.base_click(self.__confirm_btn)

    def click_act_now(self):
        """点击确认开通"""
        self.base_click(self.__act_now)

    def get_result_success_text(self):
        """获取开通成功结果文本"""
        return self.base_switch_handle(self.__success_text).text

    def get_result_fail_text(self):
        """获取开通失败结果文本"""
        return self.fd_element(self.__fail_text).text

    def open_account(self, real_name=NAME, id_card=CARD, expect_success=True):
        """执行开通托管资金账号操作"""
        self.click_account()
        self.input_real_name(real_name)
        self.input_id_card(id_card)
        self.click_confirm()
        if expect_success:
            self.click_act_now()
