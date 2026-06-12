from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal

from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill
from bootstack.widgets._core.window_controls import WindowControlsMixin
from bootstack.widgets._core.window_menu import ChromeHostMixin
from bootstack.widgets.types import Padding, Fill, Anchor, SurfaceToken, WindowStyle

if TYPE_CHECKING:
    from bootstack.images import AppIcon, Image


def _resolve_window_parent(parent: Any) -> Any:
    """Resolve a public widget (or tk widget) to its containing tk window.

    Accepts an `App`, a `Window`, or any widget inside one, and returns the
    enclosing toplevel — so centering and transient-parenting act on the window,
    not on a small child widget.
    """
    if parent is None:
        return None
    widget = None
    for attr in ("_tk_root", "_tk_toplevel", "_internal"):
        widget = getattr(parent, attr, None)
        if widget is not None:
            break
    if widget is None:
        widget = parent  # assume it is already a tk widget
    try:
        return widget.winfo_toplevel()
    except Exception:
        return widget


def _resolve_anchor_widget(target: Any) -> Any:
    """Resolve an anchor target to a tk widget (keeping it, not its toplevel).

    A string (`'screen'`/`'cursor'`/`'parent'`) passes through; a public widget
    resolves to the underlying tk widget so a window can be placed relative to
    that exact widget (e.g. beside a field).
    """
    if isinstance(target, str) or target is None:
        return target
    for attr in ("_tk_toplevel", "_tk_root", "_internal"):
        widget = getattr(target, attr, None)
        if widget is not None:
            return widget
    return target


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
        icon: Title-bar and taskbar icon — an icon file path, an `Image` handle,
            or an `AppIcon`. Defaults to the bootstack icon.
        position: Initial position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(width, height)`.
        modal: Modality level. `False` — non-modal (default). `True` or
            `'window'` — grabs input from the parent only. `'app'` — grabs
            input from all windows.
        parent: The window this one belongs to — an `App`, another `Window`, or
            any widget inside one. Makes this window transient to it (stacks
            above it, hides with it) and is the target for `center_on_parent`.
            Defaults to the main application window.
        center_on_parent: Center over `parent` (the main window if `parent` is
            not given).
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
        icon: "str | Image | AppIcon | None" = None,
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        modal: Literal[False, True, "window", "app"] = False,
        parent: Any = None,
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

        parent_widget = _resolve_window_parent(parent)
        self._parent_window = parent_widget
        if parent_widget is not None:
            init_kwargs["transient"] = parent_widget

        from bootstack.widgets._core.image_binding import resolve_window_icon

        icon_path, icon_image = resolve_window_icon(icon)
        if icon_path is not None:
            init_kwargs["icon"] = icon_path
        init_kwargs.update(kwargs)

        self._tk_toplevel = _InternalToplevel(**init_kwargs)

        # An Image handle needs the window to exist before it can be rendered.
        self._window_icon_photo = None
        if icon_image is not None:
            self._window_icon_photo = icon_image._materialize()
            self._tk_toplevel._setup_icon(self._window_icon_photo)

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

    def show(
        self,
        *,
        anchor_to: Any = None,
        anchor_point: Anchor = "center",
        window_point: Anchor = "center",
        offset: tuple[int, int] = (0, 0),
        auto_flip: bool = True,
    ) -> "Window":
        """Show the window, optionally positioned relative to a widget.

        With no arguments the window appears at its configured position (or
        centered on its `parent`). Pass `anchor_to` to place it relative to a
        widget instead — for example, to the right of a field.

        Args:
            anchor_to: A widget to position this window against, or one of
                `'screen'`, `'cursor'`, or `'parent'`. When given, this overrides
                centering.
            anchor_point: The point on the anchor target to align to — one of
                `'n'`, `'s'`, `'e'`, `'w'`, `'ne'`, `'nw'`, `'se'`, `'sw'`, or
                `'center'`. For example, `'e'` is the target's right edge.
            window_point: The matching point on this window placed at the anchor
                (same value set). For example, `anchor_point='e'` with
                `window_point='w'` puts this window's left edge at the target's
                right edge — i.e. to its right.
            offset: Extra `(x, y)` pixel offset from the anchored position.
            auto_flip: Flip to the opposite side if the window would otherwise go
                off-screen. Defaults to `True`.

        Returns:
            `self` — allows chaining: ``win = Window(...).show()``.
        """
        if anchor_to is not None:
            from bootstack._runtime.window_utilities import WindowPositioning

            toplevel = self._tk_toplevel
            toplevel.update_idletasks()
            WindowPositioning.position_anchored(
                window=toplevel,
                anchor_to=_resolve_anchor_widget(anchor_to),
                parent=self._parent_window,
                anchor_point=anchor_point,
                window_point=window_point,
                offset=offset,
                auto_flip=auto_flip,
                ensure_visible=True,
            )
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