import pytest
from api.login_register_api import LoginRegisterAPI
from utils import read_json
from scripts.base_test import BaseAPITest


class TestAPILogin(BaseAPITest):
    """测试类：登录API"""
    
    @pytest.mark.parametrize("keywords,password,expect", 
                            read_json("api_login_data.json"))
    def test_api_login(self, keywords, password, expect):
        """登录接口测试"""
        api = LoginRegisterAPI()
        
        response = api.login(keywords=keywords, password=password)
        
        assert response.status_code == 200
        
        result = response.json()
        self.logger.info(f"登录响应结果: {result}")
        
        assert result["status"] == expect
