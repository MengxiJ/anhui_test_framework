# 测试基类
import time
import pytest
import requests
from scripts import logger
from utils import read_json


class BaseUITest(object):
    """UI 测试基类"""

    logger = logger
    read_json = staticmethod(read_json)

    @pytest.fixture(autouse=True)
    def setup_ui_test(self, request):
        """UI 测试通用前置/后置操作"""
        # 前置操作：获取测试类名用于截图
        self.class_name = request.cls.__name__ if request.cls else "UnknownClass"
        self.test_start_time = time.time()
        self.logger.info(f"开始执行UI测试: {request.node.name}")
        yield
        # 后置操作
        duration = time.time() - self.test_start_time
        self.logger.info(f"UI测试执行完成，耗时: {duration:.2f}秒")


class BaseAPITest(object):
    """API 测试基类"""

    logger = logger
    read_json = staticmethod(read_json)

    @pytest.fixture(autouse=True)
    def setup_api_test(self, request):
        """API 测试通用前置/后置操作"""
        self.test_start_time = time.time()
        self.logger.info(f"开始执行API测试: {request.node.name}")
        yield
        # 后置操作
        duration = time.time() - self.test_start_time
        self.logger.info(f"API测试执行完成，耗时: {duration:.2f}秒")

    # ==================== 统一断言方法 ====================

    def assert_status_code(self, response, expected_status=200):
        """
        断言HTTP状态码
        
        Args:
            response: 响应对象
            expected_status: 期望的状态码，默认200
        """
        actual_status = response.status_code
        assert actual_status == expected_status, \
            f"期望HTTP状态码 {expected_status}，实际 {actual_status}"
        self.logger.info(f"HTTP状态码断言通过: {actual_status}")

    def assert_business_status(self, result, expected_status):
        """
        断言业务状态码
        
        Args:
            result: 响应JSON数据
            expected_status: 期望的业务状态码
        """
        actual_status = result.get("status")
        assert actual_status == expected_status, \
            f"期望业务状态码 {expected_status}，实际 {actual_status}"
        self.logger.info(f"业务状态码断言通过: {actual_status}")

    def assert_response_contains(self, result, key, value=None):
        """
        断言响应包含指定键值
        
        Args:
            result: 响应JSON数据
            key: 键名
            value: 期望的值（可选）
        """
        assert key in result, f"响应中不包含键 '{key}'，实际响应: {result}"
        
        if value is not None:
            actual_value = result.get(key)
            assert actual_value == value, \
                f"期望 {key}={value}，实际 {key}={actual_value}"
        
        self.logger.info(f"响应包含断言通过: {key}")

    def assert_response_not_empty(self, response):
        """
        断言响应不为空
        
        Args:
            response: 响应对象
        """
        assert response is not None, "响应对象为空"
        assert response.status_code is not None, "响应状态码为空"
        self.logger.info("响应非空断言通过")

    def assert_response_time(self, response, max_seconds=5):
        """
        断言响应时间
        
        Args:
            response: 响应对象
            max_seconds: 最大响应时间（秒）
        """
        if hasattr(response, 'elapsed'):
            elapsed = response.elapsed.total_seconds()
            assert elapsed <= max_seconds, \
                f"响应时间 {elapsed:.2f}秒 超过最大限制 {max_seconds}秒"
            self.logger.info(f"响应时间断言通过: {elapsed:.2f}秒")

    def assert_json_schema(self, result, required_keys):
        """
        断言JSON响应包含必需的键
        
        Args:
            result: 响应JSON数据
            required_keys: 必需的键列表
        """
        missing_keys = [key for key in required_keys if key not in result]
        assert not missing_keys, \
            f"响应缺少必需的键: {missing_keys}"
        self.logger.info(f"JSON结构断言通过: {required_keys}")

    def assert_in_text(self, actual_text, expected_text):
        """
        断言文本包含指定内容
        
        Args:
            actual_text: 实际文本
            expected_text: 期望包含的文本
        """
        assert expected_text in actual_text, \
            f"期望文本包含 '{expected_text}'，实际: '{actual_text}'"
        self.logger.info(f"文本包含断言通过: '{expected_text}'")

    def assert_not_in_text(self, actual_text, unexpected_text):
        """
        断言文本不包含指定内容
        
        Args:
            actual_text: 实际文本
            unexpected_text: 期望不包含的文本
        """
        assert unexpected_text not in actual_text, \
            f"文本不应包含 '{unexpected_text}'，实际: '{actual_text}'"
        self.logger.info(f"文本不包含断言通过: '{unexpected_text}'")

    def assert_greater_than(self, actual, expected):
        """
        断言实际值大于期望值
        
        Args:
            actual: 实际值
            expected: 期望值
        """
        assert actual > expected, \
            f"期望 {actual} > {expected}"
        self.logger.info(f"大于断言通过: {actual} > {expected}")

    def assert_less_than(self, actual, expected):
        """
        断言实际值小于期望值
        
        Args:
            actual: 实际值
            expected: 期望值
        """
        assert actual < expected, \
            f"期望 {actual} < {expected}"
        self.logger.info(f"小于断言通过: {actual} < {expected}")

    def assert_equal(self, actual, expected):
        """
        断言两个值相等
        
        Args:
            actual: 实际值
            expected: 期望值
        """
        assert actual == expected, \
            f"期望 {expected}，实际 {actual}"
        self.logger.info(f"相等断言通过: {actual} == {expected}")

    def assert_not_equal(self, actual, expected):
        """
        断言两个值不相等
        
        Args:
            actual: 实际值
            expected: 期望值
        """
        assert actual != expected, \
            f"不期望 {expected}，但实际值相同"
        self.logger.info(f"不相等断言通过: {actual} != {expected}")

    def assert_is_none(self, value):
        """
        断言值为None
        
        Args:
            value: 要检查的值
        """
        assert value is None, f"期望值为None，实际: {value}"
        self.logger.info("None断言通过")

    def assert_is_not_none(self, value):
        """
        断言值不为None
        
        Args:
            value: 要检查的值
        """
        assert value is not None, "期望值不为None，实际为None"
        self.logger.info("非None断言通过")

    def assert_in_list(self, item, list_value):
        """
        断言项在列表中
        
        Args:
            item: 要检查的项
            list_value: 列表
        """
        assert item in list_value, \
            f"项 '{item}' 不在列表 {list_value} 中"
        self.logger.info(f"列表包含断言通过: '{item}'")

    def assert_list_length(self, list_value, expected_length):
        """
        断言列表长度
        
        Args:
            list_value: 列表
            expected_length: 期望长度
        """
        actual_length = len(list_value)
        assert actual_length == expected_length, \
            f"期望列表长度 {expected_length}，实际 {actual_length}"
        self.logger.info(f"列表长度断言通过: {actual_length}")
