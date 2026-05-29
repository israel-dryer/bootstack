"""TextArea and CodeEditor composite widgets."""

from .textarea import TextArea, TextAreaInputEventData, TextAreaValidationEventData
from .codeeditor import CodeEditor
from .filter import EditFilter
from .core import _MultilineCore
from .sidebar import Sidebar
from .decoration import Position, RangeDecoration, LineDecoration, WidgetDecoration
from .extensions.line_numbers import LineNumbers
from .extensions.bracket_matcher import BracketMatcher
from .extensions.smart_indent import SmartIndent

__all__ = [
    "TextArea",
    "TextAreaInputEventData",
    "TextAreaValidationEventData",
    "CodeEditor",
    "EditFilter",
    "_MultilineCore",
    "Sidebar",
    "Position",
    "RangeDecoration",
    "LineDecoration",
    "WidgetDecoration",
    "LineNumbers",
    "BracketMatcher",
    "SmartIndent",
]
