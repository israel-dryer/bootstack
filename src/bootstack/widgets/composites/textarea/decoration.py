"""Decoration types for the TextArea/CodeEditor decoration system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any
import tkinter as tk


@dataclass(frozen=True)
class Position:
    """A line/column position in the text (1-indexed line, 0-indexed column)."""
    line: int
    col: int

    def to_tk(self) -> str:
        """Convert to a Tk text index string (e.g. ``'3.7'``)."""
        return f"{self.line}.{self.col}"


@dataclass(frozen=True)
class RangeDecoration:
    """A styled range from *start* to *end*."""
    start: Position
    end: Position
    style: str
    meta: dict | None = None


@dataclass(frozen=True)
class LineDecoration:
    """A style applied to an entire line."""
    line: int
    style: str
    meta: dict | None = None


@dataclass(frozen=True)
class WidgetDecoration:
    """A widget embedded at a position (e.g. inline diagnostic icon)."""
    at: Position
    widget_factory: Callable[[tk.Misc], tk.Widget]
    meta: dict | None = None
