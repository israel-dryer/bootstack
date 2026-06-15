"""Core dialog base class for bootstack dialogs.

This module provides the base `Dialog` class using a builder pattern
for creating flexible, customizable dialogs with composition-based content
and footer builders.
"""

from __future__ import annotations

from dataclasses import dataclass
import tkinter
from tkinter import Widget
from typing import Any, Callable, Iterable, Literal, Mapping, Optional, Tuple, TypedDict, Union

from bootstack.widgets._impl.primitives.button import Button as _Button
from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack.widgets._impl.primitives.separator import Separator as _Separator
from bootstack.widgets.types import Master, AccentToken, ButtonVariant, SurfaceToken, WindowStyle
from bootstack._runtime.toplevel import Toplevel
from bootstack._runtime.window_utilities import AnchorPoint, WindowPositioning

# --- Types -----------------------------------------------------------------

ContentBuilder = Callable[[Widget], None]
FooterBuilder = Callable[[Widget], None]

ButtonRole = Literal["primary", "secondary", "danger", "cancel"]
DialogMode = Literal["modal", "popover", "sheet"]


@dataclass
class DialogButton:
    """Specification for a dialog button."""

    text: str
    """Button label text displayed to the user."""

    role: ButtonRole = "secondary"
    """Role that determines the button's styling and keyboard behavior. One of
    `'primary'` (main action, triggered by Enter when `default=True`),
    `'secondary'` (neutral action, no keyboard shortcut), `'danger'` (destructive
    action, not focused by default), or `'cancel'` (triggered by Escape)."""

    result: Any | None = None  # value assigned to dialog.result
    """Value assigned to `dialog.result` when clicked."""

    closes: bool = True  # close dialog after click
    """Whether the button closes the dialog when clicked."""

    default: bool = False  # default button (Enter)
    """Whether this is the default button (focused, triggered by Enter)."""

    command: Callable[[Dialog], None] | None = None
    """Callback invoked when clicked."""

    accent: AccentToken | str | None = None
    """Accent token for styling (e.g. `'primary'`, `'danger'`)."""

    variant: ButtonVariant | str | None = None
    """Button style variant — `'default'`, `'solid'`, `'outline'`, or `'ghost'`."""

    icon: str | dict[str, Any] | None = None  # passed straight to _Button(icon=...)
    """Optional icon specification for the button."""


ButtonSpec = Union[DialogButton, Mapping[str, Any]]


class ShowOptions(TypedDict, total=False):
    """Options for showing the dialog window.

    Attributes:
        position (tuple[int, int] | None): Optional (x, y) coordinates.
        modal (bool | None): Override the mode's default modality.
        anchor_to (Widget | str | None): Positioning target widget or string.
        anchor_point (AnchorPoint): Point on the anchor target.
        window_point (AnchorPoint): Point on the dialog window.
        offset (tuple[int, int]): Additional (x, y) offset in pixels.
        auto_flip (bool | str): Smart positioning to keep window on screen.
    """
    position: Optional[Tuple[int, int]]
    modal: Optional[bool]
    anchor_to: Optional[Union[Widget, Literal["screen", "cursor", "parent"]]]
    anchor_point: AnchorPoint
    window_point: AnchorPoint
    offset: Tuple[int, int]
    auto_flip: Union[bool, Literal['vertical', 'horizontal']]


# --- Dialog ----------------------------------------------------------------

