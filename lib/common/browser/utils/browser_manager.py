# Copyright (C) 2026. All rights reserved.
"""浏览器管理核心类（普通类，类内不做单例）。

包装 Selenium WebDriver 与项目 ``BasePage`` 的显式等待能力，
对上层暴露与具体业务页面无关的通用操作。定位器使用字符串描述，
便于在 workflow JSON 中以参数表达：

    by:   id / name / class_name / css / xpath / link_text / tag_name
    value: 定位表达式
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from lib.core.paths import OUTPUT_DIR

_BY_MAP = {
    "id": By.ID,
    "name": By.NAME,
    "class_name": By.CLASS_NAME,
    "class": By.CLASS_NAME,
    "css": By.CSS_SELECTOR,
    "css_selector": By.CSS_SELECTOR,
    "css selector": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "tag_name": By.TAG_NAME,
    "tag name": By.TAG_NAME,
}


def _xpath_literal(text: str) -> str:
    """构造 XPath 字符串字面量（处理引号转义）。"""
    text = str(text)
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    # 同时含单双引号：用 concat 拼接
    segments = text.split("'")
    pieces: List[str] = []
    for index, seg in enumerate(segments):
        if seg:
            pieces.append(f"'{seg}'")
        if index < len(segments) - 1:
            pieces.append('"\'"')
    return "concat(" + ", ".join(pieces) + ")"


class BrowserManager:
    """WebDriver 通用操作封装。"""

    def __init__(self, driver: Any, default_timeout: int = 10) -> None:
        self.driver = driver
        self.default_timeout = default_timeout

    # ---- 定位基础 ----
    def _locator(self, by: str, value: str) -> Tuple[str, str]:
        key = (by or "").strip().lower()
        if key not in _BY_MAP:
            raise ValueError(f"不支持的定位方式: {by!r}，支持: {sorted(set(_BY_MAP))}")
        return _BY_MAP[key], value

    def find_visible(self, by: str, value: str, timeout: Optional[int] = None):
        """等待元素可见并返回。"""
        wait = WebDriverWait(self.driver, self.default_timeout if timeout is None else timeout)
        return wait.until(EC.visibility_of_element_located(self._locator(by, value)))

    def find_present(self, by: str, value: str, timeout: Optional[int] = None):
        """等待元素出现在 DOM 并返回（不要求可见）。"""
        wait = WebDriverWait(self.driver, self.default_timeout if timeout is None else timeout)
        return wait.until(EC.presence_of_element_located(self._locator(by, value)))

    # ---- 导航 ----
    def open_url(self, url: str) -> str:
        """打开指定 URL。"""
        self.driver.get(url)
        return url

    navigate = open_url

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def open_url_settled(self, url: str, settle_seconds: float = 2.0, timeout: float = 15.0) -> str:
        """打开 URL 并等待重定向稳定（URL 连续 ``settle_seconds`` 秒不变）。

        用于「打开入口 → 站点强制重定向」的场景（如未绑卡提现 → 银行卡页），
        返回重定向稳定后的最终 URL。注意 ``timeout`` 应大于 ``settle_seconds``。
        """
        self.driver.get(url)
        last_url = self.driver.current_url
        stable_since = time.time()
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.3)
            current = self.driver.current_url
            if current == last_url:
                if time.time() - stable_since >= settle_seconds:
                    return current
            else:
                last_url = current
                stable_since = time.time()
        return last_url

    def wait_for_url(self, fragment: str, timeout: Optional[float] = None) -> str:
        """等待当前 URL 包含指定片段，返回最终 URL；超时抛 ``TimeoutError``。"""
        timeout = self.default_timeout if timeout is None else timeout
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(str(fragment)))
        except TimeoutException:
            raise TimeoutError(
                f"等待 URL 包含 {fragment!r} 超时（{timeout}s），当前: {self.driver.current_url}"
            ) from None
        return self.driver.current_url

    # ---- 交互 ----
    def input_text(self, by: str, value: str, text: Any) -> None:
        """清空后输入文本。"""
        element = self.find_visible(by, value)
        element.clear()
        element.send_keys("" if text is None else str(text))

    def click(self, by: str, value: str) -> None:
        """点击可见元素。"""
        self.find_visible(by, value).click()

    def click_present(self, by: str, value: str) -> None:
        """点击存在但可能不可见的元素（如被遮挡的 radio）。"""
        self.find_present(by, value).click()

    def select_by_visible_text(self, by: str, value: str, text: str) -> None:
        """下拉框按可见文本选择。"""
        Select(self.find_visible(by, value)).select_by_visible_text(text)

    def click_text_in_container(self, by: str, value: str, text: str, exact: bool = True) -> str:
        """在容器范围内点击文本匹配的元素，返回被点击元素文本。

        ``exact=True`` 精确匹配（normalize-space 后相等），``False`` 包含匹配；
        匹配多个时取第一个可点击的（AngularJS 列表/链接场景常用）。
        """
        container = self.find_visible(by, value)
        literal = _xpath_literal(text)
        if exact:
            xpath = f".//*[normalize-space(text())={literal}]"
        else:
            xpath = f".//*[contains(normalize-space(text()),{literal})]"
        candidates = container.find_elements(By.XPATH, xpath)
        if not candidates:
            raise ValueError(f"容器 ({by}={value}) 内未找到文本 {text!r} 的元素")
        last_error: Optional[Exception] = None
        for target in candidates:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                target.click()
                return (target.text or "").strip() or str(text)
            except Exception as exc:  # noqa: BLE001 - 逐个尝试直到点击成功
                last_error = exc
                continue
        raise ValueError(f"容器 ({by}={value}) 内文本 {text!r} 的元素均无法点击: {last_error}")

    def accept_alert(self, timeout: float = 3) -> Dict[str, Any]:
        """接受原生 alert/confirm 并返回其文本；超时无 alert 返回空结果。

        Returns:
            ``{"present": bool, "text": str}``。
        """
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        except TimeoutException:
            return {"present": False, "text": ""}
        text = alert.text or ""
        alert.accept()
        return {"present": True, "text": text}

    def execute_js(self, script: str, *args: Any) -> Any:
        """在当前页面执行 JavaScript 并返回结果。"""
        return self.driver.execute_script(script, *args)

    def switch_to_frame(self, by: str, value: str) -> None:
        """切换到指定 iframe。"""
        self.driver.switch_to.frame(self.find_visible(by, value))

    def switch_to_default_frame(self) -> None:
        """切回主文档。"""
        self.driver.switch_to.default_content()

    def switch_to_new_window(self, timeout: int = 10) -> str:
        """等待并切换到新窗口，返回新窗口句柄。"""
        WebDriverWait(self.driver, timeout).until(lambda d: len(d.window_handles) > 1)
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        return handles[-1]

    # ---- 读取 / 断言辅助 ----
    def get_text(self, by: str, value: str) -> str:
        """读取可见元素文本。"""
        return self.find_visible(by, value).text

    def get_element_attribute(self, by: str, value: str, attribute: str) -> str:
        """读取元素属性（如 href/value/name），属性不存在返回空串。"""
        element = self.find_present(by, value)
        return element.get_attribute(attribute) or ""

    def get_elements_text(self, by: str, value: str, timeout: Optional[float] = None) -> List[str]:
        """等待至少一个匹配元素出现，返回全部匹配元素文本列表。"""
        wait = WebDriverWait(self.driver, self.default_timeout if timeout is None else timeout)
        elements = wait.until(EC.presence_of_all_elements_located(self._locator(by, value)))
        texts = []
        for element in elements:
            text = (element.text or "").strip()
            if not text:
                text = (element.get_attribute("textContent") or "").strip()
            texts.append(text)
        return texts

    def get_elements_attribute(
        self, by: str, value: str, attribute: str, timeout: Optional[float] = None
    ) -> List[str]:
        """等待至少一个匹配元素出现，返回全部匹配元素指定属性列表。"""
        wait = WebDriverWait(self.driver, self.default_timeout if timeout is None else timeout)
        elements = wait.until(EC.presence_of_all_elements_located(self._locator(by, value)))
        return [element.get_attribute(attribute) or "" for element in elements]

    def get_table_data(self, by: str, value: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """读取 HTML 表格数据。

        定位器指向 ``<table>`` 或包含表格的容器；返回
        ``{"headers": [...], "rows": [[...], ...], "row_count": n}``。
        表头取 ``thead`` 首行的 ``th`` 与 ``td``（被测站点存在 td 表头写法）；
        无 ``thead`` 时取首行 ``th``；数据行取含 ``td`` 的行。
        """
        root = self.find_present(by, value, timeout=timeout)
        if root.tag_name.lower() != "table":
            tables = root.find_elements(By.TAG_NAME, "table")
            if not tables:
                raise ValueError(f"元素 ({by}={value}) 内未找到 <table>")
            root = tables[0]
        header_cells = root.find_elements(
            By.CSS_SELECTOR, "thead tr:nth-child(1) th, thead tr:nth-child(1) td"
        )
        if not header_cells:
            header_cells = root.find_elements(By.CSS_SELECTOR, "tr:nth-child(1) th")
        headers = [(cell.text or "").strip() for cell in header_cells]
        body_rows = root.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not body_rows:
            body_rows = [
                row for row in root.find_elements(By.CSS_SELECTOR, "tr")
                if row.find_elements(By.TAG_NAME, "td")
            ]
        rows = []
        for row in body_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                rows.append([(cell.text or "").strip() for cell in cells])
        return {"headers": headers, "rows": rows, "row_count": len(rows)}

    def wait_for_text(self, by: str, value: str, text: str, timeout: Optional[float] = None) -> str:
        """等待元素文本包含指定内容，返回元素全文；超时抛 ``TimeoutError``。"""
        timeout = self.default_timeout if timeout is None else timeout
        locator = self._locator(by, value)
        target = str(text)

        def _text_contains(driver):
            try:
                element = driver.find_element(*locator)
                if target in (element.text or ""):
                    return element
            except Exception:  # noqa: BLE001 - 轮询中元素可能尚未渲染
                return False
            return False

        try:
            element = WebDriverWait(self.driver, timeout).until(_text_contains)
        except TimeoutException:
            raise TimeoutError(
                f"等待元素 ({by}={value}) 文本包含 {target!r} 超时（{timeout}s）"
            ) from None
        return element.text or ""

    def element_exists(self, by: str, value: str, timeout: int = 5) -> bool:
        """元素在给定时间内是否出现（不抛异常）。"""
        try:
            self.find_present(by, value, timeout=timeout)
            return True
        except Exception:  # noqa: BLE001 - 存在性判断需吞掉超时异常
            return False

    def element_visible(self, by: str, value: str, timeout: float = 5) -> bool:
        """元素在给定时间内是否可见（不抛异常）。"""
        try:
            self.find_visible(by, value, timeout=timeout)
            return True
        except Exception:  # noqa: BLE001 - 可见性判断需吞掉超时异常
            return False

    def count_elements(self, by: str, value: str, timeout: Optional[float] = None) -> int:
        """统计匹配元素数量（等待至少一个出现；超时返回 0）。"""
        try:
            wait = WebDriverWait(self.driver, self.default_timeout if timeout is None else timeout)
            elements = wait.until(EC.presence_of_all_elements_located(self._locator(by, value)))
            return len(elements)
        except Exception:  # noqa: BLE001 - 数量判断需吞掉超时异常
            return 0

    def wait_seconds(self, seconds: float) -> float:
        seconds = max(0.0, float(seconds))
        time.sleep(seconds)
        return seconds

    def screenshot(self, file_name: Optional[str] = None) -> str:
        """截图到 output/screenshot，返回文件路径。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not file_name:
            file_name = f"tblocks_{timestamp}.png"
        name, ext = os.path.splitext(file_name)
        if not ext:
            ext = ".png"
        screenshot_dir = os.path.join(OUTPUT_DIR, "screenshot")
        os.makedirs(screenshot_dir, exist_ok=True)
        file_path = os.path.join(screenshot_dir, f"{name}_{timestamp}{ext}")
        self.driver.get_screenshot_as_file(file_path)
        return file_path

    def quit(self) -> None:
        """退出浏览器（由实例管理器统一释放，一般不手动调用）。"""
        try:
            self.driver.quit()
        except Exception:  # noqa: BLE001
            pass
