"""Common type aliases for bootstack widgets."""

import tkinter
from typing import Any, Callable, Literal

Master = tkinter.Misc | None
"""Parent widget. Pass any tkinter widget or `None` to use the default root window."""

EventCallback = Callable[[tkinter.Event], None]
"""Callback that receives a Tkinter `Event` object."""

CommandCallback = Callable[[], Any]
"""Callback invoked with no arguments, e.g. a button `command=`."""

WidgetDensity = Literal['default', 'compact']
"""Widget density — `'default'` for normal sizing, `'compact'` for reduced padding."""