import pytest
from pages import LoginPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestLogin(BaseUITest):
    """测试类：登录页"""

    @pytest.mark.parametrize("username,pwd,expect,img", read_json("login_data.json"))
    def test_login(self, web_driver, username, pwd, expect, img):
        """登录"""
        login_page = LoginPage(web_driver)
        login_page.open_url()

        try:
            login_page.login(username, pwd)
            if username == expect:
                result = login_page.get_result_success_text()
            else:
                result = login_page.get_result_fail_text()

            self.logger.info(f"登录结果：{result}")
            assert expect in result
            login_page.get_shot(class_name=self.class_name, method_name="test_login")
        except Exception as e:
            self.logger.info(f"用例执行异常：{e}")
            raise
