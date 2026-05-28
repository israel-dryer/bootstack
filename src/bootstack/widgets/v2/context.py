from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets.v2.container import PublicContainer

_local = threading.local()


def _stack() -> list:
    s = getattr(_local, "stack", None)
    if s is None:
        s = []
        _local.stack = s
    return s


def push_container(container: "PublicContainer") -> None:
    _stack().append(container)


def pop_container(expected: "PublicContainer") -> None:
    s = _stack()
    if not s or s[-1] is not expected:
        if expected in s:
            s.remove(expected)
        return
    s.pop()


def current_container() -> "PublicContainer | None":
    s = _stack()
    return s[-1] if s else None
