# Copyright (C) 2026. All rights reserved.
"""文本数值解析（纯函数，无外部资源依赖）。

兼容站点常见的金额/数值展示格式：

- ``78,000.00元账户余额`` -> 78000.0
- ``￥78,000.00`` / ``¥1,234.56`` -> 78000.0 / 1234.56
- ``+100.00`` / ``-50.00`` -> 100.0 / -50.0
- ``10.00%`` -> 10.0
- ``站内信(8)`` -> 8.0

取文本中**第一个**数值；无法解析时抛 ``ValueError``。
"""
from __future__ import annotations

import re
from typing import Any

# 千分位与货币符号等干扰字符
_NOISE_CHARS = "￥¥$,，"

_NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def parse_number_text(text: Any) -> float:
    """从文本解析第一个数值并返回 float。

    Args:
        text: 任意文本（数字直接传入亦可）。

    Returns:
        解析出的数值。

    Raises:
        ValueError: 文本为空或其中不含数值。
    """
    raw = "" if text is None else str(text).strip()
    if not raw:
        raise ValueError("文本为空，无法解析数值")
    cleaned = raw
    for char in _NOISE_CHARS:
        cleaned = cleaned.replace(char, "")
    match = _NUMBER_RE.search(cleaned)
    if not match:
        raise ValueError(f"文本中未找到数值: {raw!r}")
    return float(match.group())
