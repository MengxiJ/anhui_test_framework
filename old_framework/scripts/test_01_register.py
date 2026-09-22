import pytest
from pages import RegisterPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestRegister(BaseUITest):
    """测试类：注册页"""

    @pytest.mark.parametrize("phone,password,verifycode,phone_code,expect,img", read_json("register_data.json"))
    def test_register(self, web_driver, phone, password, verifycode, phone_code, expect, img):
        """注册"""
        reg = RegisterPage(web_driver)
        reg.open_url()
        try:
            reg.register(phone, password, verifycode, phone_code)
            if "成功" in expect:
                result = reg.get_result_success_text()
            else:
                result = reg.get_result_fail_text()

            self.logger.info(f"注册结果：{result}")
            
            assert expect in result
            reg.get_shot(class_name=self.class_name, method_name="test_register")
        except Exception as e:
            self.logger.info(f"用例执行异常：{e}")
            raise
