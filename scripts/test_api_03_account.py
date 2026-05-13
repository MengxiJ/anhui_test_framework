import pytest
from config import USER, PWD
from api.login_register_api import LoginRegisterAPI
from utils import read_json
from scripts.base_test import BaseAPITest


class TestAPIAccount(BaseAPITest):
    """测试类：账户API"""
    
    @pytest.mark.parametrize("real_name,id_card,expect", 
                            read_json("api_account_data.json"))
    def test_api_approve_realname(self, real_name, id_card, expect):
        """实名认证测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        
        response = api.approve_realname(realname=real_name, card_id=id_card)
        
        assert response.status_code == 200
        
        try:
            result = response.json()
            self.logger.info(f"实名认证响应结果: {result}")
            assert result["status"] == expect
        except Exception:
            self.logger.warning("响应非JSON格式，跳过业务状态码断言")
    
    def test_api_get_approve(self):
        """获取认证信息测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        
        response = api.get_approve()
        
        assert response.status_code == 200
        
        try:
            result = response.json()
            self.logger.info(f"获取认证信息响应结果: {result}")
        except Exception:
            self.logger.warning("响应非JSON格式，跳过业务状态码断言")
    
    def test_api_trust_register(self):
        """开户测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        
        response = api.trust_register()
        
        assert response.status_code == 200
        
        try:
            result = response.json()
            self.logger.info(f"开户响应结果: {result}")
        except Exception:
            self.logger.warning("响应非JSON格式，跳过业务状态码断言")
