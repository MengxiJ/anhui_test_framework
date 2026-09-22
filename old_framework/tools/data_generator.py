# 测试数据管理工具
import os
import json
from faker import Faker


class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, locale="zh_CN"):
        self.faker = Faker(locale)
        # 使用当前文件所在目录的上级目录的data目录
        self.data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_data_cache.json")
    
    def generate_user_data(self):
        """生成用户测试数据"""
        return {
            "name": self.faker.name(),
            "phone": self.faker.phone_number(),
            "id_card": self.faker.ssn(),
            "email": self.faker.email(),
            "address": self.faker.address()
        }
    
    def generate_bank_card(self):
        """生成银行卡号"""
        return self.faker.credit_card_number()
    
    def save_test_data(self, data, key):
        """
        保存测试数据到缓存文件
        
        Args:
            data: 要保存的数据
            key: 数据的键名
        """
        cache = {}
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        
        cache[key] = data
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    
    def load_test_data(self, key):
        """
        从缓存文件加载测试数据
        
        Args:
            key: 数据的键名
            
        Returns:
            缓存的数据，如果不存在则生成新数据
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if key in cache:
                    return cache[key]
        
        # 如果不存在，生成新数据并保存
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
