"""Common type aliases for bootstack widgets.

This module provides centralized type definitions used across all widget modules
to ensure consistency and reduce import boilerplate.
"""

from __future__ import annotations

import tkinter
from typing import Any, Callable, Literal, Optional, Union

Master = Optional[tkinter.Misc]
"""Parent widget. Pass any tkinter widget or `None` to use the default root window."""

EventCallback = Callable[[tkinter.Event], None]
"""Callback that receives a Tkinter `Event` object."""

CommandCallback = Callable[[], Any]
"""Callback invoked with no arguments, e.g. a button `command=`."""

WidgetKwargs = dict[str, Any]
"""Generic dict of widget configuration keyword arguments."""

ScrollDirection = Literal['horizontal', 'vertical', 'both']
"""Scroll axis for `ScrolledText`."""

ScrollbarVisibility = Literal['always', 'never', 'hover', 'scroll']
"""Scrollbar visibility mode for `ScrolledText`."""