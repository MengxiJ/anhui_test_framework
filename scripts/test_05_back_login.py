import pytest
from pages import BackLoginPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestBackLogin(BaseUITest):
    """测试类：后台登录页"""

    @pytest.mark.parametrize("username,password,img_code,expect,img", read_json("back_login_data.json"))
    def test_back_login(self, web_driver, username, password, img_code, expect, img):
        """后台登录"""
        try:
            back_login_page = BackLoginPage(web_driver)
            back_login_page.open_back_url()
            back_login_page.back_login(username, password, img_code)
            
            # 判断是成功还是失败用例（成功用例的expect包含"欢迎"）
            if "欢迎" in expect:
                result = back_login_page.get_result_success_text()
            else:
                result = back_login_page.get_result_fail_text()
            
            self.logger.info(f"后台登录结果：{result}")
            assert expect in result
            back_login_page.get_shot(class_name=self.class_name, method_name="test_back_login")
        except Exception as e:
            back_login_page.get_shot(class_name=self.class_name, method_name="test_back_login_fail")
            self.logger.error(f"后台登录失败：{e}")
            raise
