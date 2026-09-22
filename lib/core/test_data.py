# Copyright (C) 2026. All rights reserved.
"""测试数据生成与身份缓存（原子化项目自包含，缓存位于 lib/core/data）。"""
from __future__ import annotations

import json
import os

from faker import Faker

from lib.core.paths import DATA_DIR


class TestDataGenerator:
    """测试数据生成器：生成并持久复用同一套测试用户身份。"""

    def __init__(self, locale="zh_CN"):
        self.faker = Faker(locale)
        self.data_file = os.path.join(DATA_DIR, "test_data_cache.json")

    def generate_user_data(self):
        """生成用户测试数据"""
        return {
            "name": self.faker.name(),
            "phone": self.faker.phone_number(),
            "id_card": self.faker.ssn(),
            "email": self.faker.email(),
            "address": self.faker.address(),
        }

    def save_test_data(self, data, key):
        """保存测试数据到缓存文件"""
        cache = {}
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        cache[key] = data
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    def load_test_data(self, key):
        """从缓存文件加载测试数据；不存在则生成并缓存"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
                if key in cache:
                    return cache[key]

        if key == "user_data":
            data = self.generate_user_data()
        else:
            data = None
        if data:
            self.save_test_data(data, key)
        return data

    def get_or_create_user(self):
        """获取或创建用户数据（复用）"""
        return self.load_test_data("user_data")

    def clear_cache(self):
        """清除缓存数据"""
        if os.path.exists(self.data_file):
            os.remove(self.data_file)


# 全局实例
data_generator = TestDataGenerator()
