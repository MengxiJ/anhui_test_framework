# Copyright (C) 2026. All rights reserved.
"""browser 域 step 原子节点（薄封装，仅调用 lib 入口）。"""
from __future__ import annotations

from tblocks.utils.composer import composer_step
from lib.common.browser import browser_step as lib


@composer_step(
    name="step_open_browser_url",
    description="启动浏览器并打开指定 URL（浏览器实例在工作流内共享）",
    category="browser",
    params={"url": {"name": "URL", "type": "str", "required": True, "description": "目标地址"}},
)
def step_open_browser_url(url):
    """打开 URL。"""
    return lib.step_open_browser_url(url)


@composer_step(
    name="step_navigate_browser_url",
    description="浏览器在当前标签页跳转指定 URL",
    category="browser",
    params={"url": {"name": "URL", "type": "str", "required": True, "description": "目标地址"}},
)
def step_navigate_browser_url(url):
    """跳转 URL。"""
    return lib.step_navigate_browser_url(url)


@composer_step(
    name="step_input_element_text",
    description="按定位器找到元素，清空后输入文本",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True,
               "enum": ["id", "name", "class_name", "css", "xpath", "link_text", "tag_name"],
               "description": "id/name/class_name/css/xpath/link_text/tag_name"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "text": {"name": "输入文本", "type": "str", "required": True, "description": "要输入的内容"},
    },
)
def step_input_element_text(by, value, text):
    """元素输入。"""
    return lib.step_input_element_text(by, value, text)


@composer_step(
    name="step_click_element",
    description="点击可见元素",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
    },
)
def step_click_element(by, value):
    """点击元素。"""
    return lib.step_click_element(by, value)


@composer_step(
    name="step_click_present_element",
    description="点击存在但可能不可见的元素（如隐藏 radio）",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
    },
)
def step_click_present_element(by, value):
    """点击存在性元素。"""
    return lib.step_click_present_element(by, value)


@composer_step(
    name="step_select_dropdown_option",
    description="下拉框按可见文本选择",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "text": {"name": "选项文本", "type": "str", "required": True, "description": "可见文本"},
    },
)
def step_select_dropdown_option(by, value, text):
    """下拉选择。"""
    return lib.step_select_dropdown_option(by, value, text)


@composer_step(
    name="step_switch_frame",
    description="切换到指定 iframe",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
    },
)
def step_switch_frame(by, value):
    """切换 iframe。"""
    return lib.step_switch_frame(by, value)


@composer_step(
    name="step_switch_default_frame",
    description="从 iframe 切回主文档",
    category="browser",
)
def step_switch_default_frame():
    """切回主文档。"""
    return lib.step_switch_default_frame()


@composer_step(
    name="step_switch_new_window",
    description="等待并切换到新打开的浏览器窗口",
    category="browser",
    params={"timeout": {"name": "超时秒数", "type": "int", "required": False,
                        "default": 10, "description": "等待新窗口超时"}},
)
def step_switch_new_window(timeout=10):
    """切换新窗口。"""
    return lib.step_switch_new_window(timeout=timeout)


@composer_step(
    name="step_get_element_text",
    description="读取元素文本，结果放入 data.result",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
    },
)
def step_get_element_text(by, value):
    """读取元素文本。"""
    return lib.step_get_element_text(by, value)


@composer_step(
    name="step_capture_screenshot",
    description="页面截图并保存到 output/screenshot，路径放入 data.result",
    category="browser",
    params={"file_name": {"name": "文件名", "type": "str", "required": False,
                          "default": None, "description": "可选文件名"}},
)
def step_capture_screenshot(file_name=None):
    """截图。"""
    return lib.step_capture_screenshot(file_name=file_name)


@composer_step(
    name="step_open_url_settled",
    description="打开 URL 并等待重定向稳定，最终 URL 放入 data.result（用于入口被强制重定向的场景）",
    category="browser",
    params={
        "url": {"name": "URL", "type": "str", "required": True, "description": "目标地址"},
        "settle_seconds": {"name": "稳定秒数", "type": "float", "required": False,
                           "default": 2.0, "description": "URL 连续不变即视为稳定的秒数"},
        "timeout": {"name": "总超时秒数", "type": "float", "required": False,
                    "default": 15.0, "description": "等待重定向的总超时（应大于稳定秒数）"},
    },
)
def step_open_url_settled(url, settle_seconds=2.0, timeout=15.0):
    """打开 URL 并等待重定向稳定。"""
    return lib.step_open_url_settled(url, settle_seconds=settle_seconds, timeout=timeout)


