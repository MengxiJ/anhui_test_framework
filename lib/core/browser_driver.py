# Copyright (C) 2026. All rights reserved.
"""浏览器驱动工厂（本项目的“设备通信底座”，对应框架的 adb_shell）。

职责单一：创建/配置 Selenium WebDriver。业务层不要直接调用本模块，
统一通过 ``lib.common.framework.step_singletons.get_browser`` 获取。
"""
from __future__ import annotations

import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

logger = logging.getLogger(__name__)


def create_chrome_driver(
    headless: Optional[bool] = None,
    implicit_wait: int = 10,
    page_load_timeout: int = 60,
) -> webdriver.Chrome:
    """创建 Chrome WebDriver。

    优先使用系统 PATH 中的本地 ChromeDriver；失败后回退到
    webdriver-manager 自动下载（与项目 conftest 行为保持一致）。

    Args:
        headless: 是否无头模式。None 时读取环境变量 ``TBLOCKS_HEADLESS``，
            未设置则默认有头，便于观察 UI 自动化过程。
        implicit_wait: 隐式等待秒数。
        page_load_timeout: 页面加载超时秒数（默认 60s：教学站点服务器
            响应波动大，实测同步 JS 全下载需 8~30s，30s 会间歇性超时）。

    Returns:
        已完成基础配置的 Chrome WebDriver。

    Raises:
        BrowserUnavailableError: 本地驱动与自动下载均失败。
    """
    from lib.core.exceptions import BrowserUnavailableError

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 站点页面同步引用外网脚本（QQ 客服 wpa.b.qq.com 实测 7s+ 响应），
    # 会阻塞 DOMContentLoaded 导致 renderer 超时；映射到 127.0.0.1 快速失败，
    # 统计/客服/图片 CDN 与业务无关，不影响测试。
    options.add_argument(
        "--host-resolver-rules="
        "MAP wpa.b.qq.com 127.0.0.1, "
        "MAP plausible.io 127.0.0.1, "
        "MAP imgv-p2p-test.itheima.net 127.0.0.1, "
        "MAP user-p2p-test.itheima.net 127.0.0.1, "
        "MAP www.miitbeian.gov.cn 127.0.0.1"
    )
    # eager：等待 DOMContentLoaded 即返回，进一步降低页面加载耗时。
    options.page_load_strategy = "eager"

    if headless is None:
        import os

        headless = os.getenv("TBLOCKS_HEADLESS", "").lower() in ("1", "true", "yes", "on")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("使用本地 ChromeDriver 创建浏览器")
    except Exception as exc:  # noqa: BLE001
        logger.warning("本地 ChromeDriver 不可用，尝试 webdriver-manager: %s", exc)
        try:
            from webdriver_manager.chrome import ChromeDriverManager

            driver = webdriver.Chrome(
                options=options, service=ChromeService(ChromeDriverManager().install())
            )
            logger.info("webdriver-manager 下载 ChromeDriver 成功")
        except Exception as exc2:  # noqa: BLE001
            raise BrowserUnavailableError(
                "ChromeDriver 初始化失败，请确认已安装 Chrome 浏览器且 ChromeDriver 可用"
                f"（或设置 TBLOCKS_HEADLESS=1 使用无头模式）。原因: {exc2}"
            ) from exc2

    driver.implicitly_wait(implicit_wait)
    driver.set_page_load_timeout(page_load_timeout)
    if not headless:
        try:
            driver.maximize_window()
        except Exception:  # noqa: BLE001
            pass
    return driver
