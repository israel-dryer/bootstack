from __future__ import annotations

from typing import Any

from bootstack._runtime.app import App as _InternalApp
from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.public.container import PublicContainer, PACK_KEYS


class App(PublicContainer):
    """The application window. Behaves as an implicit VStack from the user's
    perspective: accepts `padding`, `gap`, `fill_items`, `expand_items`, and
    `anchor_items` and applies them to its internal content frame.

    `app.tk` returns the underlying `tk.Tk` root window.
    """

    _auto_place = False  # no parent

    def __init__(
        self,
        *,
        title: str | None = None,
        size: tuple[int, int] | None = None,
        settings: Any = None,
        localize: Any = None,
        # Child-guidance (applied to the internal content frame)
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        surface: str | None = None,
        # Extra kwargs forwarded to the internal App (theme, icon, etc.)
        **app_kwargs: Any,
    ) -> None:
        self._parent = None

        init_kwargs: dict[str, Any] = {}
        if title is not None:
            init_kwargs["title"] = title
        if size is not None:
            init_kwargs["size"] = size
        if settings is not None:
            init_kwargs["settings"] = settings
        if localize is not None:
            init_kwargs["localize"] = localize
        init_kwargs.update(app_kwargs)

        self._tk_root = _InternalApp(**init_kwargs)

        frame_kwargs: dict[str, Any] = {
            "direction": "vertical",
            "gap": gap,
            "fill_items": fill_items,
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface

        self._content_frame = PackFrame(self._tk_root, **frame_kwargs)
        self._content_frame.pack(fill="both", expand=True)

        self._internal = self._tk_root

    def _child_master(self):
        """Children pack into the content frame, not the Tk root."""
        return self._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._tk_root.deiconify()
        self._tk_root.mainloop()

    mainloop = run

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        try:
            self._tk_root.update_idletasks()
        except Exception:
            pass
        return None
