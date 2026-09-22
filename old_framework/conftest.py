import pytest
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from pages import LoginPage, BackLoginPage
from config import USER, PWD, USERNAME, PASSWORD, IMG_CODE, PATH
from utils import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _create_chrome_driver():
    """创建Chrome驱动，优先使用本地驱动，失败后尝试webdriver-manager"""
    try:
        driver = webdriver.Chrome()
        logger.info("使用本地ChromeDriver")
        return driver
    except Exception:
        logger.info("本地ChromeDriver不可用，尝试webdriver-manager自动下载")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            logger.info("webdriver-manager下载ChromeDriver成功")
            return driver
        except Exception as e:
            logger.error(f"ChromeDriver初始化失败: {e}")
            raise RuntimeError(
                "ChromeDriver初始化失败！请确保：\n"
                "1. 已安装Chrome浏览器\n"
                "2. ChromeDriver已添加到系统PATH，或\n"
                "3. 网络可访问chromedriver下载地址"
            )


@pytest.fixture
def web_driver():
    """Chrome浏览器fixture"""
    driver = _create_chrome_driver()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture
def a_login(web_driver, phone=USER, pwd=PWD):
    """前台登录功能"""
    login_page = LoginPage(web_driver)
    login_page.open_url()
    login_page.login(phone, pwd)


@pytest.fixture
def b_login(web_driver, username=USERNAME, password=PASSWORD, img_code=IMG_CODE):
    """后台登录功能"""
    login_page = BackLoginPage(web_driver)
    login_page.open_back_url()
    login_page.back_login(username, password, img_code)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败自动截图"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("web_driver")
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            class_name = item.cls.__name__ if item.cls else "UnknownClass"
            method_name = item.name
            file_name = f"{class_name}_{method_name}_fail_{timestamp}.png"
            screenshot_dir = os.path.join(OUTPUT_DIR, "screenshot")
            os.makedirs(screenshot_dir, exist_ok=True)
            file_path = os.path.join(screenshot_dir, file_name)
            driver.get_screenshot_as_file(file_path)
