from selenium.webdriver.common.by import By
from base.page_base import BasePage
from config import BACK_URL


class BackLoginPage(BasePage):
    """后台登录页面 - 管理员登录功能"""

    __back_url = BACK_URL

    __username = (By.ID, "username")
    __password = (By.ID, "password")
    __img_code = (By.ID, "valicode")
    __login_btn = (By.CLASS_NAME, "login-button")
    __success_text = (By.XPATH, "//div[text()='欢迎光临,']")
    __fail_text = (By.ID, "errorMessage")

    def __init__(self, driver):
        """初始化后台登录页面"""
        super().__init__(driver)

    def open_back_url(self):
        """打开后台登录页面"""
        self.driver.get(self.__back_url)

    def input_username(self, username):
        """输入用户名"""
        self.base_input(self.__username, username)

    def input_password(self, password):
        """输入密码"""
        self.base_input(self.__password, password)

    def input_img_code(self, img_code="8888"):
        """输入图片验证码"""
        self.base_input(self.__img_code, img_code)

    def click_login_btn(self):
        """点击登录按钮"""
        self.base_click(self.__login_btn)

    def get_result_success_text(self):
        """获取登录成功结果文本"""
        return self.fd_element(self.__success_text).text

    def get_result_fail_text(self):
        """获取登录失败结果文本"""
        return self.fd_element(self.__fail_text).text

    def back_login(self, username, password, img_code="8888"):
        """执行后台登录操作"""
        self.input_username(username)
        self.input_password(password)
        self.input_img_code(img_code)
        self.click_login_btn()
