import time
from selenium.webdriver.common.by import By
from base.page_base import BasePage
from config import BASE_URL


class RegisterPage(BasePage):
    """前台注册页面 - 用户注册功能"""
    
    __register_url = BASE_URL + "/common/member/reg"
    __wait_time = 2
    
    __phone = (By.ID, "phone")
    __password = (By.ID, "password")
    __verifycode = (By.ID, "verifycode")
    __get_phone = (By.ID, "get_phone_code")
    __phone_code = (By.ID, "phone_code")
    __reg_btn = (By.CLASS_NAME, "lg-btn")
    __success_text = (By.XPATH, "//*[text()='注册成功！']")
    __fail_text = (By.CLASS_NAME, "reg-title")

    def __init__(self, driver):
        """初始化注册页面"""
        super().__init__(driver)

    def open_url(self):
        """打开注册页面"""
        self.driver.get(self.__register_url)

    def input_phone(self, phone):
        """输入手机号"""
        self.base_input(self.__phone, phone)

    def input_password(self, password):
        """输入密码"""
        self.base_input(self.__password, password)

    def input_verifycode(self, verifycode="8888"):
        """输入图片验证码"""
        self.base_input(self.__verifycode, verifycode)

    def click_get_code(self):
        """点击获取短信验证码"""
        self.base_click(self.__get_phone)

    def input_phone_code(self, phone_code="666666"):
        """输入短信验证码"""
        self.base_input(self.__phone_code, phone_code)

    def click_reg_btn(self):
        """点击注册按钮"""
        self.base_click(self.__reg_btn)

    def get_result_success_text(self):
        """获取注册成功结果文本"""
        return self.fd_element(self.__success_text).text

    def get_result_fail_text(self):
        """获取注册失败结果文本"""
        return self.fd_element(self.__fail_text).text

    def register(self, phone, password, verifycode="8888", phone_code="666666"):
        """执行注册操作"""
        self.input_phone(phone)
        self.input_password(password)
        self.input_verifycode(verifycode)
        self.click_get_code()
        time.sleep(self.__wait_time)
        self.input_phone_code(phone_code)
        self.click_reg_btn()
        time.sleep(1)