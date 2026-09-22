# Copyright (C) 2026. All rights reserved.
"""browser 域 Lib 入口：浏览器通用步骤。

``BrowserManager`` 缓存在 ``browser_core:<device_id>``，内部复用
``step_singletons.get_browser`` 创建的同一个 WebDriver 实例。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lib.common.browser.utils.browser_manager import BrowserManager
from lib.common.framework.step_singletons import current_device_id, get_browser
from lib.common.result_helper import step_result
from lib.core import instance_manager

_CORE_PREFIX = "browser_core"


def _get_instance_key(device_id: Optional[str] = None) -> str:
    return f"{_CORE_PREFIX}:{device_id or current_device_id()}"


def _get_core(device_id: Optional[str] = None) -> BrowserManager:
    key = _get_instance_key(device_id)
    if not instance_manager.has_instance(key):
        instance_manager.register_instance(key, BrowserManager(get_browser(device_id)))
    return instance_manager.get_instance(key)


def clear_core(device_id: Optional[str] = None) -> None:
    """释放 BrowserManager（浏览器本身随 reset_instances 退出）。"""
    instance_manager.clear_instance(_get_instance_key(device_id))


def step_open_browser_url(url: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """打开指定 URL。"""
    _get_core(device_id).open_url(url)
    return step_result("step_open_browser_url", True, f"已打开页面: {url}", {"result": url, "url": url})


def step_navigate_browser_url(url: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """浏览器跳转指定 URL（与打开页面等价，语义用于流程中途导航）。"""
    _get_core(device_id).navigate(url)
    return step_result("step_navigate_browser_url", True, f"已跳转页面: {url}", {"result": url, "url": url})


def step_input_element_text(
    by: str,
    value: str,
    text: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """定位元素并清空后输入文本。"""
    _get_core(device_id).input_text(by, value, text)
    return step_result(
        "step_input_element_text",
        True,
        f"已在元素 ({by}={value}) 输入文本",
        {"result": str(text), "by": by, "value": value, "text": str(text)},
    )


def step_click_element(by: str, value: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """点击可见元素。"""
    _get_core(device_id).click(by, value)
    return step_result(
        "step_click_element",
        True,
        f"已点击元素 ({by}={value})",
        {"result": f"{by}={value}", "by": by, "value": value},
    )


def step_click_present_element(by: str, value: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """点击存在但可能不可见的元素（如隐藏 radio）。"""
    _get_core(device_id).click_present(by, value)
    return step_result(
        "step_click_present_element",
        True,
        f"已点击存在性元素 ({by}={value})",
        {"result": f"{by}={value}", "by": by, "value": value},
    )


def step_select_dropdown_option(
    by: str,
    value: str,
    text: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """下拉框按可见文本选择。"""
    _get_core(device_id).select_by_visible_text(by, value, text)
    return step_result(
        "step_select_dropdown_option",
        True,
        f"下拉框 ({by}={value}) 已选择 {text}",
        {"result": text, "by": by, "value": value, "option": text},
    )


def step_switch_frame(by: str, value: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """切换到指定 iframe。"""
    _get_core(device_id).switch_to_frame(by, value)
    return step_result(
        "step_switch_frame",
        True,
        f"已切换到 iframe ({by}={value})",
        {"result": f"{by}={value}"},
    )


def step_switch_default_frame(device_id: Optional[str] = None) -> Dict[str, Any]:
    """切回主文档。"""
    _get_core(device_id).switch_to_default_frame()
    return step_result("step_switch_default_frame", True, "已切回主文档", {"result": "default"})


def step_switch_new_window(timeout: int = 10, device_id: Optional[str] = None) -> Dict[str, Any]:
    """切换到新打开的窗口。"""
    handle = _get_core(device_id).switch_to_new_window(timeout=timeout)
    return step_result(
        "step_switch_new_window",
        True,
        "已切换到新窗口",
        {"result": handle, "window_handle": handle},
    )


def step_get_element_text(
    by: str,
    value: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """读取元素文本，结果放入 ``data.result`` 供后续节点引用。"""
    text = _get_core(device_id).get_text(by, value)
    return step_result(
        "step_get_element_text",
        True,
        f"元素 ({by}={value}) 文本: {text}",
        {"result": text, "text": text, "by": by, "value": value},
    )


def step_capture_screenshot(
    file_name: Optional[str] = None,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """页面截图并保存到 output/screenshot。"""
    path = _get_core(device_id).screenshot(file_name=file_name)
    return step_result(
        "step_capture_screenshot",
        True,
        f"截图已保存: {path}",
        {"result": path, "file_path": path},
    )


def step_open_url_settled(
    url: str,
    settle_seconds: float = 2.0,
    timeout: float = 15.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """打开 URL 并等待重定向稳定，最终 URL 放入 ``data.result``。"""
    final_url = _get_core(device_id).open_url_settled(url, settle_seconds=settle_seconds, timeout=timeout)
    redirected = final_url != url
    return step_result(
        "step_open_url_settled",
        True,
        f"已打开 {url}，最终 URL: {final_url}" + ("（发生重定向）" if redirected else ""),
        {"result": final_url, "url": final_url, "requested_url": url, "redirected": redirected},
    )


def step_wait_for_url(
    fragment: str,
    timeout: float = 15.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """等待当前 URL 包含指定片段，最终 URL 放入 ``data.result``。"""
    current_url = _get_core(device_id).wait_for_url(fragment, timeout=timeout)
    return step_result(
        "step_wait_for_url",
        True,
        f"当前 URL 已包含 {fragment!r}: {current_url}",
        {"result": current_url, "url": current_url, "fragment": fragment},
    )


def step_wait_for_text(
    by: str,
    value: str,
    text: str,
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """等待元素文本包含指定内容，元素全文放入 ``data.result``。"""
    full_text = _get_core(device_id).wait_for_text(by, value, text, timeout=timeout)
    return step_result(
        "step_wait_for_text",
        True,
        f"元素 ({by}={value}) 已出现文本 {text!r}",
        {"result": full_text, "text": full_text, "by": by, "value": value},
    )


def step_get_element_attribute(
    by: str,
    value: str,
    attribute: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """读取元素属性（如 href/value），结果放入 ``data.result``。"""
    attr_value = _get_core(device_id).get_element_attribute(by, value, attribute)
    return step_result(
        "step_get_element_attribute",
        True,
        f"元素 ({by}={value}) 属性 {attribute}={attr_value!r}",
        {
            "result": attr_value,
            "attribute": attribute,
            "attribute_value": attr_value,
            "by": by,
            "value": value,
        },
    )


def step_get_elements_text(
    by: str,
    value: str,
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """读取全部匹配元素文本列表，结果放入 ``data.result`` / ``data.texts``。"""
    texts = _get_core(device_id).get_elements_text(by, value, timeout=timeout)
    return step_result(
        "step_get_elements_text",
        True,
        f"匹配到 {len(texts)} 个元素，文本列表: {texts}",
        {"result": texts, "texts": texts, "count": len(texts), "by": by, "value": value},
    )


def step_get_elements_attribute(
    by: str,
    value: str,
    attribute: str,
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """读取全部匹配元素指定属性列表，结果放入 ``data.result`` / ``data.values``。"""
    values = _get_core(device_id).get_elements_attribute(by, value, attribute, timeout=timeout)
    return step_result(
        "step_get_elements_attribute",
        True,
        f"匹配到 {len(values)} 个元素，属性 {attribute} 列表: {values}",
        {"result": values, "values": values, "count": len(values), "by": by, "value": value},
    )


def step_get_table_data(
    by: str,
    value: str,
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """读取 HTML 表格（表头+数据行），结果放入 ``data.headers`` / ``data.rows``。"""
    table = _get_core(device_id).get_table_data(by, value, timeout=timeout)
    return step_result(
        "step_get_table_data",
        True,
        f"读取表格: {table['row_count']} 行，表头: {table['headers']}",
        {
            "result": table,
            "headers": table["headers"],
            "rows": table["rows"],
            "row_count": table["row_count"],
            "by": by,
            "value": value,
        },
    )


def step_click_text_in_container(
    by: str,
    value: str,
    text: str,
    exact: bool = True,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """在容器范围内点击文本匹配的元素（列表/链接场景常用）。"""
    clicked = _get_core(device_id).click_text_in_container(by, value, text, exact=exact)
    return step_result(
        "step_click_text_in_container",
        True,
        f"已点击容器 ({by}={value}) 内文本 {clicked!r} 元素",
        {"result": clicked, "text": clicked, "by": by, "value": value, "exact": bool(exact)},
    )


def step_accept_alert(
    timeout: float = 3.0,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """接受原生 alert/confirm 并读取文本；无 alert 返回 present=False。"""
    alert = _get_core(device_id).accept_alert(timeout=timeout)
    present = bool(alert["present"])
    return step_result(
        "step_accept_alert",
        True,
        f"alert {'文本: ' + alert['text'] if present else '不存在（超时返回空结果）'}",
        {"result": alert["text"], "present": present, "text": alert["text"]},
    )


def step_execute_js(
    script: str,
    args: Optional[list] = None,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """在当前页面执行 JavaScript，返回值放入 ``data.result``。"""
    result = _get_core(device_id).execute_js(script, *(args or []))
    if not isinstance(result, (str, int, float, bool, list, dict, type(None))):
        result = str(result)
    return step_result(
        "step_execute_js",
        True,
        f"JS 执行完成，返回: {result!r}",
        {"result": result},
    )
