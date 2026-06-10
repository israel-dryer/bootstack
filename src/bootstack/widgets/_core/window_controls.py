from __future__ import annotations

from typing import Any, Callable


class WindowControlsMixin:
    """Window lifecycle and show-state controls shared by top-level windows.

    Mixed into `App`, `AppShell`, and `Window` so every top-level window exposes
    the same close and show-state surface.
    """

    _internal: Any

    def close(self) -> None:
        """Close the window and exit its event loop.

        For the application window this quits the loop started by `run()` — the
        natural action for a "Quit" command. It does not run the `on_close` veto
        handlers (those guard the user clicking the window's close button), so a
        programmatic `close()` always proceeds.
        """
        self._internal.close()

    def show(self) -> None:
        """Show the window — typically to reveal it again after `hide()`.

        For the application window, `run()` already shows it and starts the
        event loop; reach for `show()` to bring a hidden window back.
        """
        self._internal.show()

    def hide(self) -> None:
        """Hide the window without destroying it.

        The window is unmapped (and usually removed from the taskbar). Bring it
        back with `show()`.
        """
        self._internal.hide()

    def minimize(self) -> None:
        """Minimize the window to the taskbar or dock."""
        self._internal.minimize()

    def maximize(self) -> None:
        """Maximize the window where the platform supports it."""
        self._internal.maximize()

    def set_fullscreen(self, value: bool = True) -> None:
        """Enter or leave fullscreen mode where supported.

        Args:
            value: `True` to enter fullscreen, `False` to exit. Default `True`.
        """
        self._internal.set_fullscreen(value)

    def set_topmost(self, value: bool = True) -> None:
        """Pin the window above all others, or release it.

        Args:
            value: `True` to keep the window above others, `False` to release.
                Default `True`.
        """
        self._internal.set_topmost(value)

    def on_close(self, handler: Callable[[], bool | None]) -> None:
        """Register a handler invoked when the user clicks the window's close button.

        Handlers run in registration order; return `False` from one to veto the
        close (the window stays open), or `None`/`True` to allow it. This guards
        the close-button gesture only — it is not run by the programmatic
        `close()`.

        Args:
            handler: Called with no arguments on a close request. Return `False`
                to cancel the close.
        """
        self._internal.add_close_handler(handler)

    def add_close_handler(self, handler: Callable[[], bool | None]) -> None:
        """Register a veto-able close handler — an alias for `on_close()`.

        Args:
            handler: Called with no arguments on a close request. Return `False`
                to cancel the close.
        """
        self._internal.add_close_handler(handler)

    def remove_close_handler(self, handler: Callable[[], bool | None]) -> None:
        """Remove a close handler previously registered with `on_close()`.

        Args:
            handler: The same callable passed to `on_close()` or
                `add_close_handler()`. No-op if it was not registered.
        """
        self._internal.remove_close_handler(handler)
