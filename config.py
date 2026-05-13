# 项目配置相关的文件信息
import os
from dotenv import load_dotenv
from tools.data_generator import data_generator

# 加载环境变量
load_dotenv()

# 获取项目路径[不同操作系统都可以获取]
PATH = os.path.dirname(__file__)

# 项目的地址[切换测试环境]
BASE_URL = os.getenv("BASE_URL", "http://121.43.169.97:8081")
BACK_URL = os.getenv("BACK_URL", "http://121.43.169.97:8082")

# API基础路径
API_BASE_URL = os.getenv("API_BASE_URL", "http://121.43.169.97:8081")

# 测试数据目录路径
DATA_PATH = os.path.join(PATH, "data")

# 管理员信息（从环境变量读取）
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "HM_2023_test")
IMG_CODE = os.getenv("ADMIN_IMG_CODE", "8888")

# 借款人信息（从环境变量读取）
USER = os.getenv("TEST_USER", "18800006000")
PWD = os.getenv("TEST_PASSWORD", "Aa123456")

# 测试用户数据（使用数据生成器，支持复用）
_user_data = data_generator.get_or_create_user()
NAME = _user_data.get("name", "测试用户")
PHONE = _user_data.get("phone", "13800138000")
CARD = _user_data.get("id_card", "110101199001011234")
