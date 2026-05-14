"""Common type aliases for bootstack widgets.

This module provides centralized type definitions used across all widget modules
to ensure consistency and reduce import boilerplate.
"""

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

FileDialogType = Literal[
    'openfilename', 'openfile', 'directory', 'openfilenames', 'openfiles',
    'saveasfile', 'saveasfilename'
]
"""File dialog type for `PathEntry`.

- ``'openfilename'``: Select a single existing file (returns path string)
- ``'openfile'``: Select a single existing file (returns file object)
- ``'directory'``: Select a directory
- ``'openfilenames'``: Select multiple existing files (returns tuple of paths)
- ``'openfiles'``: Select multiple existing files (returns tuple of file objects)
- ``'saveasfile'``: Save file dialog (returns file object)
- ``'saveasfilename'``: Save file dialog (returns path string)
"""

ScrollDirection = Literal['horizontal', 'vertical', 'both']
"""Scroll axis for `ScrolledText`."""

ScrollbarVisibility = Literal['always', 'never', 'hover', 'scroll']
"""Scrollbar visibility mode for `ScrolledText`."""