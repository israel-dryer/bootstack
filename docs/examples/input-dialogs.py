from datetime import date
import bootstack as bs

with bs.App(title="Input Dialogs", size=(680, 250), padding=20, gap=16) as app:

    # ── Text and Number ────────────────────────────────────────────────────
    bs.Label("Text and Number", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Text",     on_click=lambda: bs.ask_string("Enter your name:", title="Name"))
        bs.Button("Integer",  on_click=lambda: bs.ask_integer("Enter age:", min_value=0, max_value=120))
        bs.Button("Float",    on_click=lambda: bs.ask_float("Enter price:", min_value=0.0, step=0.5))
        bs.Button("From list", on_click=lambda: bs.ask_item(
            "Select country:", ["Canada", "UK", "USA", "Australia", "Other"],
        ))

    bs.Separator(fill="x")

    # ── Date ──────────────────────────────────────────────────────────────
    bs.Label("Date", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Date",       on_click=lambda: bs.ask_date(title="Select Date", value=date.today()))
        bs.Button("Date range", on_click=lambda: bs.ask_date_range(title="Report Period"))

app.run()