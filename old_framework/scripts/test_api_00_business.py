from config import USER, PWD
from api.login_register_api import LoginRegisterAPI
from scripts.base_test import BaseAPITest


class TestAPIBusiness(BaseAPITest):
    """API业务流程测试"""
    
    def test_api_login_only(self):
        """登录流程测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        login_result = login_response.json()
        self.logger.info(f"登录结果: {login_result}")
        assert login_result["status"] == 200
        
        self.logger.info("=== 登录流程测试通过 ===")
