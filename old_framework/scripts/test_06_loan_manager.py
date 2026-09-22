import pytest
from pages import LoanManagerPage
from utils import read_json
from scripts.base_test import BaseUITest


class TestLoanManager(BaseUITest):
    """测试类：额度审核页"""

    @pytest.mark.parametrize("phone,note,img_code,expect,img", read_json("loan_manager_data.json"))
    def test_loan_manager(self, web_driver, b_login, phone, note, img_code, expect, img):
        """额度审核"""
        try:
            loan_page = LoanManagerPage(web_driver)
            loan_page.credit_application_review(phone, note, img_code)
            
            if "通过" in expect:
                loan_page.click_app_rec(phone)
                result = loan_page.get_result_success_text()
            else:
                result = loan_page.get_result_fail_text()
            
            self.logger.info(f"额度审核结果：{result}")
            assert expect in result
            loan_page.get_shot(class_name=self.class_name, method_name="test_loan_manager")
        except Exception as e:
            loan_page.get_shot(class_name=self.class_name, method_name="test_loan_manager_fail")
            self.logger.error(f"额度审核失败：{e}")
            raise
