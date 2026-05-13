# 登录注册API接口
import random
from api.base_request import BaseRequest
from scripts import logger


class LoginRegisterAPI(BaseRequest):
    """登录注册API接口"""
    
    def __init__(self):
        super().__init__()
    
    def get_verifycode(self, r=None):
        """
        获取图片验证码
        
        Args:
            r: 随机数，默认自动生成
        
        Returns:
            响应对象
        """
        if r is None:
            r = random.random()
        
        url = f"/common/public/verifycode1/{r}"
        logger.info("获取图片验证码")
        return self.get(url)
    
    def send_sms(self, phone, img_verify_code, type="reg"):
        """
        获取短信验证码
        
        Args:
            phone: 手机号
            img_verify_code: 图片验证码
            type: 类型，默认reg(注册)
        
        Returns:
            响应对象
        """
        url = "/member/public/sendSms"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "phone": phone,
            "imgVerifyCode": img_verify_code,
            "type": type
        }
        logger.info(f"获取短信验证码，手机号: {phone}")
        return self.post(url, data=data, headers=headers)
    
    def register(self, phone, password, verifycode, phone_code, dy_server="on", invite_phone=None):
        """
        注册
        
        Args:
            phone: 手机号
            password: 密码
            verifycode: 图片验证码
            phone_code: 手机验证码
            dy_server: 是否同意协议，默认on
            invite_phone: 邀请人，可选
        
        Returns:
            响应对象
        """
        url = "/member/public/reg"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "phone": phone,
            "password": password,
            "verifycode": verifycode,
            "phone_code": phone_code,
            "dy_server": dy_server
        }
        
        if invite_phone:
            data["invite_phone"] = invite_phone
        
        logger.info(f"注册，手机号: {phone}")
        return self.post(url, data=data, headers=headers)
    
    def login(self, keywords, password):
        """
        登录
        
        Args:
            keywords: 手机号
            password: 密码
        
        Returns:
            响应对象
        """
        url = "/member/public/login"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "keywords": keywords,
            "password": password
        }
        logger.info(f"登录，手机号: {keywords}")
        return self.post(url, data=data, headers=headers)
    
    def is_login(self):
        """
        判断是否登录
        
        Returns:
            响应对象
        """
        url = "/member/public/isLogin"
        logger.info("判断是否登录")
        return self.post(url)
    
    def approve_realname(self, realname, card_id):
        """
        实名认证
        
        Args:
            realname: 真实姓名
            card_id: 身份证号
        
        Returns:
            响应对象
        """
        url = "/member/realname/approverealname"
        data = {
            "realname": realname,
            "card_id": card_id
        }
        logger.info(f"实名认证，姓名: {realname}")
        return self.post(url, data=data)
    
    def get_approve(self):
        """
        获取认证信息
        
        Returns:
            响应对象
        """
        url = "/member/member/getapprove"
        logger.info("获取认证信息")
        return self.post(url)
    
    def trust_register(self):
        """
        开户
        
        Returns:
            响应对象
        """
        url = "/trust/trust/register"
        logger.info("开户")
        return self.post(url)
    
    def get_recharge_verifycode(self, r=None):
        """
        获取充值验证码
        
        Args:
            r: 随机数，默认自动生成
        
        Returns:
            响应对象
        """
        if r is None:
            r = random.random()
        
        url = f"/common/public/verifycode/{r}"
        logger.info("获取充值验证码")
        return self.get(url)
    
    def recharge(self, payment_type="chinapnrTrust", amount="", form_str="reForm", valicode=""):
        """
        充值
        
        Args:
            payment_type: 充值类型，默认chinapnrTrust
            amount: 充值金额
            form_str: 表单字符串，默认reForm
            valicode: 验证码
        
        Returns:
            响应对象
        """
        url = "/trust/trust/recharge"
        data = {
            "paymentType": payment_type,
            "amount": amount,
            "formStr": form_str,
            "valicode": valicode
        }
        logger.info(f"充值，金额: {amount}")
        return self.post(url, data=data)
    
    def tender(self, loan_id=0, deposit_certificate=-1, amount=0):
        """
        投资
        
        Args:
            loan_id: 产品id
            deposit_certificate: 默认-1
            amount: 投资金额
        
        Returns:
            响应对象
        """
        url = "/trust/trust/tender"
        data = {
            "id": loan_id,
            "depositCertificate": deposit_certificate,
            "amount": amount
        }
        logger.info(f"投资，产品id: {loan_id}，金额: {amount}")
        return self.post(url, data=data)
