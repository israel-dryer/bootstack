from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal
from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs, WidgetDensity


class TreeViewKwargs(StyledKwargs, total=False):
    # Standard ttk.Treeview options
    columns: Any
    displaycolumns: Any
    show: Literal['tree', 'headings', '']
    height: int
    padding: Any
    selectmode: Literal['browse','extended','none'] | str

    # bootstack-specific extensions
    density: WidgetDensity
    border_color: str
    show_border: bool
    select_background: str
    header_background: str


class TreeView(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Treeview):
    """bootstack wrapper for `ttk.Treeview` with themed styling support."""

    _ttk_base = ttk.Treeview

    def __init__(self, master: Master = None, **kwargs: Unpack[TreeViewKwargs]) -> None:
        """Create a themed bootstack Treeview.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            columns: Sequence of column identifiers.
            displaycolumns: Subset and order of columns to display.
            show: Which parts to display (e.g., 'tree', 'headings').
            height: Number of rows to display.
            padding: Extra padding around the widget.
            selectmode: Selection mode ('browse', 'extended', 'none').
            style: Explicit ttk style name.
            surface: Optional surface token; otherwise inherited.
            density: Compactness of widget content ('default' or 'compact').
            border_color: Color of the border around the table.
            show_border: Whether to show a border around the table.
            open_icon: Icon used for the open state.
            close_icon: Icon used for the close state.
            select_background: Semantic color token for selection background.
            header_background: Semantic color token for the header background.
            style_options: Optional dict forwarded to the style builder.
        """
        kwargs.update(style_options=self._capture_style_options([
            'density',
            'border_color',
            'show_border',
            'open_icon',
            'close_icon',
            'select_background',
            'header_background'
        ],
            kwargs))
        super().__init__(master, **kwargs)
