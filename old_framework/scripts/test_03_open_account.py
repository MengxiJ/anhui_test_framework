import pytest
from pages import OpenAccountPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestOpenAccount(BaseUITest):
    """测试类：资金托管页"""

    @pytest.mark.parametrize("real_name,card,expect,img", read_json("open_account_data.json"))
    def test_open_account(self, web_driver, a_login, real_name, card, expect, img):
        """开通资金托管"""
        account_page = OpenAccountPage(web_driver)
        
        try:
            is_success = "OK" in expect
            account_page.open_account(real_name, card, expect_success=is_success)
            
            if is_success:
                result = account_page.get_result_success_text()
            else:
                result = account_page.get_result_fail_text()
            
            self.logger.info(f"开通托管资金的结果：{result}")
            assert expect in result
            account_page.get_shot(class_name=self.class_name, method_name="test_open_account")
        except Exception as e:
            self.logger.info(f"用例执行异常：{e}")
            raise
