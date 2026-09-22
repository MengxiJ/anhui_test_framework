# Copyright (C) 2026. All rights reserved.
"""API 请求基类（原子化项目自包含的 HTTP 底座）。

Session + 5xx 重试 + 超时，原子化各业务域统一通过
``lib.core.http_client.create_api_client`` 获取实例。
"""
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from lib.core.logging_utils import GetLog
from lib.core.project_config import API_BASE_URL

logger = GetLog.get_log()


class BaseRequest(object):
    """API请求基类"""

    def __init__(self, max_retries=3, timeout=30, base_url=None):
        self.session = requests.Session()
        # 默认走前台 8081；后台 8082 等其他站点可显式传入 base_url
        self.base_url = base_url or API_BASE_URL
        self.timeout = timeout

        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]),
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send_request(self, method, url, **kwargs):
        """
        发送HTTP请求

        Args:
            method: 请求方法 GET/POST/PUT/DELETE
            url: 请求路径
            **kwargs: 其他参数(data/params/json/headers等)

        Returns:
            响应对象
        """
        full_url = self.base_url + url
        kwargs.setdefault("timeout", self.timeout)

        try:
            logger.info(f"请求方法: {method}, 请求地址: {full_url}")
            if "data" in kwargs:
                logger.info(f"请求参数: {kwargs['data']}")
            if "json" in kwargs:
                logger.info(f"请求JSON: {kwargs['json']}")

            response = self.session.request(method=method, url=full_url, **kwargs)

            logger.info(f"响应状态码: {response.status_code}")

            try:
                response_json = response.json()
                logger.info(f"响应内容: {response_json}")
            except json.JSONDecodeError:
                content = response.text[:500] if len(response.text) > 500 else response.text
                logger.info(f"响应内容: {content}")

            return response
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise

    def get(self, url, params=None, **kwargs):
        """GET请求"""
        return self.send_request("GET", url, params=params, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """POST请求"""
        return self.send_request("POST", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        """PUT请求"""
        return self.send_request("PUT", url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        """DELETE请求"""
        return self.send_request("DELETE", url, **kwargs)
