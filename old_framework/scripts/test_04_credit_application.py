import pytest
from pages import CreditApplicationPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestCreditApplication(BaseUITest):
    """测试类：额度申请页"""

    @pytest.mark.parametrize("amount,detail_msg,img_code,expect,img", read_json("credit_application_data.json"))
    def test_credit_application(self, web_driver, a_login, amount, detail_msg, img_code, expect, img):
        """额度申请"""
        try:
            credit_page = CreditApplicationPage(web_driver)
            credit_page.credit_application(amount, detail_msg, img_code)
            
            # 判断是成功还是失败用例
            if ".00" in expect:
                result = credit_page.get_result_success_text()
            else:
                result = credit_page.get_result_fail_text()
            
            self.logger.info(f"额度申请结果：{result}")
            assert expect in result
            credit_page.get_shot(class_name=self.class_name, method_name="test_credit_application")
        except Exception as e:
            credit_page.get_shot(class_name=self.class_name, method_name="test_credit_application_fail")
            self.logger.error(f"额度申请失败：{e}")
            raise