class Dialog:
    """A flexible dialog window using the builder pattern.

    Dialog provides a composition-based approach to creating modal and non-modal
    dialogs with customizable content, buttons, and behavior. Instead of requiring
    inheritance, you provide callback functions to build the dialog content and
    optionally the footer.

    The dialog manages window creation, positioning, button handling, and keyboard
    shortcuts automatically.

    Attributes:
        result: The value returned by the dialog after closing.
            Set automatically when a button with a result value is clicked.
            Defaults to None.

    Args:
        title: Dialog window title. Defaults to `'bootstack'`.
        content_builder: Callback to build the dialog body. Receives an internal
            frame — place widgets into it using raw internal constructors or by
            calling `widget._internal` directly. If `None`, the dialog has
            no body area.
        footer_builder: Callback to build a fully custom footer. Replaces the
            standard button row when provided.
        buttons: List of `DialogButton` (or equivalent dicts) for the footer.
            Ignored when `footer_builder` is given. Buttons are displayed
            right-to-left — the first entry appears rightmost.
        min_size: Minimum window size as `(width, height)` in pixels.
        max_size: Maximum window size as `(width, height)` in pixels.
        resizable: `(width, height)` booleans controlling resize. Default
            `(False, False)`.
        alert: Play the system alert sound when the dialog is shown. Default
            `False`.
        mode: Interaction mode. `'modal'` (default) blocks the parent;
            `'popover'` closes on focus loss; `'sheet'` renders as a Cocoa
            sheet on macOS and falls back to modal elsewhere.
        undecorated: Remove OS window decorations. Useful for popover-style
            dialogs. Default `False`.
        window_style: Windows-only pywinstyles effect (`'mica'`, `'acrylic'`,
            `'aero'`, etc.). Defaults to the app's window style setting.
        on_close: Callback fired when the dialog is closed by any means (button
            click, X button, Escape, or focus loss in popover mode). Receives
            no arguments. Useful for non-modal dialogs where `show()` does
            not block.
        parent: Parent window. Defaults to the active root window.
    """

    def __init__(
            self,
            *,
            title: str = "bootstack",
            content_builder: Optional[ContentBuilder] = None,
            footer_builder: Optional[FooterBuilder] = None,
            buttons: Iterable[ButtonSpec] | None = None,
            min_size: tuple[int, int] | None = None,
            max_size: tuple[int, int] | None = None,
            resizable: tuple[bool, bool] | None = (False, False),
            alert: bool = False,
            mode: DialogMode = "modal",
            undecorated: bool = False,
            window_style: WindowStyle | str | None = None,
            on_close: Callable[[], Any] | None = None,
            surface: SurfaceToken | str | None = None,
            parent: Master = None,
    ):
        import tkinter
        self._master = parent if parent else tkinter._default_root
        self._title = title
        self._content_builder = content_builder
        self._footer_builder = footer_builder
        self._buttons: list[DialogButton] = self._normalize_buttons(buttons)

        self._minsize = min_size
        self._maxsize = max_size
        self._resizable = resizable
        self._alert = alert
        self._mode = mode
        self._undecorated = undecorated
        self._window_style = window_style
        self._on_close = on_close
        self._surface = surface

        self._toplevel: Toplevel | None = None
        self._content: _Frame | None = None
        self._footer: _Frame | None = None
        self._border_frame: _Frame | None = None

        self.result: Any = None

    # --------------------------------------------------------------- API

    def show(
            self,
            *,
            position: Optional[Tuple[int, int]] = None,
            modal: Optional[bool] = None,
            anchor_to: Optional[Union[Widget, Literal["screen", "cursor", "parent"]]] = None,
            anchor_point: AnchorPoint = 'center',
            window_point: AnchorPoint = 'center',
            offset: Tuple[int, int] = (0, 0),
            auto_flip: Union[bool, Literal['vertical', 'horizontal']] = False
    ):
        """Create and show the dialog with flexible positioning options.

        Args:
            position: Optional (x, y) coordinates to position the dialog.
                If provided, takes precedence over anchor-based positioning.
            modal: Override the mode's default modality. When `None`, follows the
                mode — `"modal"` grabs focus and waits for the dialog to close;
                `"popover"` waits without grabbing.
            anchor_to: Positioning target. A widget anchors to that widget;
                `"screen"` anchors to the screen edges/corners; `"cursor"` anchors
                to the mouse cursor; `"parent"` anchors to the parent window; and
                `None` (default) centers on the parent.
            anchor_point: Point on the anchor target (n, s, e, w, ne, nw, se, sw, center).
                Default 'center'.
            window_point: Point on the dialog window (n, s, e, w, ne, nw, se, sw, center).
                Default 'center'.
            offset: Additional (x, y) offset in pixels from the anchor position.
            auto_flip: Smart positioning to keep window on screen.
                - False: No flipping (default)
                - True: Flip both vertically and horizontally as needed
                - 'vertical': Only flip up/down
                - 'horizontal': Only flip left/right

        Positioning Logic:
            1. If position is provided: Use explicit coordinates
            2. If anchor_to is provided: Use anchor-based positioning
            3. Default: Center on parent window
        """
        if modal is None:
            modal = self._mode in ("modal", "sheet")

        self.result = None
        self._create_toplevel(modal=modal)
        self._build_footer()
        self._build_content()
        self._position_dialog(
            position=position,
            anchor_to=anchor_to,
            anchor_point=anchor_point,
            window_point=window_point,
            offset=offset,
            auto_flip=auto_flip
        )

        if self._alert:
            self._toplevel.bell()

        if self._mode == "popover":
            self._toplevel.bind("<FocusOut>", self._on_focus_out, add="+")

        if modal:
            # Sheets are inherently modal to their parent on Aqua via the
            # sheet window class; calling grab_set on top of that is fine
            # but unnecessary. Plain modal mode still uses grab to block
            # interaction with the parent on platforms without a sheet.
            if self._mode in ("modal", "sheet"):
                self._toplevel.grab_set()
            self._master.wait_window(self._toplevel)

    @property
    def toplevel(self) -> Toplevel | None:
        """Read-only access to the underlying toplevel window."""
        return self._toplevel

    # --------------------------------------------------------------- Internals

    def _normalize_buttons(
            self,
            buttons: Iterable[ButtonSpec] | None,
    ) -> list[DialogButton]:
        if not buttons:
            return []

        normalized: list[DialogButton] = []
        for b in buttons:
            if isinstance(b, DialogButton):
                normalized.append(b)
            else:
                # assume mapping/dict
                try:
                    normalized.append(DialogButton(**b))  # type: ignore[arg-type]
                except TypeError as exc:
                    raise ValueError(
                        f"Invalid button mapping {b!r}: {exc}"
                    ) from exc
        return normalized

    def _create_toplevel(self, modal: bool = True):
        # Pass transient to Toplevel so it's set before window_style is applied
        # (required for mica effect to work on Windows)
        self._toplevel = Toplevel(
            master=self._master,
            window_style=self._window_style,
            transient=self._master if modal else None
        )
        self._toplevel.title(self._title)
        self._toplevel.protocol("WM_DELETE_WINDOW", self._on_close_request)
        if self._on_close:
            self._toplevel.bind("<Destroy>", self._on_toplevel_destroy)

        try:
            self._toplevel.withdraw()
        except Exception:
            pass

        # Sheet mode: on Aqua, apply the Cocoa 'sheet' window class so the
        # dialog renders chromeless and tied to its parent. Must be set
        # before the window is mapped, hence here while still withdrawn.
        # On non-Aqua, sheet mode is treated as plain modal — there's no
        # cross-platform equivalent of a Cocoa sheet.
        if self._mode == "sheet" and getattr(self._toplevel, 'winsys', None) == 'aqua':
            try:
                self._toplevel.tk.call(
                    '::tk::unsupported::MacWindowStyle', 'style',
                    self._toplevel, 'sheet', 'none',
                )
            except tkinter.TclError:
                pass

        if self._minsize:
            self._toplevel.minsize(*self._minsize)
        if self._maxsize:
            self._toplevel.maxsize(*self._maxsize)
        if self._resizable is not None:
            self._toplevel.resizable(*self._resizable)

        if self._undecorated:
            self._toplevel.overrideredirect(True)
            self._border_frame = _Frame(self._toplevel, show_border=True, padding=2)
            self._border_frame.pack(fill='both', expand=True)

    def _build_content(self):
        parent = self._border_frame if self._undecorated else self._toplevel
        padding = 2 if self._undecorated else 0
        kw = {"padding": padding}
        if self._surface:
            kw["surface"] = self._surface
        self._content = _Frame(parent, **kw)

        if self._undecorated:
            self._content.pack(fill="both", side="top", expand=False)
        else:
            self._content.pack(fill="both", side="top", expand=True)

        if self._content_builder:
            self._content_builder(self._content)

    def _build_footer(self):
        parent = self._border_frame if self._undecorated else self._toplevel
        footer_padding = 6 if self._undecorated else 4

        footer_kw = {"padding": footer_padding}
        if self._surface:
            footer_kw["surface"] = self._surface

        if self._footer_builder:
            self._footer = _Frame(parent, **footer_kw)
            self._footer.pack(side="bottom", fill="x")
            _Separator(parent, orient="horizontal").pack(side="bottom", fill="x")
            self._footer_builder(self._footer)
            return

        if not self._buttons:
            return

        self._footer = _Frame(parent, **footer_kw)
        self._footer.pack(side="bottom", fill="x")
        _Separator(parent, orient="horizontal").pack(side="bottom", fill="x")

        self._create_standard_buttons(self._footer)

    def _create_standard_buttons(self, parent: Widget):
        """Create standardized footer buttons from self._buttons.

        Buttons are packed right-to-left so first button appears rightmost.
        """
        default_button: _Button | None = None
        cancel_button: _Button | None = None

        for spec in reversed(self._buttons):
            # Get accent/variant from spec or derive from role
            if spec.accent or spec.variant:
                accent, variant = spec.accent, spec.variant
            else:
                accent, variant = self._style_for_role(spec.role)

            def make_command(s: DialogButton):
                def cmd():
                    if s.command:
                        s.command(self)
                    if s.result is not None:
                        self.result = s.result
                    if s.closes and self._toplevel:
                        self._toplevel.destroy()

                return cmd

            btn = _Button(
                parent,
                text=spec.text,
                accent=accent,
                variant=variant,
                command=make_command(spec),
                icon=spec.icon,
                compound="left" if spec.icon else "text",
            )
            btn.pack(side="right")

            if spec.default and default_button is None:
                default_button = btn
            if spec.role == "cancel" and cancel_button is None:
                cancel_button = btn

        if self._toplevel is None:
            return

        if default_button is not None:
            default_button.focus_set()
            self._toplevel.bind("<Return>", lambda e, b=default_button: b.invoke())

        if cancel_button is not None:
            self._toplevel.bind("<Escape>", lambda e, b=cancel_button: b.invoke())
        else:
            self._toplevel.bind("<Escape>", lambda e: self._toplevel.destroy())

    def _position_dialog(
            self,
            position: Optional[Tuple[int, int]] = None,
            anchor_to: Optional[Union[Widget, Literal["screen", "cursor", "parent"]]] = None,
            anchor_point: AnchorPoint = 'center',
            window_point: AnchorPoint = 'center',
            offset: Tuple[int, int] = (0, 0),
            auto_flip: Union[bool, Literal['vertical', 'horizontal']] = False
    ) -> None:
        """Position the dialog window using consolidated positioning logic.

        Positioning logic:
        1. If position is provided: Use explicit coordinates
        2. If anchor_to is provided: Use anchor-based positioning
        3. Default: Center on parent
        """
        if not self._toplevel:
            return

        # Priority 1: Explicit position coordinates
        if position is not None:
            x, y = position
            x, y = WindowPositioning.ensure_on_screen(self._toplevel, int(x), int(y))
            self._toplevel.geometry(f"+{x}+{y}")

        # Priority 2: Anchor-based positioning
        elif anchor_to is not None:
            WindowPositioning.position_anchored(
                window=self._toplevel,
                anchor_to=anchor_to,
                parent=self._master,
                anchor_point=anchor_point,
                window_point=window_point,
                offset=offset,
                auto_flip=auto_flip,
                ensure_visible=True
            )

        # Priority 3: Default - center on parent
        else:
            WindowPositioning.position_window(
                window=self._toplevel,
                position=None,
                parent=self._master,
                center_on_parent=True,
                ensure_visible=True
            )

        # Apply window style while still withdrawn, right before showing.
        # The update() call is here so pywinstyles can attach to a fully
        # realized HWND on Windows; on Aqua (and X11) it serves no purpose
        # and can hang indefinitely flushing children's pending events
        # (e.g. FontDialog's Treeview with hundreds of tag-configure font
        # calls), so gate it on the platform that actually needs it.
        self._toplevel.update_idletasks()
        self._toplevel._apply_window_style()
        if getattr(self._toplevel, 'winsys', None) == 'win32':
            self._toplevel.update()
        self._toplevel.deiconify()

        # Second centering pass for default positioning (handles dynamic sizing)
        if position is None and anchor_to is None:
            try:
                x, y = WindowPositioning.center_on_parent(self._toplevel, self._master)
                x, y = WindowPositioning.ensure_on_screen(self._toplevel, x, y)
                self._toplevel.geometry(f"+{x}+{y}")
            except Exception:
                pass

    # --------------------------------------------------------------- Event Handlers

    def _on_toplevel_destroy(self, event) -> None:
        if event.widget is self._toplevel and self._on_close:
            self._on_close()

    def _on_focus_out(self, _event):
        """For popover mode: close when focus leaves the dialog."""
        if self._mode != "popover" or not self._toplevel:
            return

        new_focus = self._toplevel.focus_get()

        if new_focus is None:
            self._toplevel.destroy()
            return

        if not str(new_focus).startswith(str(self._toplevel)):
            self._toplevel.destroy()

    def _on_close_request(self):
        if self._toplevel:
            self._toplevel.destroy()

    # --------------------------------------------------------------- Helpers

    def _style_for_role(self, role: ButtonRole) -> tuple[str | None, str | None]:
        """Return (accent, variant) tuple for a button role."""
        if role == "primary":
            return ("primary", None)
        if role == "secondary":
            return ("default", None)
        if role == "danger":
            return ("danger", None)
        if role == "cancel":
            return ("default", "outline")
        return ("default", None)
