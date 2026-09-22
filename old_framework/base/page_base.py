import os.path
import time
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from config import PATH
from utils import GetLog, OUTPUT_DIR


class BasePage(object):

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.default_timeout = timeout

    def fd_element(self, loc):
        try:
            element = WebDriverWait(self.driver, self.default_timeout).until(EC.visibility_of_element_located(loc))
            return element
        except Exception as e:
            GetLog.get_log().error(f"元素定位超时，定位信息：{loc}，错误详情：{e}")
            raise

    def get_shot(self, file_name=None, class_name=None, method_name=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if class_name and method_name:
            final_file_name = f"{class_name}_{method_name}_{timestamp}.png"
        elif file_name:
            name, ext = os.path.splitext(file_name)
            final_file_name = f"{name}_{timestamp}{ext}"
        else:
            final_file_name = f"screenshot_{timestamp}.png"

        screenshot_dir = os.path.join(OUTPUT_DIR, "screenshot")
        os.makedirs(screenshot_dir, exist_ok=True)
        file_path = os.path.join(screenshot_dir, final_file_name)
        self.driver.get_screenshot_as_file(file_path)

    def base_input(self, loc, text):
        ele = self.fd_element(loc)
        ele.clear()
        ele.send_keys(text)

    def base_click(self, loc):
        self.fd_element(loc).click()

    def base_click_special(self, loc):
        ele = WebDriverWait(self.driver, self.default_timeout).until(EC.presence_of_element_located(loc))
        ele.click()

    def base_switch_handle(self, loc):
        WebDriverWait(self.driver, self.default_timeout).until(lambda x: len(x.window_handles) > 1)
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])
        element = self.fd_element(loc)
        return element

    def base_switch_frame(self, loc):
        frame_ele = self.fd_element(loc)
        self.driver.switch_to.frame(frame_ele)

    def base_default_frame(self):
        self.driver.switch_to.default_content()

    def base_select_list(self, loc, text):
        ele = self.fd_element(loc)
        Select(ele).select_by_visible_text(text)
