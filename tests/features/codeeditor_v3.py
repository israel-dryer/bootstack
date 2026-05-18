"""Visual test for CodeEditor v3 — syntax highlighting via PygmentsHighlighter.

Tests: language= at construction, set_language() switching, pygments_style=,
       set_language(None) to disable, editing with live re-highlight.
"""
import bootstack as bs

app = bs.App(title="CodeEditor v3 — Syntax Highlighting", minsize=(820, 680), theme="dark")
log_var = bs.Signal("")

def log(msg):
    log_var.set(msg)
    print(msg)


PYTHON_SAMPLE = '''\
import os
from pathlib import Path


class FileScanner:
    """Recursively scan a directory for matching files."""

    def __init__(self, root: str, pattern: str = "*.py") -> None:
        self.root = Path(root)
        self.pattern = pattern

    def scan(self) -> list[Path]:
        """Return all files matching the pattern under root."""
        return sorted(self.root.rglob(self.pattern))

    def count(self) -> int:
        return len(self.scan())


def main() -> None:
    scanner = FileScanner(os.getcwd())
    files = scanner.scan()
    for path in files:
        print(f"  {path}")
    print(f"Total: {scanner.count()} files")


if __name__ == "__main__":
    main()
'''

SQL_SAMPLE = '''\
-- Find top customers by total order value
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id)   AS order_count,
    SUM(o.total_amount) AS lifetime_value
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status != 'cancelled'
  AND o.created_at >= DATE('now', '-1 year')
GROUP BY c.customer_id, c.name
HAVING lifetime_value > 1000
ORDER BY lifetime_value DESC
LIMIT 25;
'''

JSON_SAMPLE = '''\
{
  "name": "bootstack",
  "version": "1.0.0",
  "description": "Python/Tkinter desktop UI framework",
  "keywords": ["tkinter", "gui", "widgets"],
  "config": {
    "theme": "flatly",
    "debug": false,
    "max_workers": 4,
    "timeout": null
  },
  "dependencies": {
    "pygments": ">=2.15",
    "pillow": ">=10.0"
  }
}
'''

# ── main editor ───────────────────────────────────────────────────────────────

editor = bs.CodeEditor(
    app,
    value=PYTHON_SAMPLE,
    language="python",
    pygments_style="default",
    show_line_numbers=True,
    scrollbars="both",
    font="TkFixedFont",
)
editor.pack(fill="both", expand=True, padx=8, pady=8)
editor.on_change(lambda e: log(f"changed: op={e.data['op']}"))

# ── controls ──────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
ctrl = bs.PackFrame(app, direction="row", gap=6, padding=8)
ctrl.pack(fill="x")

bs.Label(ctrl, text="Language:").pack(side="left")

def set_python():
    editor.set_language("python")
    editor.value = PYTHON_SAMPLE
    log("language=python")

def set_sql():
    editor.set_language("sql")
    editor.value = SQL_SAMPLE
    log("language=sql")

def set_json():
    editor.set_language("json")
    editor.value = JSON_SAMPLE
    log("language=json")

def set_none():
    editor.set_language(None)
    log("language=None (highlighting off)")

bs.Button(ctrl, text="Python", command=set_python).pack(side="left")
bs.Button(ctrl, text="SQL",    command=set_sql).pack(side="left")
bs.Button(ctrl, text="JSON",   command=set_json).pack(side="left")
bs.Button(ctrl, text="None",   command=set_none).pack(side="left")

bs.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=4)
bs.Label(ctrl, text="Style:").pack(side="left")

def apply_style(name):
    editor._pygments_style = name
    lang = editor._language
    if lang:
        editor.set_language(lang)
    log(f"pygments_style={name!r}")

bs.Button(ctrl, text="default", command=lambda: apply_style("default")).pack(side="left")
bs.Button(ctrl, text="monokai", command=lambda: apply_style("monokai")).pack(side="left")
bs.Button(ctrl, text="dracula", command=lambda: apply_style("dracula")).pack(side="left")

# ── status bar ────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()