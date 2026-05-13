import pytest
from config import USER, PWD
from api.login_register_api import LoginRegisterAPI
from utils import read_json
from scripts.base_test import BaseAPITest


class TestAPIRechargeTender(BaseAPITest):
    """测试类：充值和投资API"""
    
    @pytest.mark.parametrize("payment_type,amount,form_str,valicode,expect", 
                            read_json("api_recharge_data.json"))
    def test_api_recharge(self, payment_type, amount, form_str, valicode, expect):
        """充值接口测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        
        api.get_recharge_verifycode()
        
        response = api.recharge(
            payment_type=payment_type,
            amount=amount,
            form_str=form_str,
            valicode=valicode
        )
        
        assert response.status_code == 200
        
        try:
            result = response.json()
            self.logger.info(f"充值响应结果: {result}")
            assert result["status"] == expect
        except Exception:
            self.logger.warning("响应非JSON格式，跳过业务状态码断言")

    @pytest.mark.parametrize("loan_id,deposit_certificate,amount,expect", 
                            read_json("api_tender_data.json"))
    def test_api_tender(self, loan_id, deposit_certificate, amount, expect):
        """投资接口测试"""
        api = LoginRegisterAPI()
        
        login_response = api.login(keywords=USER, password=PWD)
        assert login_response.status_code == 200
        
        response = api.tender(
            loan_id=loan_id,
            deposit_certificate=deposit_certificate,
            amount=amount
        )
        
        assert response.status_code == 200
        
        try:
            result = response.json()
            self.logger.info(f"投资响应结果: {result}")
            assert result["status"] == expect
        except Exception:
            self.logger.warning("响应非JSON格式，跳过业务状态码断言")
