"""Visual test for CodeEditor v2 — minimal editor without syntax highlighting.

Tests: line numbers, bracket matching, smart indent, tab_width, undo/redo,
goto_line, on_change, install/uninstall custom filter.
"""
import bootstack as bs
from bootstack.widgets.composites.textarea.filter import EditFilter

app = bs.App(title="CodeEditor v2", size=(700, 560))
log_var = bs.Signal("")

def log(msg):
    log_var.set(msg)
    print(msg)


# ── main editor ───────────────────────────────────────────────────────────────

SAMPLE = '''\
def greet(name):
    """Say hello."""
    msg = f"Hello, {name}!"
    return msg

result = greet("World")
print(result)
'''

editor = bs.CodeEditor(
    app,
    value=SAMPLE,
    show_line_numbers=True,
    tab_width=4,
    insert_spaces=True,
    auto_indent=True,
    scrollbars="both",
)
editor.pack(fill="both", expand=True, padx=8, pady=8)
editor.on_change(lambda e: log(f"changed: op={e.data['op']}"))

# ── controls ──────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
ctrl = bs.PackFrame(app, direction="row", gap=6, padding=8)
ctrl.pack(fill="x")

bs.Button(ctrl, text="goto line 3",
          command=lambda: (editor.goto_line(3), log("goto_line(3)"))).pack(side="left")
bs.Button(ctrl, text="Undo",   command=editor.undo).pack(side="left")
bs.Button(ctrl, text="Redo",   command=editor.redo).pack(side="left")
bs.Button(ctrl, text="is_dirty?",
          command=lambda: log(f"is_dirty={editor.is_dirty}")).pack(side="left")
bs.Button(ctrl, text="mark_saved()",
          command=lambda: (editor.mark_saved(), log("saved"))).pack(side="left")


# ── custom filter demo ────────────────────────────────────────────────────────

class _UpperFilter(EditFilter):
    """Demo filter: uppercases every inserted character."""
    def insert(self, index, chars, tags=None):
        self.delegate.insert(index, chars.upper(), tags)
    def delete(self, index1, index2=None):
        self.delegate.delete(index1, index2)

_upper = _UpperFilter()
_upper_installed = [False]

def toggle_upper():
    if _upper_installed[0]:
        editor.uninstall(_upper)
        _upper_installed[0] = False
        log("UpperFilter removed")
    else:
        editor.install(_upper)
        _upper_installed[0] = True
        log("UpperFilter installed — type to see uppercase")

bs.Button(ctrl, text="Toggle uppercase filter",
          command=toggle_upper).pack(side="left")

# ── status bar ────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()
