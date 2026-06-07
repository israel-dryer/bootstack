"""File-backed data source — stream a CSV into a table, export to any format.

A CSV is generated on a temp path, then ``FileDataSource`` streams it into a
SQLite working store (bounded memory, even for large files). The ``DataTable``
pages, filters, and sorts it as fast SQL, and its export menu offers several
formats via ``export_formats=``. The original file is read-only input; edits live
in the working store, and the temp store is cleaned up automatically.

Run with:
    python docs/examples/file_source.py
"""

import csv
import tempfile
from pathlib import Path

import bootstack as bs

DEPARTMENTS = ["Engineering", "Design", "Sales", "Support"]


def make_csv() -> Path:
    """Write a sample CSV to a temp file and return its path."""
    path = Path(tempfile.gettempdir()) / "bootstack_people.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "department", "score"])
        for i in range(1, 501):
            writer.writerow([i, f"Person {i:03d}", DEPARTMENTS[i % 4], (i * 7) % 100])
    return path


def main() -> None:
    csv_path = make_csv()

    # Stream the file into a SQLite working store (temporary, auto-cleaned).
    source = bs.FileDataSource(csv_path)
    source.load()

    with bs.App(title="FileDataSource", size=(720, 480), padding=12, gap=8) as app:
        bs.Label("500 rows streamed from a CSV — sort, filter, and export.",
                 font="heading-sm")

        bs.DataTable(
            data_source=source,
            columns=[
                {"text": "ID", "key": "id", "width": 60},
                {"text": "Name", "key": "name", "width": 160},
                {"text": "Department", "key": "department", "width": 140},
                {"text": "Score", "key": "score", "width": 80},
            ],
            page_size=25,
            allow_export=True,
            export_formats=["csv", "json", "jsonl", "xml"],
            fill="both",
            expand=True,
        )

    app.run()
    source.close()  # remove the temp working store


if __name__ == "__main__":
    main()
