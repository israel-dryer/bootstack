"""SideNavHeader widget for section labels in navigation menus."""

from typing import Any, Callable

from typing_extensions import TypedDict, Unpack

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master


class SideNavHeaderKwargs(TypedDict, total=False):
    text: str
    # Frame options
    padding: Any
    width: int
    height: int


class SideNavHeader(Frame):
    """A section header for grouping navigation items.

    SideNavHeader provides a text label to identify groups of related
    navigation items. Unlike SideNavItem, headers are not selectable
    and serve only as visual labels. Uses the 'label' font token for styling.

    When `collapsible` is True the header gains a chevron and reports clicks via
    `on_toggle`; the owner (e.g. `NavPanel`) flips `collapsed` and re-lays out the
    group's items. The header itself holds only the collapsed flag + chevron — it
    does not own the items. The chevron styling is refined in the shell styling
    pass; here it is a functional affordance.

    """

    DEFAULT_PADDING = (8, 20, 8, 4)
    DEFAULT_FONT = 'label'
    DEFAULT_ACCENT = 'default'

    def __init__(
        self,
        master: Master = None,
        text: str = '',
        collapsible: bool = False,
        on_toggle: Callable[[], None] | None = None,
        **kwargs: Unpack[SideNavHeaderKwargs]
    ):
        """Initialize a SideNavHeader.

        Args:
            master: Parent widget.
            text: The header text to display.
            collapsible: Render a chevron and report clicks via `on_toggle`.
            on_toggle: Called (no args) when a collapsible header is clicked.
            **kwargs: Additional arguments passed to Frame.
        """
        self._text = text
        self._collapsible = collapsible
        self._collapsed = False
        self._on_toggle = on_toggle

        # Default padding: more top margin for visual separation between sections
        kwargs.setdefault('padding', self.DEFAULT_PADDING)

        super().__init__(master, **kwargs)

        # Header label with 'label' font (smaller, bold) and secondary accent.
        self._text_label = Label(
            self,
            text=text,
            font=self.DEFAULT_FONT,
            accent=self.DEFAULT_ACCENT,
            anchor='w',
        )
        self._chevron: Label | None = None

        if self._collapsible:
            self._text_label.pack(side='left', fill='x', expand=True)
            self._chevron = Label(
                self,
                icon=self._chevron_icon(),
                icon_only=True,
                accent=self.DEFAULT_ACCENT,
            )
            self._chevron.pack(side='right')
            for widget in (self, self._text_label, self._chevron):
                widget.bind('<Button-1>', self._on_click, add='+')
        else:
            self._text_label.pack(fill='x')

    def _chevron_icon(self) -> dict:
        name = 'chevron-right' if self._collapsed else 'chevron-down'
        return {'name': name, 'size': 14}

    def _on_click(self, _event=None):
        if self._on_toggle is not None:
            self._on_toggle()

    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed flag and update the chevron (visual only)."""
        self._collapsed = collapsed
        if self._chevron is not None:
            self._chevron.configure(icon=self._chevron_icon())

    @property
    def collapsible(self) -> bool:
        """Whether this header toggles a group of items."""
        return self._collapsible

    @property
    def collapsed(self) -> bool:
        """Whether this header's group is currently collapsed."""
        return self._collapsed

    @property
    def text(self) -> str:
        """Get the header text."""
        return self._text

    @configure_delegate('text')
    def _delegate_text(self, value: str = None):
        """Configure the header text."""
        if value is None:
            return self._text
        self._text = value
        self._text_label.configure(text=value)
        return None
