"""TextArea and CodeEditor composite widgets."""

from .textarea import TextArea
from .filter import EditFilter
from .core import _MultilineCore
from .sidebar import Sidebar
from .decoration import Position, RangeDecoration, LineDecoration, WidgetDecoration
from .extensions.line_numbers import LineNumbers

__all__ = [
    "TextArea",
    "EditFilter",
    "_MultilineCore",
    "Sidebar",
    "Position",
    "RangeDecoration",
    "LineDecoration",
    "WidgetDecoration",
    "LineNumbers",
]
