# Copyright (C) 2026. All rights reserved.
"""``${...}`` 变量引用解析。

支持引用（见 WORKFLOW_JSON.md）：

- ``${<node_id>.data.<field>}``：前序 step/check 节点返回值；
- ``${custom_params.<field>}``：运行时台架参数；
- ``${loop_index}`` / ``${loop_current_item.xxx}``：range 循环上下文。

规则：

- 整个字符串是单一占位符时，解析后保留原始类型（int/dict/list 等）；
- 占位符嵌在文本中时，按字符串拼接；
- ``strict=True``（执行期）下无法解析的占位符抛 ``UnresolvedVariableError``；
  静态校验场景使用 ``strict=False`` 保留原样。
"""
from __future__ import annotations

import re
from typing import Any, Dict

PLACEHOLDER_RE = re.compile(r"\$\{([^{}]+)\}")


class VariableResolver:
    """基于节点返回上下文的变量解析器。"""

    def __init__(self, context: Dict[str, Any]) -> None:
        self.context = context

    def resolve(self, value: Any, strict: bool = True) -> Any:
        if isinstance(value, dict):
            return {key: self.resolve(item, strict) for key, item in value.items()}
        if isinstance(value, list):
            return [self.resolve(item, strict) for item in value]
        if not isinstance(value, str):
            return value

        matches = list(PLACEHOLDER_RE.finditer(value))
        if not matches:
            return value
        if len(matches) == 1 and matches[0].span() == (0, len(value)):
            return self._lookup(matches[0].group(1), strict, unresolved=value)

        def _replace(match: re.Match) -> str:
            resolved = self._lookup(match.group(1), strict, unresolved=match.group(0))
            return self._humanize(resolved)

        return PLACEHOLDER_RE.sub(_replace, value)

    def _lookup(self, path: str, strict: bool, unresolved: str) -> Any:
        parts = [part.strip() for part in path.split(".") if part.strip()]
        if not parts:
            if strict:
                from lib.core.exceptions import UnresolvedVariableError

                raise UnresolvedVariableError(f"空变量引用: ${{{path}}}")
            return unresolved
        if parts[0] not in self.context:
            if strict:
                from lib.core.exceptions import UnresolvedVariableError

                raise UnresolvedVariableError(
                    f"变量引用无法解析：${{{path}}}（上下文中不存在 {parts[0]!r}）"
                )
            return unresolved

        current: Any = self.context[parts[0]]
        for part in parts[1:]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                if strict:
                    from lib.core.exceptions import UnresolvedVariableError

                    raise UnresolvedVariableError(
                        f"变量引用无法解析：${{{path}}}（字段 {part!r} 不存在）"
                    )
                return unresolved
        return current

    @staticmethod
    def _humanize(value: Any) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)


def has_unresolved_placeholder(value: Any) -> bool:
    """递归检查值中是否仍含未解析的 ``${...}``。"""
    if isinstance(value, str):
        return bool(PLACEHOLDER_RE.search(value))
    if isinstance(value, dict):
        return any(has_unresolved_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(has_unresolved_placeholder(item) for item in value)
    return False
