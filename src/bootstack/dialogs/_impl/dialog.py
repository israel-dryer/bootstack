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

from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._impl.primitives.button import Button as _Button
from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack.widgets._impl.primitives.separator import Separator as _Separator
from bootstack.widgets.types import Master, AccentToken, ButtonVariant, Padding, SurfaceToken, WindowStyle
from bootstack._runtime.toplevel import Toplevel
from bootstack._runtime.window_utilities import AnchorPoint, WindowPositioning

# --- Types -----------------------------------------------------------------

# Called to fill the dialog body. The dialog content area is a public container
# pushed as the active parent, so the builder can create widgets directly (no
# `parent=`). It is also passed the content container, so a builder that wants an
# explicit handle can declare a single parameter (`def build(content): ...`).
ContentBuilder = Callable[..., None]
FooterBuilder = Callable[[Widget], None]

# Where a dialog can anchor itself. A public widget anchors to that widget; the
# string forms anchor to the screen, the cursor, or the parent window.
AnchorTarget = Union["PublicWidgetBase", Literal["screen", "cursor", "parent"]]


def _resolve_anchor_target(anchor_to: Any) -> Any:
    """Unwrap a public widget to its underlying tk widget for positioning.

    A public bootstack widget is a plain object holding `_internal`, not a tk
    widget — so positioning (which reads `winfo_*`) needs the internal handle.
    String forms (`'screen'`/`'cursor'`/`'parent'`) and `None` pass through.
    """
    internal = getattr(anchor_to, "_internal", None)
    return internal if internal is not None else anchor_to


