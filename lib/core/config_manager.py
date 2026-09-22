# Copyright (C) 2026. All rights reserved.
"""配置管理器。

统一封装 ``lib.core.project_config`` 中的环境配置，并承载工作流运行时注入的
``custom_params``（台架参数），对应框架 ``lib/core/config_manager.py``。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.core import project_config


class ConfigManager:
    """全局配置 + 运行时自定义参数。"""

    def __init__(self) -> None:
        self._custom_params: Dict[str, Any] = {}

    def load_project_config(self) -> Dict[str, Any]:
        """读取项目环境配置。

        Returns:
            包含前后台地址、管理员、测试用户等信息的字典。
        """
        return {
            "base_url": project_config.BASE_URL,
            "back_url": project_config.BACK_URL,
            "api_base_url": project_config.API_BASE_URL,
            "admin_username": project_config.USERNAME,
            "admin_password": project_config.PASSWORD,
            "img_code": project_config.IMG_CODE,
            "user_phone": project_config.USER,
            "user_password": project_config.PWD,
            "test_name": project_config.NAME,
            "test_phone": project_config.PHONE,
            "test_id_card": project_config.CARD,
            "data_path": project_config.DATA_PATH,
        }

    def default_custom_params(self) -> Dict[str, Any]:
        """默认台架参数（可被工作流 ``${custom_params.xxx}`` 引用）。"""
        cfg = self.load_project_config()
        return {
            "base_url": cfg["base_url"],
            "back_url": cfg["back_url"],
            "user_phone": cfg["user_phone"],
            "user_password": cfg["user_password"],
            "admin_username": cfg["admin_username"],
            "admin_password": cfg["admin_password"],
            "img_code": cfg["img_code"],
            "test_name": cfg["test_name"],
            "test_id_card": cfg["test_id_card"],
        }

    def set_custom_params(self, params: Optional[Dict[str, Any]]) -> None:
        """合并设置台架参数（None 表示清空后用默认值填充）。"""
        merged = self.default_custom_params()
        if params:
            merged.update(params)
        self._custom_params = merged

    @property
    def custom_params(self) -> Dict[str, Any]:
        if not self._custom_params:
            self._custom_params = self.default_custom_params()
        return self._custom_params

    def get(self, key: str, default: Any = None) -> Any:
        """读取单个台架参数。"""
        return self.custom_params.get(key, default)


# 全局唯一配置管理器
config_manager = ConfigManager()
