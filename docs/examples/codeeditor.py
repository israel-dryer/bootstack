"""CodeEditor — full feature demo.

Demonstrates syntax highlighting, language switching, read-only state,
search/replace, undo/redo, dirty tracking, and cursor move events.

Run with:
    python docs/examples/codeeditor.py
"""

import bootstack as bs

SAMPLE_PY = """\
import bootstack as bs

with bs.App(title="My App", padding=16, gap=12) as app:
    bs.Label("Hello, bootstack!", font="heading-lg")
    name = bs.TextField(label="Your name", placeholder="Enter name…")
    accent = bs.Select(["primary", "secondary", "success"], label="Accent")
    with bs.Row(gap=8):
        bs.Button("Submit", accent="primary")
        bs.Button("Cancel", variant="outline")
app.run()
"""

SAMPLE_SQL = """\
SELECT
    u.name,
    u.email,
    COUNT(o.id)   AS order_count,
    SUM(o.total)  AS lifetime_value
FROM users u
LEFT JOIN orders o
       ON o.user_id = u.id
      AND o.status  = 'completed'
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
ORDER BY lifetime_value DESC
LIMIT 50;
"""

with bs.App(title="CodeEditor Demo", size=(800, 700)) as app:
    with bs.ScrollView(grow=True, horizontal="stretch"):
        with bs.Column(padding=20, gap=16, horizontal_items="stretch"):

            # Python syntax highlighting
            bs.Label("Python", font="heading-sm")
            bs.CodeEditor(value=SAMPLE_PY, language="python", height=7)

            # SQL syntax highlighting
            bs.Label("SQL", font="heading-sm")
            bs.CodeEditor(value=SAMPLE_SQL, language="sql", height=7)

            # No highlighting
            bs.Label("Plain text (no language)", font="heading-sm")
            bs.CodeEditor(value="Hello, World!\nNo syntax highlighting.", height=3)

            # Read only
            bs.Label("Read Only", font="heading-sm")
            bs.CodeEditor(value=SAMPLE_PY, language="python", height=6, read_only=True)

            # Undo / redo + dirty tracking
            bs.Label("Undo / Redo + Dirty Tracking", font="heading-sm")
            dirty_sig = bs.Signal("not modified")
            editor = bs.CodeEditor(value=SAMPLE_PY, language="python", height=6)
            editor.on_modified(lambda e: dirty_sig.set("modified" if editor.is_dirty else "not modified"))
            with bs.Row(gap=8, vertical_items="center"):
                bs.Button("Undo",       on_click=lambda: editor.undo())
                bs.Button("Redo",       on_click=lambda: editor.redo())
                bs.Button("Mark saved", on_click=lambda: editor.mark_saved())
                bs.Label(textsignal=dirty_sig, accent="secondary")

            # Search / replace
            bs.Label("Search / Replace", font="heading-sm")
            ed2 = bs.CodeEditor(value=SAMPLE_PY, language="python", height=7)
            with bs.Row(gap=8):
                bs.Button("Find",    on_click=lambda: ed2.show_search())
                bs.Button("Replace", on_click=lambda: ed2.show_replace())

            # Cursor position
            bs.Label("Cursor Move Event", font="heading-sm")
            pos_sig = bs.Signal("line ?, col ?")
            ed3 = bs.CodeEditor(value=SAMPLE_PY, language="python", height=6)

            def _update_pos(e):
                idx = ed3._internal._core.text.index("insert")
                line, col = idx.split(".")
                pos_sig.set(f"line {line}, col {int(col) + 1}")

            ed3.on_cursor_move(_update_pos)
            bs.Label(textsignal=pos_sig, accent="secondary")

app.run()