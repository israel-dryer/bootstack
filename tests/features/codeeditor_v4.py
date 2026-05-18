"""Visual test for CodeEditor v4 — IndentGuides + SearchOverlay.

Tests: show_indent_guides=True, Ctrl+F find bar, match navigation,
       case-sensitive toggle, regex toggle, set_language() with search open.
"""
import print

import bootstack as bs
from bootstack.widgets.composites.textarea.extensions.indent_guides import IndentGuides

app = bs.App(title="CodeEditor v4 — Guides + Search", minsize=(820, 680))
log_var = bs.Signal("")

def log(msg):
    log_var.set(msg)
    print(msg)


SAMPLE = '''\
import os
import re
from pathlib import Path
from typing import Iterator


class FileScanner:
    """Recursively scan a directory for matching files."""

    DEFAULT_PATTERN = "*.py"

    def __init__(self, root: str, pattern: str = DEFAULT_PATTERN) -> None:
        self.root = Path(root)
        self.pattern = pattern
        self._cache: list[Path] | None = None

    def scan(self) -> list[Path]:
        """Return all files matching the pattern under root."""
        if self._cache is None:
            self._cache = sorted(self.root.rglob(self.pattern))
        return self._cache

    def invalidate(self) -> None:
        """Clear the cached scan result."""
        self._cache = None

    def iter_matches(self, query: str) -> Iterator[Path]:
        """Yield files whose names contain `query` (case-insensitive)."""
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for path in self.scan():
            if pattern.search(path.name):
                yield path

    def count(self) -> int:
        return len(self.scan())


def main() -> None:
    scanner = FileScanner(os.getcwd())
    files = scanner.scan()
    for path in files:
        print(f"  {path}")
    print(f"Total: {scanner.count()} files")

    matches = list(scanner.iter_matches("test"))
    if matches:
        print(f"Test files: {len(matches)}")
        for p in matches:
            print(f"  {p.name}")


if __name__ == "__main__":
    main()
'''

# ── main editor ───────────────────────────────────────────────────────────────

editor = bs.CodeEditor(
    app,
    value=SAMPLE,
    language="python",
    pygments_style="default",
    show_line_numbers=True,
    show_indent_guides=True,
    tab_width=4,
    scrollbars="both",
    font="TkFixedFont",
)
editor.pack(fill="both", expand=True, padx=8, pady=8)
editor.on_change(lambda e: log(f"changed: op={e.data['op']}"))

# ── controls ──────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
ctrl = bs.PackFrame(app, direction="row", gap=6, padding=8)
ctrl.pack(fill="x")

bs.Button(ctrl, text="Show Search (Ctrl+F)",
          command=editor.show_search).pack(side="left")
bs.Button(ctrl, text="Hide Search",
          command=editor.hide_search).pack(side="left")

bs.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=4)

def toggle_guides():
    if editor._indent_guides is None:
        editor._indent_guides = IndentGuides(tab_width=4)
        editor._core.add_filter(editor._indent_guides)
        log("indent guides ON")
    else:
        editor._core.remove_filter(editor._indent_guides)
        editor._indent_guides = None
        log("indent guides OFF")

bs.Button(ctrl, text="Toggle Indent Guides", command=toggle_guides).pack(side="left")

bs.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=4)

bs.Label(ctrl, text="Style:").pack(side="left")
for name in ("default", "monokai", "one-dark"):
    bs.Button(ctrl, text=name,
              command=lambda n=name: (
                  setattr(editor, "_pygments_style", n),
                  editor.set_language(editor._language),
                  log(f"style={n!r}")
              )).pack(side="left")

# ── status bar ────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()