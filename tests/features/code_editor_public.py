"""Visual test for the public CodeEditor widget."""
from bootstack import (
    App, VStack, HStack, Label, Button, Separator, CodeEditor,
)

_PYTHON_SAMPLE = '''\
def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"


class Counter:
    def __init__(self, start: int = 0) -> None:
        self.value = start

    def increment(self) -> None:
        self.value += 1

    def reset(self) -> None:
        self.value = 0
'''

_SQL_SAMPLE = '''\
SELECT
    u.id,
    u.name,
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.active = 1
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 20;
'''


with App(title="CodeEditor — public layer", minsize=(780, 640), padding=16, gap=12) as app:

    Label("CodeEditor", font="heading-lg")

    with HStack(gap=12, fill="both", expand=True):

        with VStack(gap=6, fill="both", expand=True):
            Label("Python — line numbers, syntax highlight")
            py_editor = CodeEditor(
                _PYTHON_SAMPLE,
                language="python",
                pygments_style="default",
                show_line_numbers=True,
                fill="both",
                expand=True,
            )

        with VStack(gap=6, fill="both", expand=True):
            Label("SQL — no line numbers")
            sql_editor = CodeEditor(
                _SQL_SAMPLE,
                language="sql",
                show_line_numbers=False,
                fill="both",
                expand=True,
            )

    Separator(fill="x")

    Label("Controls", font="heading-sm")
    status_lbl = Label("is_dirty: False")

    def _refresh_dirty(e=None):
        status_lbl.value = f"is_dirty: {py_editor.is_dirty}"

    py_editor.on_change(_refresh_dirty)

    with HStack(gap=8):
        Button("Mark saved", variant="outline",
               on_click=lambda: (py_editor.mark_saved(), _refresh_dirty()))
        Button("Goto line 5", variant="outline",
               on_click=lambda: py_editor.goto_line(5))
        Button("Select all", variant="outline",
               on_click=lambda: py_editor.select_all())
        Button("Clear", variant="outline",
               on_click=lambda: (py_editor.clear(), _refresh_dirty()))
        Button("Find (Ctrl+F)", variant="outline",
               on_click=lambda: py_editor.show_search())
        Button("Replace", variant="outline",
               on_click=lambda: py_editor.show_replace())

    with HStack(gap=8):
        Button("Toggle read-only", variant="outline",
               on_click=lambda: setattr(py_editor, "read_only", not py_editor.read_only))
        Button("Python", on_click=lambda: setattr(py_editor, "language", "python"))
        Button("JSON", on_click=lambda: setattr(py_editor, "language", "json"))
        Button("None", variant="outline",
               on_click=lambda: setattr(py_editor, "language", None))

app.run()
