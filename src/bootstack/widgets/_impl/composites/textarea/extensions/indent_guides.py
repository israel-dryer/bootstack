"""IndentGuides — draws subtle guide marks at each indent stop.

Filter-style extension: on each edit (debounced), scans all lines and
places a single-character background highlight at the last space of each
tab-stop in the leading whitespace, producing a visual column guide.

Only space-based indentation is supported. Tab-character indentation is
ignored (guide count will be zero for tab-indented lines).
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.filter import EditFilter
from bootstack.widgets._impl.composites.textarea.decoration import Position, RangeDecoration

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


_LAYER = "indent"
_DEBOUNCE_MS = 200
_STYLE = "guide"


class IndentGuides(EditFilter):
    """Draws subtle vertical guide marks at each indent stop.

    Install via the `show_indent_guides=True` parameter on `CodeEditor`,
    or manually: `core.add_filter(IndentGuides())`.

    Guide marks are placed on the last space character of each tab-stop
    group in a line's leading whitespace (e.g. at column 3, 7, 11, ...
    for `tab_width=4`). Only space-indented lines receive guides.

    Args:
        tab_width: Spaces per indent level. Should match `SmartIndent`.
    """

    def __init__(self, tab_width: int = 4) -> None:
        super().__init__()
        self._core: _MultilineCore | None = None
        self._after_id: str | None = None
        self._tab_width = tab_width
        self._theme_root: Any = None
        self._theme_bind_id: str | None = None

    # ── EditFilter protocol ───────────────────────────────────────────────

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.register_layer(_LAYER, priority=0)
        self._apply_guide_style(core)
        core.text.bind("<<EditorBgChanged>>", self._on_theme_changed, add="+")
        # Recalibrate guide color after a theme rebuild. Bind <<BsThemeChanged>>
        # on the root — fired ONCE by bootstack after the full rebuild (correct
        # colors) — NOT the ttk <<ThemeChanged>>, which fires mid-rebuild.
        self._theme_root = core.winfo_toplevel()
        self._theme_bind_id = self._theme_root.bind(
            "<<BsThemeChanged>>", self._on_theme_changed, add="+"
        )
        self._schedule()

    def detach(self, core: _MultilineCore) -> None:
        self._cancel()
        if self._theme_bind_id is not None and self._theme_root is not None:
            try:
                self._theme_root.unbind("<<BsThemeChanged>>", self._theme_bind_id)
            except Exception:
                pass
            self._theme_bind_id = None
            self._theme_root = None
        if self._core is not None:
            core.clear_decorations(_LAYER)
        self._core = None

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)
        self._schedule()

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)
        self._schedule()

    # ── internal ──────────────────────────────────────────────────────────

    def _apply_guide_style(self, core: _MultilineCore) -> None:
        try:
            bg = core.text.cget("background")
            guide_bg = _subtle_variant(bg)
        except Exception:
            guide_bg = "#cccccc"
        core.define_style(_STYLE, background=guide_bg)

    def _on_theme_changed(self, _event=None) -> None:
        if self._core is not None:
            self._apply_guide_style(self._core)

    def _schedule(self) -> None:
        self._cancel()
        if self._core is not None:
            self._after_id = self._core.text.after(_DEBOUNCE_MS, self._update)

    def _cancel(self) -> None:
        if self._after_id is not None and self._core is not None:
            try:
                self._core.text.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None

    def _update(self) -> None:
        self._after_id = None
        if self._core is None:
            return
        try:
            text = self._core.value
        except Exception:
            return

        decorations = _compute_guides(text, self._tab_width)
        self._core.set_decorations(_LAYER, decorations)


def _compute_guides(text: str, tab_width: int) -> list[RangeDecoration]:
    """Return guide decorations for every indent stop in `text`."""
    decorations: list[RangeDecoration] = []
    for line_num, line in enumerate(text.split("\n"), 1):
        n = len(line) - len(line.lstrip(" "))
        for k in range(1, n // tab_width + 1):
            col = k * tab_width - 1
            decorations.append(RangeDecoration(
                Position(line_num, col),
                Position(line_num, col + 1),
                _STYLE,
            ))
    return decorations


def _subtle_variant(hex_color: str) -> str:
    """Return a slightly darker or lighter shade of `hex_color`."""
    h = hex_color.lstrip("#")
    if len(h) < 6:
        return "#cccccc"
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance > 128:
            r2 = max(0, int(r * 0.88))
            g2 = max(0, int(g * 0.88))
            b2 = max(0, int(b * 0.88))
        else:
            r2 = min(255, r + 28)
            g2 = min(255, g + 28)
            b2 = min(255, b + 28)
        return f"#{r2:02x}{g2:02x}{b2:02x}"
    except Exception:
        return "#cccccc"