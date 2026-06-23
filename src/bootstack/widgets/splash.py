from __future__ import annotations

import tkinter
from typing import TYPE_CHECKING, Any, Callable, Literal, overload

from bootstack.errors import BootstackError
from bootstack.events import Subscription
from bootstack.events._payloads import SplashDismissEvent
from bootstack.widgets._core.container import FlexContainer
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Padding, SurfaceToken

if TYPE_CHECKING:
    from bootstack.streams import Stream


# Fade ramp: ~250ms over 12 steps. Tuned for a soft, quick in/out that never
# feels like a stall; degrades to an instant snap where alpha isn't honored.
_FADE_STEPS = 12
_FADE_INTERVAL_MS = 20


class Splash(FlexContainer):
    """A borderless app intro screen shown while the main window is built.

    Constructing a `Splash` inside an `App` context registers it with that app
    and shows it; the app then defers revealing its own window until the splash
    dismisses. Author the splash's contents — a logo, a title, a status line —
    inside its `with` block exactly as you would the app body::

        with bs.App(title="My App") as app:
            with bs.Splash(min_duration=1.0):
                bs.Picture(logo)
                bs.Label("My App", font="heading-lg")
                bs.Label("Loading…", textsignal=status)
            # ...build the heavy app body — the splash covers this cost...
        app.run()

    Where you write the `Splash` determines how much of startup it covers: put
    it first to cover the most. The `with` block scopes content authoring only —
    it does not bound the splash's lifetime, which is governed by `until`,
    `min_duration`, `skippable`, and `dismiss()`.

    Args:
        until: What automatically closes the splash. `'ready'` (default) closes
            it when the app finishes building. A number of seconds closes it
            after that delay (app-ready does not auto-close it). `'manual'` never
            auto-closes — use `skippable`, an authored button, or `dismiss()`.
        skippable: When `True`, a click or the Escape key dismisses the splash.
        min_duration: A floor in seconds — the splash never closes before this
            has elapsed, even if its trigger fires sooner (prevents a blink on a
            fast startup).
        fade: Fade the window in and out where the platform supports window
            alpha; snap instantly where it does not.
        size: Fixed size as `(width, height)`. Defaults to auto-fitting the
            content. Either way the splash is centered on screen.
        surface: Surface token for the panel background.
        padding: Inner content padding.
        gap: Spacing between content items.
    """

    _auto_place = False  # its own top-level window — no parent manages it

    def __init__(
        self,
        *,
        until: float | Literal["ready", "manual"] = "ready",
        skippable: bool = False,
        min_duration: float = 0.0,
        fade: bool = True,
        size: tuple[int, int] | None = None,
        surface: SurfaceToken | str = "card",
        padding: Padding = 24,
        gap: int = 12,
    ) -> None:
        from bootstack._runtime.app import get_current_app
        from bootstack._runtime.toplevel import Toplevel as _InternalToplevel

        self._parent = None

        # ----- Resolve & register on the ambient app -----
        try:
            app = get_current_app()
        except RuntimeError:
            app = None
        if app is None:
            raise BootstackError(
                "Splash requires an App — construct it inside a "
                "`with bs.App(...) as app:` block."
            )
        if getattr(app, "_splash", None) is not None:
            raise BootstackError(
                "An app can show only one Splash. A second Splash was "
                "constructed before the first dismissed."
            )
        self._app = app
        app._splash = self

        # ----- Dismiss model -----
        if isinstance(until, bool):  # bool is an int subclass — reject explicitly
            raise BootstackError(
                f"Splash until= must be 'ready', 'manual', or a number of "
                f"seconds; got {until!r}."
            )
        if isinstance(until, (int, float)):
            self._until: str = "timer"
            self._until_seconds: float | None = float(until)
        elif until in ("ready", "manual"):
            self._until = until
            self._until_seconds = None
        else:
            raise BootstackError(
                f"Splash until= must be 'ready', 'manual', or a number of "
                f"seconds; got {until!r}."
            )

        self._skippable = skippable
        self._min_duration = max(0.0, float(min_duration))
        self._fade = fade
        self._size = size

        # ----- Lifecycle state -----
        self._shown = False          # _reveal() has run (idempotent guard)
        self._is_showing = False     # mapped and not yet dismissed
        self._dismissing = False     # _begin_dismiss() has run
        self._min_elapsed = self._min_duration <= 0.0
        self._pending_reason: str | None = None
        self._app_reveal: Callable[[], Any] | None = None

        # ----- Build the borderless top-level -----
        # windowtype='splash' is the single cross-platform switch (#308):
        # overrideredirect on Windows, MacWindowStyle on macOS, -type on X11.
        # topmost keeps it above the (still-hidden) app window.
        self._tk_toplevel = _InternalToplevel(
            title="",
            windowtype="splash",
            overrideredirect=True,
            topmost=True,
        )
        self._internal = self._tk_toplevel

        # A 1px themed border frames the panel so it reads as an intentional
        # surface rather than blending into a same-colored desktop.
        self._region_root = Frame(self._tk_toplevel, show_border=True, padding=1)
        self._region_root.pack(fill="both", expand=True)

        # Content is centered both ways — the classic splash composition.
        self._content_frame = FlexFrame(
            self._region_root,
            direction="vertical",
            padding=padding,
            gap=gap,
            horizontal_items="center",
            vertical_items="center",
            surface=surface,
        )
        self._content_frame.pack(fill="both", expand=True)

        if self._skippable:
            self._tk_toplevel.bind("<Escape>", self._on_skip, add="+")
            self._tk_toplevel.bind("<Button-1>", self._on_skip, add="+")

    @property
    def _flex_frame(self) -> Any:
        return self._content_frame

    # ----- Context manager: author content, then reveal -----------------------

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        # Reveal AFTER the content is authored so centering uses the real size.
        # Showing here (not at construction) means the splash is painted before
        # the synchronous body build that follows the block — so it genuinely
        # covers that cost.
        if exc_type is None:
            self._reveal()
        return None

    # ----- Public surface ------------------------------------------------------

    @property
    def is_showing(self) -> bool:
        """Whether the splash is currently on screen."""
        return self._is_showing

    def dismiss(self) -> None:
        """Dismiss the splash now, fading out and revealing the app.

        Respects `min_duration` — if the floor has not elapsed, the dismissal is
        deferred until it has. Safe to call more than once; later calls are
        ignored once a dismissal is under way.
        """
        self._request_dismiss("manual")

    @overload
    def on_dismiss(self) -> "Stream": ...
    @overload
    def on_dismiss(self, handler: Callable[[SplashDismissEvent], Any]) -> Subscription: ...
    def on_dismiss(
        self,
        handler: Callable[[SplashDismissEvent], Any] | None = None,
    ) -> "Stream | Subscription":
        """Register a callback fired when the splash begins dismissing.

        The handler receives a :class:`~bootstack.events.SplashDismissEvent`
        whose `reason` says why it closed (`'ready'`, `'timer'`, `'manual'`, or
        `'skip'`). Fires once, as the fade-out starts.

        Args:
            handler: Called with the dismiss event. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("dismiss", handler)

    # ----- App integration -----------------------------------------------------

    def _notify_app_ready(self, reveal: Callable[[], Any]) -> None:
        """Called by the app when it is built and ready to be revealed.

        Stores the reveal callback so the splash can trigger it when it
        dismisses. Under `until='ready'` this also kicks off the dismissal.
        """
        if not self._is_showing:
            # Never shown (constructed without a `with` block) or already gone —
            # don't strand the app; reveal it now and drop any orphan splash.
            self._app_reveal = None
            self._clear_registration()
            try:
                self._tk_toplevel.destroy()
            except tkinter.TclError:
                pass
            reveal()
            return
        self._app_reveal = reveal
        if self._until == "ready":
            self._request_dismiss("ready")

    # ----- Reveal --------------------------------------------------------------

    def _reveal(self) -> None:
        if self._shown:
            return
        self._shown = True
        top = self._tk_toplevel
        top.update_idletasks()

        if self._size is not None:
            top.geometry(f"{int(self._size[0])}x{int(self._size[1])}")
            top.update_idletasks()

        from bootstack._runtime.window_utilities import WindowPositioning

        x, y = WindowPositioning.center_on_screen(top)
        x, y = WindowPositioning.ensure_on_screen(top, x, y)
        top.geometry(f"+{x}+{y}")

        if self._fade:
            try:
                top.attributes("-alpha", 0.0)
            except tkinter.TclError:
                self._fade = False

        top.deiconify()
        top.lift()
        try:
            top.focus_set()
        except tkinter.TclError:
            pass
        # Force a paint now so the splash is on screen before the synchronous
        # body build that follows the `with` block.
        top.update()
        self._is_showing = True

        if self._fade:
            self._fade_in(1)
        self._start_timers()

    def _start_timers(self) -> None:
        top = self._tk_toplevel
        if self._min_duration > 0:
            top.after(int(self._min_duration * 1000), self._on_min_elapsed)
        if self._until_seconds is not None:
            top.after(int(self._until_seconds * 1000),
                      lambda: self._request_dismiss("timer"))

    # ----- Fade ramps ----------------------------------------------------------

    def _fade_in(self, step: int) -> None:
        if not self._is_showing or self._dismissing:
            return
        alpha = min(1.0, step / _FADE_STEPS)
        try:
            self._tk_toplevel.attributes("-alpha", alpha)
        except tkinter.TclError:
            return
        if step < _FADE_STEPS:
            self._tk_toplevel.after(_FADE_INTERVAL_MS, lambda: self._fade_in(step + 1))

    def _fade_out(self, step: int) -> None:
        alpha = max(0.0, 1.0 - step / _FADE_STEPS)
        try:
            self._tk_toplevel.attributes("-alpha", alpha)
        except tkinter.TclError:
            self._finalize()
            return
        if step < _FADE_STEPS:
            self._tk_toplevel.after(_FADE_INTERVAL_MS, lambda: self._fade_out(step + 1))
        else:
            self._finalize()

    # ----- Dismiss flow --------------------------------------------------------

    def _on_skip(self, _event: Any = None) -> None:
        self._request_dismiss("skip")

    def _on_min_elapsed(self) -> None:
        self._min_elapsed = True
        if self._pending_reason is not None:
            self._begin_dismiss(self._pending_reason)

    def _request_dismiss(self, reason: str) -> None:
        if self._dismissing or not self._is_showing:
            return
        if not self._min_elapsed:
            # Hold the first requested reason until the floor passes.
            if self._pending_reason is None:
                self._pending_reason = reason
            return
        self._begin_dismiss(reason)

    def _begin_dismiss(self, reason: str) -> None:
        if self._dismissing:
            return
        self._dismissing = True
        self.emit("dismiss", data=SplashDismissEvent(reason=reason))  # type: ignore[arg-type]
        # Reveal the app now so it is painted behind the (topmost) fading splash.
        if self._app_reveal is not None:
            reveal, self._app_reveal = self._app_reveal, None
            try:
                reveal()
            except Exception:
                pass
        if self._fade and self._is_showing:
            self._fade_out(1)
        else:
            self._finalize()

    def _finalize(self) -> None:
        self._is_showing = False
        self._clear_registration()
        try:
            self._tk_toplevel.destroy()
        except tkinter.TclError:
            pass

    def _clear_registration(self) -> None:
        if getattr(self._app, "_splash", None) is self:
            self._app._splash = None


register_widget_events(Splash, {"dismiss": "<<SplashDismiss>>"})