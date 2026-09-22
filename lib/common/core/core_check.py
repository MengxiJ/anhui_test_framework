# Copyright (C) 2026. All rights reserved.
"""core 域 Lib 入口：通用检查点（纯内存断言，不依赖外部资源）。

校验“不通过”返回 ``status=False``；只有执行异常（如类型无法转换、
收到未解析的 ``${...}`` 占位符）才算执行错误，同样以失败结果返回。
"""
from __future__ import annotations

from typing import Any, Dict

from lib.common.core.utils.text_number import parse_number_text
from lib.common.result_helper import check_result

_CHECK_EQUAL = "check_value_equal"
_CHECK_GREATER = "check_value_greater_than"
_CHECK_WITHIN = "check_value_within_range"
_CHECK_TEXT_CONTAINS = "check_text_contains"
_CHECK_TEXT_NOT_CONTAINS = "check_text_not_contains"
_CHECK_TEXT_NUMBER = "check_text_number_compare"

_COMPARE_FUNCS = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


def _is_unresolved_placeholder(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("${")
        and value.endswith("}")
    )


def _to_number(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    return float(value)


def check_value_equal(actual: Any, expected: Any) -> Dict[str, Any]:
    """检查两个值相等（数值按数值比较，其余按字符串比较）。"""
    if _is_unresolved_placeholder(actual) or _is_unresolved_placeholder(expected):
        return check_result(
            _CHECK_EQUAL,
            False,
            f"存在未解析的变量引用: actual={actual!r}, expected={expected!r}",
            expected=expected,
            actual=actual,
        )
    try:
        actual_num = _to_number(actual)
        expected_num = _to_number(expected)
        passed = actual_num == expected_num
    except (TypeError, ValueError):
        passed = str(actual) == str(expected)
    return check_result(
        _CHECK_EQUAL,
        passed,
        f"实际值 {actual!r} {'等于' if passed else '不等于'} 期望值 {expected!r}",
        expected=expected,
        actual=actual,
        data={"actual": actual, "expected": expected},
    )


def check_value_greater_than(actual: Any, expected: Any) -> Dict[str, Any]:
    """检查实际数值大于期望值。"""
    name = _CHECK_GREATER
    if _is_unresolved_placeholder(actual) or _is_unresolved_placeholder(expected):
        return check_result(
            name,
            False,
            f"存在未解析的变量引用: actual={actual!r}, expected={expected!r}",
            expected=expected,
            actual=actual,
        )
    try:
        actual_num = _to_number(actual)
        expected_num = _to_number(expected)
    except (TypeError, ValueError):
        return check_result(
            name,
            False,
            f"无法比较非数值: actual={actual!r}, expected={expected!r}",
            expected=expected,
            actual=actual,
        )
    passed = actual_num > expected_num
    return check_result(
        name,
        passed,
        f"{actual_num:g} {'大于' if passed else '不大于'} {expected_num:g}",
        expected=f"> {expected_num:g}",
        actual=actual_num,
        data={"actual": actual_num, "expected": expected_num},
    )


def check_value_within_range(actual: Any, lower: Any, upper: Any) -> Dict[str, Any]:
    """检查实际数值落在 [lower, upper] 闭区间内。"""
    name = _CHECK_WITHIN
    try:
        actual_num = _to_number(actual)
        lower_num = _to_number(lower)
        upper_num = _to_number(upper)
    except (TypeError, ValueError):
        return check_result(
            name,
            False,
            f"存在非数值参数: actual={actual!r}, lower={lower!r}, upper={upper!r}",
            expected=f"[{lower}, {upper}]",
            actual=actual,
        )
    passed = lower_num <= actual_num <= upper_num
    return check_result(
        name,
        passed,
        f"{actual_num:g} {'在' if passed else '不在'} 区间 [{lower_num:g}, {upper_num:g}] 内",
        expected=f"[{lower_num:g}, {upper_num:g}]",
        actual=actual_num,
        data={"actual": actual_num, "lower": lower_num, "upper": upper_num},
    )


def check_text_contains(actual: Any, expected: Any) -> Dict[str, Any]:
    """检查实际文本包含期望子串。"""
    name = _CHECK_TEXT_CONTAINS
    actual_text = "" if actual is None else str(actual)
    expected_text = "" if expected is None else str(expected)
    passed = expected_text in actual_text
    return check_result(
        name,
        passed,
        f"实际文本{'包含' if passed else '不包含'}期望子串 {expected_text!r}",
        expected=f"包含 {expected_text!r}",
        actual=actual_text,
        data={"actual": actual_text, "expected": expected_text},
    )


def check_text_not_contains(actual: Any, expected: Any) -> Dict[str, Any]:
    """检查实际文本不包含期望子串。"""
    name = _CHECK_TEXT_NOT_CONTAINS
    actual_text = "" if actual is None else str(actual)
    expected_text = "" if expected is None else str(expected)
    passed = expected_text not in actual_text
    return check_result(
        name,
        passed,
        f"实际文本{'不包含' if passed else '包含了'}被排除子串 {expected_text!r}",
        expected=f"不包含 {expected_text!r}",
        actual=actual_text,
        data={"actual": actual_text, "expected": expected_text},
    )


def check_text_number_compare(
    text: Any,
    operator: str = ">=",
    expected: Any = 0,
) -> Dict[str, Any]:
    """解析文本数值并与期望值比较。

    兼容 ``￥78,000.00元账户余额`` / ``+100.00`` / ``10.00%`` / ``站内信(8)``
    等格式，取文本第一个数值参与比较。
    """
    name = _CHECK_TEXT_NUMBER
    if _is_unresolved_placeholder(text) or _is_unresolved_placeholder(expected):
        return check_result(
            name,
            False,
            f"存在未解析的变量引用: text={text!r}, expected={expected!r}",
            expected=expected,
            actual=text,
        )
    compare = _COMPARE_FUNCS.get(str(operator))
    if compare is None:
        return check_result(
            name,
            False,
            f"不支持的比较运算符: {operator!r}，支持: {sorted(_COMPARE_FUNCS)}",
            expected=f"运算符 ∈ {sorted(_COMPARE_FUNCS)}",
            actual=str(operator),
            data={"operator": str(operator)},
        )
    try:
        actual_num = parse_number_text(text)
        expected_num = float(expected)
    except (TypeError, ValueError) as exc:
        return check_result(
            name,
            False,
            f"数值解析失败: {exc}",
            expected=f"文本可解析为数值并与 {expected!r} 比较",
            actual=str(text),
            data={"source_text": str(text)},
        )
    passed = compare(actual_num, expected_num)
    return check_result(
        name,
        passed,
        f"解析值 {actual_num:g} {operator} {expected_num:g} -> {'成立' if passed else '不成立'}",
        expected=f"{operator} {expected_num:g}",
        actual=actual_num,
        data={
            "actual": actual_num,
            "expected": expected_num,
            "operator": str(operator),
            "source_text": str(text),
        },
    )
