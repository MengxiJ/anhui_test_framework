from config import USER, PWD, USERNAME, PASSWORD, IMG_CODE
from pages import LoginPage, CreditApplicationPage, BackLoginPage, LoanManagerPage
from scripts.base_test import BaseUITest


class TestBusiness(BaseUITest):
    """核心业务测试"""

    def test_00_business_success(self, web_driver):
        """核心业务1：额度申请审核业务"""
        login_page = LoginPage(web_driver)
        login_page.open_url()
        login_page.login(USER, PWD)

        credit_page = CreditApplicationPage(web_driver)
        credit_page.credit_application("100000", "额度申请详情信息", "8888")

        back_page = BackLoginPage(web_driver)
        back_page.open_back_url()
        back_page.back_login(USERNAME, PASSWORD, IMG_CODE)

        loan_page = LoanManagerPage(web_driver)
        loan_page.credit_application_review(USER)

        loan_page.click_app_rec(USER)
        result = loan_page.get_result_text()
        self.logger.info(f"额度审核结果：{result}")
        assert "通过" == result

        loan_page.get_shot(class_name=self.class_name, method_name="test_00_business_success")
