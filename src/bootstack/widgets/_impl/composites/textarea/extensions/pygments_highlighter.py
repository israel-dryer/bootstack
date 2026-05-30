"""PygmentsHighlighter — syntax highlighting via Pygments.

Implements a debounced full-document retokenize strategy: on each
insert/delete, schedules a retokenize after 150 ms. Tokens are mapped
to `RangeDecoration` objects and applied via the decoration layer system.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from pygments import lex
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pygments.util import ClassNotFound

from bootstack.widgets._impl.composites.textarea.filter import EditFilter
from bootstack.widgets._impl.composites.textarea.decoration import Position, RangeDecoration

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


_LAYER = "syntax"
_DEBOUNCE_MS = 150

# Token family → bootstack style name.  More-specific entries must come
# before their parents so that the parent-walk hits the right name first.
_TOKEN_TO_STYLE: dict = {
    Token.String.Doc: "string_doc",
    Token.String: "string",
    Token.Keyword: "keyword",
    Token.Comment: "comment",
    Token.Number: "number",
    Token.Operator: "operator",
    Token.Name.Builtin: "name_builtin",
    Token.Name.Function: "name_function",
    Token.Name.Class: "name_class",
    Token.Name.Decorator: "name_decorator",
    Token.Name.Exception: "name_exception",
    Token.Name.Namespace: "name_namespace",
    Token.Name.Tag: "name_tag",           # JSON keys, HTML/XML tags
    Token.Name.Attribute: "name_attribute",  # HTML/XML attributes
    Token.Punctuation: "punctuation",
    Token.Error: "error",
}

# Reverse map: style name → canonical token (used for color extraction)
_STYLE_TO_TOKEN: dict = {v: k for k, v in _TOKEN_TO_STYLE.items()}


def _find_style(ttype) -> str | None:
    """Walk up the Pygments token hierarchy to find the nearest style name."""
    t = ttype
    while t is not None:
        if t in _TOKEN_TO_STYLE:
            return _TOKEN_TO_STYLE[t]
        t = t.parent
    return None


def _extract_colors(style_cls) -> dict[str, str]:
    """Return `{style_name: '#RRGGBB'}` for all style names that have a color."""
    colors: dict[str, str] = {}
    for name, token in _STYLE_TO_TOKEN.items():
        info = style_cls.style_for_token(token)
        color = info.get("color")
        if color:
            colors[name] = f"#{color}"
    return colors


def _contrast_color(hex_color: str) -> str:
    """Return black or white for maximum contrast against `hex_color`."""
    h = hex_color.lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "#000000" if luminance > 128 else "#ffffff"
    except Exception:
        return "#000000"


class PygmentsHighlighter(EditFilter):
    """Syntax highlighting via Pygments.

    Install via the `language=` parameter on `CodeEditor`, or manually:

        core.add_filter(PygmentsHighlighter("python"))

    Uses a debounced full-document retokenize: 150 ms after the last edit the
    full text is re-lexed, tokens are converted to `RangeDecoration` objects,
    and applied via `core.set_decorations()`.

    Args:
        language: Pygments lexer name (e.g. `'python'`, `'sql'`,
            `'javascript'`). Unknown names fall back to plain text.
        pygments_style: Pygments style name, or `'auto'` to track the
            bootstack theme. When `'auto'`, `light_style` and `dark_style`
            determine the actual Pygments style used.
        light_style: Pygments style used in auto mode when the active
            bootstack theme is light. Default `'default'`.
        dark_style: Pygments style used in auto mode when the active
            bootstack theme is dark. Default `'monokai'`.
    """

    def __init__(
        self,
        language: str,
        pygments_style: str = "default",
        light_style: str = "default",
        dark_style: str = "monokai",
    ) -> None:
        super().__init__()
        self._core: _MultilineCore | None = None
        self._after_id: str | None = None
        self._publisher_name: str | None = None

        self._auto = pygments_style == "auto"
        self._light_style = light_style
        self._dark_style = dark_style

        try:
            self._lexer = get_lexer_by_name(language, stripall=False, stripnl=False)
        except ClassNotFound:
            self._lexer = TextLexer()

        # Load initial style — auto resolves after attach when the theme is known.
        initial = self._resolve_auto_name() if self._auto else pygments_style
        self._load_style(initial)

        # Saved originals — restored on detach.
        self._orig_bg: str | None = None
        self._orig_fg: str | None = None
        self._orig_ibg: str | None = None

    # ── EditFilter protocol ───────────────────────────────────────────────

    def attach(self, core: _MultilineCore) -> None:
        self._core = core

        # Resolve auto style now that we can query the theme provider.
        if self._auto:
            self._load_style(self._resolve_auto_name())

        core.register_layer(_LAYER, priority=1)
        for sname, color in self._style_colors.items():
            core.define_style(sname, foreground=color)

        # Save current text-widget colors before overriding them.
        self._orig_bg = core.text.cget("background")
        self._orig_fg = core.text.cget("foreground")
        self._orig_ibg = core.text.cget("insertbackground")
        self._apply_widget_colors(core)

        # Subscribe to the framework Publisher — fires AFTER _rebuild_all_styles()
        # so colors read from the style builder reflect the new theme.
        from bootstack._core.publisher import Publisher, Channel
        self._publisher_name = f"_pygments_{id(self)}"
        Publisher.subscribe(
            name=self._publisher_name,
            func=self._on_framework_theme_changed,
            channel=Channel.STD,
        )
        self._schedule()

    def detach(self, core: _MultilineCore) -> None:
        self._cancel()
        if self._publisher_name is not None:
            from bootstack._core.publisher import Publisher
            Publisher.unsubscribe(self._publisher_name)
            self._publisher_name = None
        if self._core is not None:
            core.clear_decorations(_LAYER)
            self._restore_widget_colors(core)
        self._core = None

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)
        self._schedule()

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)
        self._schedule()

    # ── internal ──────────────────────────────────────────────────────────

    def _apply_widget_colors(self, core: _MultilineCore, notify: bool = True) -> None:
        kw: dict = {"background": self._style_bg}
        if self._style_fg:
            kw["foreground"] = self._style_fg
        kw["insertbackground"] = self._style_fg or _contrast_color(self._style_bg)
        try:
            core.text.configure(**kw)
            if notify:
                # Notify extensions that the editor background changed so they
                # can re-calibrate colors.  Only fire on deliberate style
                # application (attach / set_language), not on every
                # <<ThemeChanged>> — extensions already receive that event
                # directly and cascading it causes unnecessary repaints.
                core.text.event_generate("<<EditorBgChanged>>", when="tail")
        except Exception:
            pass

    def _restore_widget_colors(self, core: _MultilineCore) -> None:
        kw: dict = {}
        if self._orig_bg is not None:
            kw["background"] = self._orig_bg
        if self._orig_fg is not None:
            kw["foreground"] = self._orig_fg
        if self._orig_ibg is not None:
            kw["insertbackground"] = self._orig_ibg
        if kw:
            try:
                core.text.configure(**kw)
            except Exception:
                pass

    def _resolve_auto_name(self) -> str:
        """Return the appropriate Pygments style name for the current theme mode."""
        try:
            from bootstack.style.style import get_theme_provider
            mode = get_theme_provider().mode
        except Exception:
            mode = "light"
        return self._dark_style if mode == "dark" else self._light_style

    def _load_style(self, style_name: str) -> None:
        """Load a Pygments style, updating all color state."""
        try:
            style_cls = get_style_by_name(style_name)
        except ClassNotFound:
            style_cls = get_style_by_name("default")
        self._style_colors = _extract_colors(style_cls)
        self._active_styles: frozenset[str] = frozenset(self._style_colors)
        self._style_bg: str = style_cls.background_color
        raw_fg = (
            style_cls.style_for_token(Token.Text).get("color")
            or style_cls.style_for_token(Token).get("color")
        )
        self._style_fg: str | None = f"#{raw_fg}" if raw_fg else None

    def _on_framework_theme_changed(self, theme: str = None, mode: str = None, **kwargs) -> None:
        """Called by the Publisher after _rebuild_all_styles() completes."""
        if self._core is None:
            return
        if self._auto:
            resolved = self._dark_style if mode == "dark" else self._light_style
            self._load_style(resolved)
            for sname, color in self._style_colors.items():
                self._core.define_style(sname, foreground=color)
        self._apply_widget_colors(self._core, notify=True)
        self._schedule()

    def _schedule(self) -> None:
        self._cancel()
        if self._core is not None:
            self._after_id = self._core.text.after(_DEBOUNCE_MS, self._retokenize)

    def _cancel(self) -> None:
        if self._after_id is not None and self._core is not None:
            try:
                self._core.text.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None

    def _retokenize(self) -> None:
        self._after_id = None
        if self._core is None:
            return
        try:
            text = self._core.value
        except Exception:
            return

        if not text:
            self._core.clear_decorations(_LAYER)
            return

        decorations: list[RangeDecoration] = []
        line, col = 1, 0
        active = self._active_styles

        for ttype, value in lex(text, self._lexer):
            if value:
                style = _find_style(ttype)
                if style is not None and style in active:
                    if "\n" in value:
                        vlines = value.split("\n")
                        end_line = line + len(vlines) - 1
                        end_col = len(vlines[-1])
                    else:
                        end_line = line
                        end_col = col + len(value)
                    decorations.append(RangeDecoration(
                        Position(line, col),
                        Position(end_line, end_col),
                        style,
                    ))

                # Advance position regardless of whether we added a decoration.
                if "\n" in value:
                    vlines = value.split("\n")
                    line += len(vlines) - 1
                    col = len(vlines[-1])
                else:
                    col += len(value)

        self._core.set_decorations(_LAYER, decorations)