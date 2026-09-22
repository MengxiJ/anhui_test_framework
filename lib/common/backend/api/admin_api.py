# Copyright (C) 2026. All rights reserved.
"""运营后台 8082 HTTP 接口（与前台 UI 自动化的 BackendManager 并列）。"""
import random

from lib.core.base_request import BaseRequest
from lib.core.logging_utils import GetLog
from lib.core.project_config import BACK_URL

logger = GetLog.get_log()


class AdminAPI(BaseRequest):
    """运营后台管理员接口（基址固定为 BACK_URL 8082）。"""

    def __init__(self):
        super().__init__(base_url=BACK_URL)

    def get_verifycode(self, r=None):
        """
        获取后台登录图形验证码（会话级，登录前必须先请求一次）。

        Returns:
            响应对象（JPEG 图片）
        """
        if r is None:
            r = random.random()
        url = f"/common/public/verifycode/{r}"
        logger.info("获取后台登录图形验证码")
        return self.get(url)

    def verify_login(self, username, password, valicode="8888"):
        """
        管理员登录校验 POST /system/public/verifyLogin。

        Args:
            username: 管理员账号
            password: 管理员密码
            valicode: 图形验证码（教学站固定 8888，需先 get_verifycode 建立会话）

        Returns:
            响应对象，成功体 {"status":200,"description":"OK"}
        """
        url = "/system/public/verifyLogin"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"username": username, "password": password, "valicode": valicode}
        logger.info(f"后台管理员登录校验，账号: {username}")
        return self.post(url, data=data, headers=headers)