def _call_builder(builder: Callable[..., None], content: Any) -> None:
    """Call a content builder, passing the content container only if it takes one.

    Supports both the idiomatic parent-free form (`def build(): ...`, run inside
    the content container's context) and an explicit form (`def build(content):
    ...`). Falls back to passing the argument if the signature can't be read.
    """
    import inspect

    try:
        params = inspect.signature(builder).parameters.values()
        takes_arg = any(
            p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL)
            for p in params
        )
    except (TypeError, ValueError):
        takes_arg = True
    builder(content) if takes_arg else builder()

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

    default: bool = False  # default button (Enter)
    """Whether this is the default button (focused, triggered by Enter)."""

    command: Callable[[Dialog], Any] | None = None
    """Callback invoked when clicked. Returning `False` refuses the press — no
    result is recorded, and a dialog stays open — which is how a button rejects
    the input it was given. Any other return value, including `None`, accepts
    it. The same applies wherever these specifications are used, including the
    button row of a `Form`."""

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
        anchor_to (PublicWidgetBase | str | None): Positioning target widget or string.
        anchor_point (AnchorPoint): Point on the anchor target.
        window_point (AnchorPoint): Point on the dialog window.
        offset (tuple[int, int]): Additional (x, y) offset in pixels.
        auto_flip (bool | str): Smart positioning to keep window on screen.
    """
    position: Optional[Tuple[int, int]]
    modal: Optional[bool]
    anchor_to: Optional[AnchorTarget]
    anchor_point: AnchorPoint
    window_point: AnchorPoint
    offset: Tuple[int, int]
    auto_flip: Union[bool, Literal['vertical', 'horizontal']]


# --- Dialog result delivery -------------------------------------------------

DIALOG_RESULT = "<<DialogResult>>"


def result_target(dialog: "Dialog", master: Optional[tkinter.Misc]) -> Optional[tkinter.Misc]:
    """The widget `<<DialogResult>>` is bound on and fired from.

    Binding and firing both route through here so the two cannot resolve
    differently. That mattered: `Dialog.toplevel` is `None` before `show()`
    and a *destroyed* widget after it, because nothing resets `_toplevel`
    when the modal wait ends. A target derived from it is therefore never
    live at both ends — subscribers bound to the master while the result
    fired at a dead toplevel, where `event_generate` raised and the error
    was swallowed (#397).

    `master` comes first for that reason: it outlives the dialog.

    Args:
        dialog: The dialog producing the result.
        master: The dialog's master widget, if it has one.

    Returns:
        A live widget, or `None` when there is nothing left to fire on.
    """
    if master is not None:
        return master
    top = dialog.toplevel
    if top is not None and top.winfo_exists():
        return top
    return None


def emit_dialog_result(target: Optional[tkinter.Misc], payload: dict) -> None:
    """Fire `<<DialogResult>>` on `target` with `payload` attached.

    Args:
        target: The widget from `result_target`, or `None` to do nothing.
        payload: Mapping with `result` and `confirmed` keys.
    """
    if target is None:
        return
    try:
        target.event_generate(DIALOG_RESULT, data=payload)
    except tkinter.TclError:
        # `result_target` hands back a live widget, so reaching here means it
        # was destroyed in between. Nothing can receive the result; surface it
        # in development rather than letting it vanish the way it used to.
        from bootstack._runtime.utility import debug_log_exception
        debug_log_exception(f"could not deliver {DIALOG_RESULT}")


# --- Dialog ----------------------------------------------------------------

def restore_grab(previous: Any) -> None:
    """Hand the modal grab back to whatever held it before this dialog took it.

    Tk releases a grab when the window holding it is destroyed, but it does NOT
    restore the grab that window displaced. So a modal opened from inside
    another modal — `bs.alert()` from a dialog button command, or
    `QueryDialog._on_submit` — took the grab over and then dropped it on the
    floor when it closed. The OUTER dialog was left on screen and still
    blocking its caller inside `show()`, yet holding no grab at all: the user
    could click straight back into the main window and drive the app
    underneath it, against a dialog that was modal in appearance only
    (issue #440).

    Pass the value `grab_current()` returned BEFORE `grab_set()`. `None` means
    nothing held the grab, which is the outermost case and needs no restore.

    A failure here is deliberately swallowed. This runs on a teardown path,
    where the previous holder may itself have been destroyed while the inner
    dialog was up, or the whole interpreter may be going down — and a dialog
    that has already closed must not raise on its way out.
    """
    if previous is None:
        return
    try:
        if previous.winfo_exists():
            previous.grab_set()
    except (AttributeError, tkinter.TclError):
        pass


# Bindtags whose widgets treat Enter as CONTENT rather than as a command.
# `Text` is Tk's multi-line text class, which `TextArea` and `CodeEditor` are
# both built on — naming the class covers them, and anything else Text-backed,
# without listing widgets.
_ENTER_IS_CONTENT = frozenset({"Text"})


def _key_was_consumed(widget: Any) -> bool:
    """Did `widget` already answer the Return key by the time it reached us?

    A dialog binds Return on its TOPLEVEL so the default button can be pressed
    from an input field. The toplevel is last in the bindtag walk, so by the
    time that binding runs a widget-level or class-level handler has already
    had the key — and firing the default button on top of it either invokes the
    same button twice or runs the default button's command over the one the
    user actually pressed.

    Two kinds of widget answer Enter, and the rule names the intent rather than
    inferring it:

    * a **button** invokes. bootstack installs `TButton <Key-Return>` ->
      `button_default_binding` at app construction (`_runtime/app.py:151`).
    * a **multi-line text widget** inserts a newline. That is issue #441: the
      newline went in and the dialog then closed on top of it, because the
      guard recognized only buttons.

    In both cases a DISABLED widget is the exception: its class binding runs
    but does nothing — `invoke` is a no-op on a disabled button, and
    `tk::TextInsert` returns early on a disabled text (both measured,
    `development/probe_441_key_already_handled.py`). Nothing answered the key,
    so the default button should still get it. Standing down there would leave
    the keyboard dead for the whole dialog.

    ⚠ INTERROGATING THE BINDINGS INSTEAD WAS TRIED AND IS WRONG — do not
    re-propose it as the "general" rule. Asking whether any bindtag carries a
    real binding for the key looks principled and misclassifies the control:
    bootstack's own `TextField` binds `<Return>` as an instance binding to emit
    its `submit` event, so a plain entry reads as "already handled" and
    `ask_string()` stops submitting. Tk also binds `TEntry <Return>` to the
    literal script `# nothing`, so a non-empty script does not mean the key was
    handled either. Binding inspection cannot separate binds-to-notify from
    binds-to-consume; the class name is where that intent is recorded.
    """
    try:
        tags = {str(tag) for tag in widget.bindtags()}
    except (AttributeError, tkinter.TclError):
        # Nothing identifiable answered the key, so let the default button run
        # rather than silently swallowing Enter for the whole dialog.
        return False

    if "TButton" in tags:
        try:
            return not widget.instate(["disabled"])
        except (AttributeError, tkinter.TclError):
            return True

    if tags & _ENTER_IS_CONTENT:
        try:
            return str(widget.cget("state")) == "normal"
        except (AttributeError, tkinter.TclError):
            return True

    return False


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
        content_builder: Callback to build the dialog body. The content area is a
            public container set as the active parent, so the callback creates
            widgets directly — no `parent=` needed, like an `App` body. Declare a
            single parameter (`def build(content): ...`) to also receive the
            content container. If `None`, the dialog has no body area.
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
        padding: Space in pixels between the dialog body edge and its content.
            Defaults to `20`.
        gap: Space in pixels between stacked content widgets. Defaults to `8`.
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
            padding: Padding = 20,
            gap: int = 8,
            parent: Master = None,
            _raw_content: bool = False,
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
        self._content_padding = padding
        self._content_gap = gap
        # Internal builders (the built-in verbs, FormDialog, …) render with raw
        # primitives and want the bare content frame; public content_builders get
        # the parent-free public container.
        self._raw_content = _raw_content

        self._toplevel: Toplevel | None = None
        self._content: _Frame | None = None
        self._content_area: Any = None
        self._footer: _Frame | None = None
        self._border_frame: _Frame | None = None

        # Who gets focus when the window comes up. `_focus_target` is the
        # override a content builder can claim (QueryDialog's entry); the
        # default button is the fallback. Resolved once in `show()`, after
        # content is built, so the two cannot race — see `_focus_when_mapped`.
        self._default_button: _Button | None = None
        self._focus_target: Widget | None = None

        self.result: Any = None

    # --------------------------------------------------------------- API

    def show(
            self,
            *,
            position: Optional[Tuple[int, int]] = None,
            modal: Optional[bool] = None,
            anchor_to: Optional[AnchorTarget] = None,
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
            anchor_to: Positioning target. A widget (e.g. a `bs.Button`) anchors to
                that widget; `"screen"` anchors to the screen edges/corners;
                `"cursor"` anchors to the mouse cursor; `"parent"` anchors to the
                parent window; and `None` (default) centers on the parent.
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

        # Resolve initial focus once, now that both halves exist. A content
        # widget that claimed `_focus_target` wins; otherwise the default
        # button takes it, which is what `DialogButton.default` promises.
        # Deferred to <Map> because the window is still withdrawn here and
        # `focus_set()` is a silent no-op until it is not (issue #439).
        focus_target = self._focus_target or self._default_button
        if focus_target is not None:
            self._focus_when_mapped(focus_target)

        self._position_dialog(
            position=position,
            anchor_to=_resolve_anchor_target(anchor_to),
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
            previous_grab = None
            if self._mode in ("modal", "sheet"):
                # Remember who held the grab so it can be handed back — a
                # nested modal must not leave its opener non-modal (#440).
                previous_grab = self._toplevel.grab_current()
                self._toplevel.grab_set()
            try:
                self._master.wait_window(self._toplevel)
            finally:
                restore_grab(previous_grab)

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
            if self._raw_content:
                # Internal builders render with raw primitives into the frame.
                self._content_builder(self._content)
                return

            from bootstack.widgets.stacks import Column

            # Public content area the builder fills — set as the active parent so
            # the body needs no `parent=`, like an App body. It is hosted in the
            # content frame via the raw-Tk-parent bridge in `_resolve_parent`.
            self._content_area = Column(
                parent=self._content,
                padding=self._content_padding,
                gap=self._content_gap,
            )
            with self._content_area:
                _call_builder(self._content_builder, self._content_area)

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
                    # A command returning False refuses the press: the dialog
                    # neither records a result nor closes. Without this, a
                    # command that declines to act (a form failing validation,
                    # say) still stamps its button's result, and that value
                    # outlives the press — a later cancel cannot clear it,
                    # because a cancel button's own result is None and the write
                    # below is skipped for None.
                    if s.command and s.command(self) is False:
                        return
                    if s.result is not None:
                        self.result = s.result
                    # `winfo_exists` rather than a bare truth test: a command is
                    # free to close the dialog itself, and destroying an already
                    # destroyed toplevel raises.
                    if self._toplevel and self._toplevel.winfo_exists():
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
            # Recorded, not focused here: `show()` resolves focus after the
            # content is built, so a content widget asking for initial focus
            # is not overruled by build order (issue #439).
            self._default_button = default_button
            top = self._toplevel

            def press_default(event: Any, b: Any = default_button) -> None:
                """Press the default button, unless a button already has.

                This binding lives on the toplevel, so it runs for every key
                press anywhere in the dialog. A press delivered to a button has
                already invoked that button by the time the bindtag walk
                reaches here — buttons carry a class binding for Return and
                KP_Enter — so firing again would either invoke the same button
                twice or, with focus on some OTHER button, run the default
                button's command on top of the one the user actually pressed.
                Standing down is also what makes keyboard traversal mean
                something: Enter presses the button you tabbed to.

                A DISABLED button is the exception: its class binding runs but
                `invoke` does nothing, so nothing has answered the key and the
                default button should still get it. Standing down there would
                leave the keyboard dead for the whole dialog — which is what a
                content button that greys itself out on click would cause.

                A multi-line text widget answers Enter too, by inserting a
                newline, and standing down for it is issue #441 — the newline
                went in and the dialog closed on top of it. `_key_was_consumed`
                owns that decision for both kinds of widget.

                The remaining case is the one this binding exists for — focus
                in an entry, as in `QueryDialog`, where nothing else would
                answer the key.
                """
                if _key_was_consumed(event.widget):
                    return
                b.invoke()

            # The keypad Enter key reports `KP_Enter`, a separate keysym from
            # `Return` on Windows, X11 and Aqua alike, so it needs its own
            # binding to reach the default button from an input field.
            for key in ("<Return>", "<KP_Enter>"):
                self._toplevel.bind(key, press_default)

        if cancel_button is not None:
            self._toplevel.bind("<Escape>", lambda e, b=cancel_button: b.invoke())
        else:
            self._toplevel.bind("<Escape>", lambda e: self._toplevel.destroy())

    @staticmethod
    def _focus_when_mapped(widget: Widget) -> None:
        """Focus `widget` once it is actually mapped.

        `focus_set()` is a SILENT no-op while the widget's toplevel is
        withdrawn: `TkSetFocusWin` walks the ancestry and returns without
        setting anything, reporting nothing. Footer buttons are built from
        `_build_footer`, which runs while `_create_toplevel` still has the
        window withdrawn, so focusing the default button there never took —
        `focus_lastfor()` kept naming the toplevel, leaving keyboard users
        with no focus ring and a Tab order starting from nowhere, in a dialog
        documented as focusing its default button (issue #439).

        Waiting for the widget's own `<Map>` states that precondition instead
        of guessing a delay. Measured on Windows
        (`development/probe_439_focus_timing.py`): the button is still
        unmapped once `deiconify()` AND `update_idletasks()` have both
        returned, so neither is a usable barrier. Asking after the toplevel is
        deiconified happens to work — Tk defers a request made against a
        mapped toplevel — but that deferral is a Tk implementation detail and
        window managers map asynchronously, so the explicit wait is what
        travels off this box.

        Binding on the widget rather than scheduling on the root is
        deliberate: a `<Map>` binding is torn down with the widget it is on,
        so a dialog closed before it ever maps leaves nothing pending. An
        `after` timer would outlive the widget and fire as an orphan.
        """
        if widget.winfo_ismapped():
            widget.focus_set()
            return

        def on_map(_event: Any = None) -> None:
            # One-shot: the default button should not reclaim focus every time
            # the dialog is unmapped and remapped (minimize/restore), which
            # would yank focus off whatever the user had tabbed to.
            try:
                widget.unbind("<Map>", bind_id)
            except tkinter.TclError:
                pass
            try:
                if widget.winfo_exists():
                    widget.focus_set()
            except tkinter.TclError:
                pass

        bind_id = widget.bind("<Map>", on_map, add="+")

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
            return "primary", None
        if role == "secondary":
            return "default", None
        if role == "danger":
            return "danger", None
        if role == "cancel":
            return "default", "outline"
        return "default", None