@composer_step(
    name="step_wait_for_url",
    description="等待当前 URL 包含指定片段，最终 URL 放入 data.result",
    category="browser",
    params={
        "fragment": {"name": "URL 片段", "type": "str", "required": True,
                     "description": "期望出现在 URL 中的文本"},
        "timeout": {"name": "超时秒数", "type": "float", "required": False,
                    "default": 15.0, "description": "等待超时"},
    },
)
def step_wait_for_url(fragment, timeout=15.0):
    """等待 URL 出现。"""
    return lib.step_wait_for_url(fragment, timeout=timeout)


@composer_step(
    name="step_wait_for_text",
    description="等待元素文本包含指定内容，元素全文放入 data.result",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "text": {"name": "期望文本", "type": "str", "required": True, "description": "等待出现的文本片段"},
        "timeout": {"name": "超时秒数", "type": "float", "required": False,
                    "default": 10.0, "description": "等待超时"},
    },
)
def step_wait_for_text(by, value, text, timeout=10.0):
    """等待元素文本出现。"""
    return lib.step_wait_for_text(by, value, text, timeout=timeout)


@composer_step(
    name="step_get_element_attribute",
    description="读取元素属性（如 href/value），结果放入 data.result",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "attribute": {"name": "属性名", "type": "str", "required": True,
                      "description": "如 href / value / name / src"},
    },
)
def step_get_element_attribute(by, value, attribute):
    """读取元素属性。"""
    return lib.step_get_element_attribute(by, value, attribute)


@composer_step(
    name="step_get_elements_text",
    description="读取全部匹配元素的文本列表，结果放入 data.result / data.texts",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "timeout": {"name": "超时秒数", "type": "float", "required": False,
                    "default": 10.0, "description": "等待至少一个元素出现的超时"},
    },
)
def step_get_elements_text(by, value, timeout=10.0):
    """读取多元素文本列表。"""
    return lib.step_get_elements_text(by, value, timeout=timeout)


@composer_step(
    name="step_get_elements_attribute",
    description="读取全部匹配元素的指定属性列表，结果放入 data.result / data.values",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "定位方式"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "attribute": {"name": "属性名", "type": "str", "required": True, "description": "如 href / value"},
        "timeout": {"name": "超时秒数", "type": "float", "required": False,
                    "default": 10.0, "description": "等待至少一个元素出现的超时"},
    },
)
def step_get_elements_attribute(by, value, attribute, timeout=10.0):
    """读取多元素属性列表。"""
    return lib.step_get_elements_attribute(by, value, attribute, timeout=timeout)


@composer_step(
    name="step_get_table_data",
    description="读取 HTML 表格（表头+数据行），结果放入 data.headers / data.rows / data.row_count",
    category="browser",
    params={
        "by": {"name": "定位方式", "type": "str", "required": True, "description": "指向 table 或其容器"},
        "value": {"name": "定位表达式", "type": "str", "required": True, "description": "定位值"},
        "timeout": {"name": "超时秒数", "type": "float", "required": False,
                    "default": 10.0, "description": "等待表格出现的超时"},
    },
)
def step_get_table_data(by, value, timeout=10.0):
    """读取表格数据。"""
    return lib.step_get_table_data(by, value, timeout=timeout)


@composer_step(
    name="step_click_text_in_container",
    description="在容器范围内点击文本匹配的元素（列表项/链接场景常用）",
    category="browser",
    params={
        "by": {"name": "容器定位方式", "type": "str", "required": True, "description": "容器定位方式"},
        "value": {"name": "容器定位表达式", "type": "str", "required": True, "description": "容器定位值"},
        "text": {"name": "目标文本", "type": "str", "required": True, "description": "要点击的元素文本"},
        "exact": {"name": "精确匹配", "type": "bool", "required": False,
                  "default": True, "description": "True=文本完全相等，False=包含"},
    },
)
def step_click_text_in_container(by, value, text, exact=True):
    """按文本点击容器内元素。"""
    return lib.step_click_text_in_container(by, value, text, exact=exact)


@composer_step(
    name="step_accept_alert",
    description="接受原生 alert/confirm 并读取文本放入 data.text；无 alert 时 data.present=False",
    category="browser",
    params={
        "timeout": {"name": "等待秒数", "type": "float", "required": False,
                    "default": 3.0, "description": "等待 alert 出现的超时"},
    },
)
def step_accept_alert(timeout=3.0):
    """接受原生弹窗。"""
    return lib.step_accept_alert(timeout=timeout)


@composer_step(
    name="step_execute_js",
    description="在当前页面执行 JavaScript，返回值放入 data.result",
    category="browser",
    params={
        "script": {"name": "JS 脚本", "type": "str", "required": True,
                   "description": "JS 代码（arguments[0..n] 对应 args）"},
        "args": {"name": "脚本参数", "type": "list", "required": False,
                 "default": None, "description": "传给脚本的参数列表"},
    },
)
def step_execute_js(script, args=None):
    """执行 JavaScript。"""
    return lib.step_execute_js(script, args=args)
