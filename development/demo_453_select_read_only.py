"""Manual visual check for #453 — a read-only Select must actually be read-only.

Run it:  py -3.13 development/demo_453_select_read_only.py

WHAT TO DO — work down the numbered checklist in the window. The pass/fail for
each row is written beside it, so nothing has to be remembered. The CHANGED
banner at the bottom turns red the moment ANY select reports a new value; on
the unfixed build, step 2 alone is enough to light it up.

Pre-fix behavior, for comparison while testing:
  step 2  clicking the text area opens the list and changes the value
  step 2  the arrow looks dim, which is the only thing read_only ever did
  step 3  read_only is discarded entirely; you can type freely
  step 6  a plain select claims read_only == True
"""
import bootstack as bs

OPTIONS = ["Alpha", "Bravo", "Charlie", "Delta"]

changed = bs.Signal("no change yet")
status = bs.Signal("")


def note_change(event):
    """Any value change at all is a failure for the read-only rows."""
    changed.set(f"CHANGED -> {event.value!r}   (fine for row 1, a FAILURE for rows 2-5)")


with bs.App(title="#453 — read-only Select", minsize=(780, 1), padding=16, gap=12) as app:

    bs.Label("Read-only Select — manual check", font="heading-md")
    bs.Label(
        "Click the ARROW and then the TEXT AREA of each field. Both are separate "
        "ways into the list, and #453 was the text area staying live.",
        font="caption",
    )
    bs.Divider()

    # ---------------------------------------------------------------- static
    with bs.Card(padding=12, gap=10):
        bs.Label("Static states", font="heading-md")

        with bs.Row(gap=16, vertical_items="top"):
            with bs.Column(gap=2):
                s1 = bs.Select(OPTIONS, value="Alpha", label="1. plain", width=16)
                bs.Label("arrow opens - text area opens - cannot type", font="caption")

            with bs.Column(gap=2):
                s2 = bs.Select(OPTIONS, value="Alpha", label="2. read_only", width=16,
                               read_only=True)
                bs.Label("NEITHER opens - arrow dimmed  <-- the report", font="caption")

        with bs.Row(gap=16, vertical_items="top"):
            with bs.Column(gap=2):
                s3 = bs.Select(OPTIONS, value="Alpha", label="3. read_only + custom values",
                               width=16, read_only=True, allow_custom_values=True)
                bs.Label("NEITHER opens - and typing does nothing", font="caption")

            with bs.Column(gap=2):
                s4 = bs.Select(OPTIONS, value="Alpha", label="4. read_only + searchable",
                               width=16, read_only=True, searchable=True)
                bs.Label("NEITHER opens - and typing does nothing", font="caption")

        with bs.Row(gap=16, vertical_items="top"):
            with bs.Column(gap=2):
                s5 = bs.Select(OPTIONS, value="Alpha", label="5. disabled (control)",
                               width=16, disabled=True)
                bs.Label("greyed out entirely - the control", font="caption")

            with bs.Column(gap=2):
                s6 = bs.Select(OPTIONS, value="Alpha", label="6. plain, for the readout",
                               width=16)
                bs.Label("its read_only must report False", font="caption")

    # --------------------------------------------------------------- runtime
    with bs.Card(padding=12, gap=10):
        bs.Label("7. Runtime toggles — the half that construction cannot show", font="heading-md")
        bs.Label(
            "Flip these while watching the field. Turning read_only OFF must give back "
            "whatever the field was built with, not turn every field into a text box.",
            font="caption",
        )

        live = bs.Select(OPTIONS, value="Alpha", label="live field",
                         allow_custom_values=True, width=20)

        def refresh():
            entry = live._entry_widget()
            typeable = not entry.instate(["readonly"]) and not entry.instate(["disabled"])
            arrow = live._internal._addons.get("dropdown")
            status.set(
                f"read_only={live.read_only}   disabled={live.disabled}   "
                f"can type={typeable}   arrow dimmed="
                f"{arrow.instate(['disabled']) if arrow else 'n/a'}"
            )

        def toggle_read_only():
            live.read_only = not live.read_only
            refresh()

        def toggle_disabled():
            live.disabled = not live.disabled
            refresh()

        def toggle_custom():
            now = live._internal.configure("allow_custom_values")
            live._internal.configure(allow_custom_values=not now)
            refresh()

        with bs.Row(gap=8):
            bs.Button("toggle read_only", accent="primary", on_click=toggle_read_only)
            bs.Button("toggle disabled", on_click=toggle_disabled)
            bs.Button("toggle allow_custom_values", on_click=toggle_custom)

        bs.Label(textsignal=status, font="code")
        bs.Label(
            "This field is built with allow_custom_values=True. read_only ON then OFF "
            "must leave you able to TYPE again. On a plain field the same round trip "
            "must leave you UNABLE to type.",
            font="caption",
        )

    # --------------------------------------------------------------- banner
    bs.Divider()
    bs.Label(textsignal=changed, font="code", accent="danger")

    for sel in (s1, s2, s3, s4, s5, s6, live):
        sel.on_change(note_change)

    refresh()

app.run()
