"""Interactive demo for `widget.capture()` (#427) and the #429 fix.

Shows the result INSIDE the window: every capture is written to a file and then
loaded back into the panel on the right, so what you see is the pixels that
landed on disk rather than a claim that they did.

What to try, in order:

  1. `Capture the card`   — one widget, not the whole window. The picture that
     comes back is just the card, at the card's size.
  2. `Capture the window` — the whole application.
  3. `Export…`            — the documented pattern: a save dialog, then a
     capture of whatever you chose. THEN TRY DOUBLE-CLICKING IT. Before #429
     the second click re-entered the handler mid-capture and stacked a second
     save dialog on top of the first; now it waits its turn, so you get one
     dialog, and the second click runs after the capture has finished.
  4. `Capture a hidden widget` — the refusal path. A capture reads the screen,
     so a widget that is not on it cannot be photographed, and saying so beats
     silently saving whatever was behind it.

Run:  py -3.12 development/demo_427_capture.py
"""

from pathlib import Path

import bootstack as bs
from bootstack.errors import BootstackError

OUT = Path(__file__).parent / "capture_demo_out"
OUT.mkdir(parents=True, exist_ok=True)

with bs.App(title="capture() demo — #427", size=(900, 560), padding=16,
            gap=12) as app:

    bs.Label("widget.capture()", font="heading-lg")
    bs.Label(
        "Every capture below is written to a file, then loaded back into the "
        "panel on the right.",
        font="caption", wrap_width=840,
    )

    with bs.Row(gap=16, vertical_items="start"):

        with bs.Column(gap=12):

            # The subject of arm 1 — a widget worth photographing on its own.
            with bs.Card(padding=16, gap=8) as card:
                bs.Label("Quarterly summary", font="heading-md")
                bs.Label("Revenue    $128,400", font="code")
                bs.Label("Expenses    $71,200", font="code")
                bs.Label("Net         $57,200", font="code")
                bs.ProgressBar(value=68, accent="success")

            # Never shown, so it can never be captured — arm 4.
            hidden = bs.Label("you cannot photograph me")
            hidden.detach()

            # Wrapped, and given the column's width: the refusal message is a
            # full sentence, and unwrapped it stretches the window wider than
            # the screen — at which point the grab runs off the desktop edge
            # and pads the difference with black.
            status = bs.Label("Nothing captured yet.", font="caption",
                              wrap_width=420, justify="left", anchor="w")

            with bs.Row(gap=8):
                bs.Button("Capture the card", accent="primary",
                          on_click=lambda: shoot(card, "card"))
                bs.Button("Capture the window",
                          on_click=lambda: shoot(app, "window"))

            with bs.Row(gap=8):
                bs.Button("Export…", accent="secondary", on_click=lambda: export())
                bs.Button("Capture a hidden widget", variant="outline",
                          on_click=lambda: shoot(hidden, "hidden"))

        with bs.Column(gap=8):
            bs.Label("What was written to disk", font="heading-md")
            preview = bs.Picture(width=390, height=300, fit="contain")
            preview_path = bs.Label("—", font="caption", wrap_width=390,
                                    justify="left", anchor="w")

    def show(written):
        """Load the file back in, so the panel proves the capture happened."""
        preview.image = str(written)
        preview_path.text = str(written)
        status.text = f"Wrote {written.name}"

    def shoot(target, name):
        try:
            show(target.capture(OUT / f"{name}.png"))
        except BootstackError as exc:
            # The refusal path is part of the feature, not a demo failure.
            status.text = f"Refused: {exc}"
            preview_path.text = "—"

    def export():
        chosen = bs.ask_save_file(
            title="Save the capture",
            initial_file="dashboard.png",
            file_types=[("PNG image", "*.png"), ("JPEG image", "*.jpg")],
            initial_dir=str(OUT),
        )
        if not chosen:
            status.text = "Export cancelled."
            return
        show(app.capture(chosen))

app.run()
