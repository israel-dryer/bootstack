from __future__ import annotations

from typing import Any, Callable, Literal


class StatusBar:
    """The shell's full-width bottom status band — passive status only.

    The status bar is the home for an app's *passive* status — counts, sync
    state, a ready message — as distinct from the `commandbar`, which holds
    *interactive* controls. It reuses the command-bar strip primitive in a
    thinner, muted variant, so the left/right-cluster mental model carries over:
    items add left-to-right, and an `add_spacer()` (or `side='right'`) pushes the
    following items to the right cluster.

    The band renders only once a segment is added (or the shell was built with
    `show_statusbar=True`), so a one-screen utility never shows an empty strip.
    Obtained from `shell.statusbar` — not constructed directly. Create custom
    widgets with `parent=shell.statusbar` (they add to the left cluster
    automatically) or pass a pre-parented widget to `add_widget()`.
    """

    _auto_place = True

    def __init__(self, toolbar: Any, show: Callable[[], None]) -> None:
        self._internal = toolbar
        self._show = show
        self._has_right_spacer = False

    # ----- Container protocol (so `parent=shell.statusbar` works) -----

    def _child_master(self) -> Any:
        return self._internal.content

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # A widget created with `parent=shell.statusbar` adds to the left cluster.
        self._internal.add_widget(child._internal)
        self._show()

    @property
    def content(self) -> Any:
        """The band's content frame — parent custom widgets here."""
        return self._internal.content

    # ----- Segments -----

    def _ensure_right(self) -> None:
        if not self._has_right_spacer:
            self._internal.add_spacer()
            self._has_right_spacer = True

    def add_widget(self, widget: Any, *, side: Literal["left", "right"] = "left") -> None:
        """Add a passive widget to the left or right cluster.

        Args:
            widget: A public widget (or raw internal widget) parented to this
                status bar's `content` frame.
            side: `'left'` (default) or `'right'` (after the spacer).
        """
        if side == "right":
            self._ensure_right()
        tk_widget = getattr(widget, "_internal", widget)
        self._internal.add_widget(tk_widget)
        self._show()

    def add_text(
        self,
        text: str,
        *,
        side: Literal["left", "right"] = "left",
        icon: str | None = None,
        font: str | None = None,
    ) -> None:
        """Add a text (and optional icon) segment to a cluster.

        Args:
            text: The label text.
            side: `'left'` (default) or `'right'` (after the spacer).
            icon: Optional icon name displayed beside the text.
            font: Optional font token, e.g. `'caption'`.
        """
        if side == "right":
            self._ensure_right()
        self._internal.add_label(text, icon=icon, font=font)
        self._show()

    def add_spacer(self) -> None:
        """Add a flexible spacer that pushes following items to the right."""
        self._internal.add_spacer()
        self._has_right_spacer = True
        self._show()

    def clear(self) -> None:
        """Remove all status segments. The band stays shown once shown."""
        for child in list(self._internal.content.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        self._has_right_spacer = False
