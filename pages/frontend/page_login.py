from selenium.webdriver.common.by import By
from base.page_base import BasePage
from config import BASE_URL


class LoginPage(BasePage):
    """前台登录页面 - 用户登录功能"""

    __login_url = BASE_URL + "/common/member/login"

    __phone = (By.ID, "keywords")
    __password = (By.ID, "password")
    __login_btn = (By.ID, "login-btn")
    __success_text = (By.CLASS_NAME, "a-link1")
    __fail_text = (By.CSS_SELECTOR, "span.ng-binding")

    def __init__(self, driver):
        """初始化登录页面"""
        super().__init__(driver)

    def open_url(self):
        """打开登录页面"""
        self.driver.get(self.__login_url)

    def input_phone(self, phone):
        """输入手机号"""
        self.base_input(self.__phone, phone)

    def input_password(self, password):
        """输入密码"""
        self.base_input(self.__password, password)

    def click_login_btn(self):
        """点击登录按钮"""
        self.base_click(self.__login_btn)

    def get_result_success_text(self):
        """获取登录成功结果文本"""
        return self.fd_element(self.__success_text).text

    def get_result_fail_text(self):
        """获取登录失败结果文本"""
        return self.fd_element(self.__fail_text).text

    def login(self, phone, password="Aa123456"):
        """执行登录操作"""
        self.input_phone(phone)
        self.input_password(password)
        self.click_login_btn()
