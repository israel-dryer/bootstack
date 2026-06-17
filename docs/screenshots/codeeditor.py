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


def hero():
    with bs.App(title="CodeEditor", padding=20, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        bs.CodeEditor(value=SAMPLE_PY, language="python", height=12, horizontal="stretch")
    app.run()


def languages():
    with bs.App(title="CodeEditor — Languages", padding=20, gap=12, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        bs.CodeEditor(value=SAMPLE_PY,  language="python", height=12, horizontal="stretch", width=1)
        bs.CodeEditor(value=SAMPLE_SQL, language="sql",    height=15, horizontal="stretch", width=1)
    app.run()


def states():
    with bs.App(title="CodeEditor — States", padding=20, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            bs.CodeEditor(value=SAMPLE_PY, language="python", height=12, width=1)
            bs.CodeEditor(value=SAMPLE_PY, language="python", height=12, width=1, read_only=True)
    app.run()


SCENES = {
    "hero":      hero,
    "languages": languages,
    "states":    states,
}