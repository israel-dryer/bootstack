"""Manual test for Table export — small (sync) and large (async + progress).

Run:  py -3.12 tests/features/table_export.py

- Click the download icon (top-right) → "Copy to clipboard" or "Save to file".
- The table has 1,000,000 rows, so "Save to file" runs asynchronously behind a
  progress dialog you can cancel. (Excel option appears if bootstack[excel] is
  installed.)
- The on_export handler logs what happened below the table.
"""
import bootstack as bs

ROWS = [
    {
        "id_no": i,
        "name": f"Person {i:05d}",
        "department": ["Engineering", "Design", "Sales", "Support"][i % 4],
        "score": (i * 7) % 100,
    }
    for i in range(1_000_000)
]

with bs.App(title="Table Export", size=(820, 560), padding=12, gap=8) as app:
    bs.Label("1,000,000 rows — try the export menu (top-right).", font="heading-sm")
    status = bs.Label("Ready.", font="caption")

    table = bs.Table(
        columns=[
            {"text": "ID", "key": "id_no", "width": 80},
            {"text": "Name", "key": "name", "width": 160},
            {"text": "Department", "key": "department", "width": 140},
            {"text": "Score", "key": "score", "width": 80},
        ],
        rows=ROWS,
        selection_mode="multi",
        allow_export=True,
        page_size=50,
        fill="both",
        expand=True,
    )

    def on_export(e):
        where = e.path if e.target == "file" else "clipboard"
        status.text = f"Exported {e.count} rows as {e.format} → {where}"

    table.on_export(on_export)

app.run()
