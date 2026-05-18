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

from bootstack.widgets.composites.textarea.filter import EditFilter
from bootstack.widgets.composites.textarea.decoration import Position, RangeDecoration

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore


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
        pygments_style: Pygments style name (e.g. `'default'`,
            `'monokai'`, `'dracula'`). Defaults to `'default'`.
    """

    def __init__(
        self,
        language: str,
        pygments_style: str = "default",
    ) -> None:
        super().__init__()
        self._core: _MultilineCore | None = None
        self._after_id: str | None = None

        try:
            self._lexer = get_lexer_by_name(language, stripall=False, stripnl=False)
        except ClassNotFound:
            self._lexer = TextLexer()

        try:
            style_cls = get_style_by_name(pygments_style)
        except ClassNotFound:
            style_cls = get_style_by_name("default")

        self._style_colors = _extract_colors(style_cls)
        # Pre-compute the set of style names that actually have colors — used
        # in the per-token hot path to skip style-name lookups with no color.
        self._active_styles: frozenset[str] = frozenset(self._style_colors)

    # ── EditFilter protocol ───────────────────────────────────────────────

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.register_layer(_LAYER, priority=1)
        for style_name, color in self._style_colors.items():
            core.define_style(style_name, foreground=color)
        self._schedule()

    def detach(self, core: _MultilineCore) -> None:
        self._cancel()
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