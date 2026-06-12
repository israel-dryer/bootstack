from __future__ import annotations

from typing import Any, Callable, Literal

from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill
from bootstack.widgets._core.window_controls import WindowControlsMixin
from bootstack.widgets._core.window_menu import ChromeHostMixin
from bootstack.widgets.types import Padding, Fill, Anchor, SurfaceToken, WindowStyle


class Window(WindowControlsMixin, ChromeHostMixin, PublicContainer):
    """A secondary top-level window.

    Behaves as an implicit `VStack` from the user's perspective: children
    created inside a ``with`` block are automatically packed into its content
    frame top-to-bottom.  Call `show()` to display the window after building
    its content, or `block_until_closed()` to show it and wait for the user
    to close it.

    Args:
        title: Window title bar text.
        size: Initial size as `(width, height)`.
        position: Initial position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(width, height)`.
        modal: Modality level. `False` — non-modal (default). `True` or
            `'window'` — grabs input from the parent only. `'app'` — grabs
            input from all windows.
        center_on_parent: Center over the parent/transient window.
        center_on_screen: Center on the screen.
        topmost: Keep the window above other windows.
        undecorated: Remove OS window decorations (`overrideredirect`).
        window_style: Windows-only window effect. None inherits the app's setting.
        on_close: Callback invoked when the user clicks the close button.
            Return `False` to veto; return `None` or `True` to allow.
        padding: Inner padding for the content frame.
        gap: Spacing between children.
        fill_items: Default `fill` value for children.
        expand_items: Default `expand` value for children.
        anchor_items: Default anchor for children that do not fill their cell.
        surface: Surface token for the content frame background.
        menu_layout: How the menu bar and toolbar stack at the top on
            Windows/Linux — `'fused'` (one row) or `'stacked'` (two rows). No
            effect on macOS (the menu bar moves to the global bar). Default `'fused'`.
        chrome_surface: Color token for the menu bar / toolbar row — `'chrome'`
            (default), `'background'` to blend into the window, or an accent like
            `'primary'` for a branded bar. Any surface/accent token (not `'content'`).
        chrome_divider: Draw a hairline divider below the menu/toolbar row.
            Default `True`; set `False` for a seamless blend.
    """

    _auto_place = False  # top-level window — no parent manages its position

    def __init__(
        self,
        *,
        title: str = "",
        size: tuple[int, int] | None = None,
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        modal: Literal[False, True, "window", "app"] = False,
        center_on_parent: bool = False,
        center_on_screen: bool = False,
        topmost: bool = False,
        undecorated: bool = False,
        window_style: WindowStyle | str | None = None,
        on_close: Callable[[], bool | None] | None = None,
        # chrome
        menu_layout: Literal["fused", "stacked"] = "fused",
        chrome_surface: SurfaceToken | str = "chrome",
        chrome_divider: bool = True,
        # Content frame layout
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | None = None,
        surface: SurfaceToken | str | None = None,
        **kwargs: Any,
    ) -> None:
        from bootstack._runtime.toplevel import Toplevel as _InternalToplevel

        self._parent = None
        self._menu_layout = menu_layout
        self._chrome_surface = chrome_surface
        self._chrome_divider_enabled = chrome_divider

        init_kwargs: dict[str, Any] = {
            "title": title,
            "modal": modal,
            "center_on_parent": center_on_parent,
            "center_on_screen": center_on_screen,
            "topmost": topmost,
            "overrideredirect": undecorated,
        }
        if size is not None:
            init_kwargs["size"] = size
        if position is not None:
            init_kwargs["position"] = position
        if min_size is not None:
            init_kwargs["minsize"] = min_size
        if max_size is not None:
            init_kwargs["maxsize"] = max_size
        if resizable is not None:
            init_kwargs["resizable"] = resizable
        if on_close is not None:
            init_kwargs["on_close"] = on_close
        if window_style is not None:
            init_kwargs["window_style"] = window_style
        init_kwargs.update(kwargs)

        self._tk_toplevel = _InternalToplevel(**init_kwargs)

        frame_kwargs: dict[str, Any] = {
            "direction": "vertical",
            "gap": gap,
            "fill_items": normalize_fill(fill_items),
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface

        self._content_frame = PackFrame(self._tk_toplevel, **frame_kwargs)
        self._content_frame.pack(fill="both", expand=True)

        self._internal = self._tk_toplevel

    def _child_master(self) -> Any:
        return self._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    # ----- Lifecycle -----

    def show(self) -> "Window":
        """Show the window and apply any modal grab.

        Returns:
            `self` — allows chaining: ``win = Window(...).show()``.
        """
        self._tk_toplevel.show()
        return self

    def block_until_closed(self) -> Any:
        """Show the window and block until it is destroyed.

        Returns:
            The value of `result` at the time the window was closed.
        """
        return self._tk_toplevel.block_until_closed()

    # ----- Properties -----

    @property
    def title(self) -> str:
        """The window's title bar text. Assigning to it updates the title live."""
        return self._tk_toplevel.title()

    @title.setter
    def title(self, value: str) -> None:
        self._tk_toplevel.title(value)

    @property
    def result(self) -> Any:
        """Value set before closing, returned by `block_until_closed()`."""
        return self._tk_toplevel.result

    @result.setter
    def result(self, value: Any) -> None:
        self._tk_toplevel.result = value