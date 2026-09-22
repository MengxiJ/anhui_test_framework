from selenium.webdriver.common.by import By
from base.page_base import BasePage


class CreditApplicationPage(BasePage):
    """额度申请页面 - 借款额度申请功能"""
    
    __switch_account = (By.XPATH, "//em[text()='借款账户']")
    __account_apply = (By.LINK_TEXT, "申请额度")
    __amount = (By.ID, "amount_account")
    __detail_msg = (By.NAME, "remark")
    __img_code = (By.ID, "verifycode")
    __confirm_btn = (By.CSS_SELECTOR, ".btn-submit.btn-md")
    __success_text = (By.XPATH, '//*[@id="amount_list"]/tr[1]/td[3]')
    __fail_text = (By.XPATH, '//label[@class="error"]')

    def __init__(self, driver):
        """初始化额度申请页面"""
        super().__init__(driver)

    def click_switch_account(self):
        """点击切换账户"""
        self.base_click(self.__switch_account)

    def click_account_apply(self):
        """点击申请额度"""
        self.base_click(self.__account_apply)

    def input_amount(self, amount):
        """输入申请额度"""
        self.base_input(self.__amount, amount)

    def input_detail_msg(self, msg):
        """输入申请详情"""
        self.base_input(self.__detail_msg, msg)

    def input_img_code(self, img_code):
        """输入图片验证码"""
        self.base_input(self.__img_code, img_code)

    def click_confirm(self):
        """点击确认按钮"""
        self.base_click(self.__confirm_btn)

    def credit_application(self, amount, msg, img_code="8888"):
        """执行额度申请操作"""
        self.click_switch_account()
        self.click_account_apply()
        self.input_amount(amount)
        self.input_detail_msg(msg)
        self.input_img_code(img_code)
        self.click_confirm()

    def get_result_success_text(self):
        """获取额度申请成功结果文本"""
        return self.fd_element(self.__success_text).text

    def get_result_fail_text(self):
        """获取额度申请失败结果文本"""
        return self.fd_element(self.__fail_text).text
