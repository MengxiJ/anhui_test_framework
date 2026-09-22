import pytest
from api.login_register_api import LoginRegisterAPI
from utils import read_json
from scripts.base_test import BaseAPITest


class TestAPIRegister(BaseAPITest):
    """测试类：注册API"""

    @pytest.mark.parametrize("phone,password,verifycode,phone_code,expect", read_json("api_register_data.json"))
    def test_api_register(self, phone, password, verifycode, phone_code, expect):
        """注册接口测试"""
        api = LoginRegisterAPI()

        # 1. 获取图片验证码
        api.get_verifycode()
        
        # 2. 发送短信验证码（当verifycode不为空时）
        if verifycode:
            sms_response = api.send_sms(phone=phone, img_verify_code=verifycode)
            self.logger.info(f"短信验证码响应: {sms_response.json()}")

        # 3. 注册
        response = api.register(phone=phone, password=password, verifycode=verifycode, phone_code=phone_code)

        # 断言
        assert response.status_code == 200

        result = response.json()
        self.logger.info(f"注册响应结果: {result}")

        assert result["status"] == expect
