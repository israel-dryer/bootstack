"""Calendar — full feature demo.

Demonstrates single-date selection and date-range selection.

Run with:
    python docs/examples/calendar.py
"""

from datetime import date
import bootstack as bs

with bs.App(title="Calendar Demo", padding=20, gap=16) as app:

    # Single mode
    bs.Label("Single Select", font="heading-sm")
    bs.Calendar(value=date(2026, 5, 15))

    # Range mode
    bs.Label("Range Select", font="heading-sm")
    bs.Calendar(
        selection_mode="range",
        start_date=date(2026, 5, 8),
        end_date=date(2026, 5, 22),
    )

app.run()
