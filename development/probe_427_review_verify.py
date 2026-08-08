"""Independent verification of the #427 review's findings 1 and 2.

Both are claims about guards in `PublicWidgetBase.capture()`, and both would be
real defects if true, so neither is taken on trust. Every arm carries a control
so an arm that cannot reproduce its trap says so rather than quietly agreeing.

FINDING 1: a widget scrolled out of view inside a `ScrollView` stays mapped, so
the `winfo_ismapped()` guard passes and the grab reads a rectangle that is not
the widget — silently.

FINDING 2: `winfo_exists()` returns 0 for a destroyed child but RAISES for a
destroyed root, so the destroyed-target guard leaks a raw `TclError` when the
capture target is the App itself.

Run: python development/probe_427_review_verify.py
"""

import tkinter
from pathlib import Path

from PIL import Image

import bootstack as bs
from bootstack.errors import BootstackError

OUT = Path(__file__).parent / "screencap_out"
OUT.mkdir(parents=True, exist_ok=True)


def line(label, detail):
    print(f"  {label:<52} {detail}")


def distinct(path):
    with Image.open(path) as img:
        colors = img.convert("RGB").getcolors(maxcolors=1_000_000)
    return len(colors) if colors else 999_999


def finding_2_destroyed_root():
    """winfo_exists() on a destroyed ROOT vs a destroyed CHILD."""
    print("\n--- FINDING 2: destroyed target ---")

    # Control: a destroyed CHILD reports 0 and does not raise.
    root = tkinter.Tk()
    root.geometry("200x100+100+100")
    child = tkinter.Label(root, text="x")
    child.pack()
    root.update_idletasks()
    child.destroy()
    try:
        line("CONTROL destroyed child winfo_exists()", child.winfo_exists())
    except tkinter.TclError as exc:
        line("CONTROL destroyed child winfo_exists()", f"raised {exc}")
    root.destroy()

    # The claim: a destroyed ROOT raises instead of reporting 0.
    root2 = tkinter.Tk()
    root2.geometry("200x100+100+100")
    root2.update_idletasks()
    root2.destroy()
    try:
        line("destroyed ROOT winfo_exists()", root2.winfo_exists())
        line("VERDICT finding 2", "NOT reproduced — it returned a value")
    except tkinter.TclError as exc:
        line("destroyed ROOT winfo_exists()", f"RAISED TclError: {exc}")
        line("VERDICT finding 2", "REPRODUCED")


def finding_1_scrolled_out(app, rows, view):
    """A row scrolled out of the viewport: still mapped? grab still succeeds?"""
    print("\n--- FINDING 1: clipped by a scroll viewport ---")

    top = app.tk
    tw, th = top.winfo_width(), top.winfo_height()
    ty, tx = top.winfo_rooty(), top.winfo_rootx()
    line("window rect (x, y, w, h)", f"({tx}, {ty}, {tw}, {th})")

    # Control arm: the FIRST row is inside the viewport and captures normally.
    first = rows[0]
    shot = first.capture(OUT / "review-row-visible.png", settle=0)
    line("CONTROL visible row rooty", first.tk.winfo_rooty())
    line("CONTROL visible row colors", distinct(shot))

    # Scroll just far enough that row 0 leaves the viewport while its rect is
    # still ON the display. Scrolling to the bottom pushes it ~1100px above the
    # window, off the top of the screen, where the off-display guard catches it
    # — that is geometry luck, not a guard doing its job, and it hides the
    # defect being measured here.
    view.yview_moveto(0.12)
    top.update_idletasks()
    top.update()

    ry = first.tk.winfo_rooty()
    mapped = first.tk.winfo_ismapped()
    viewable = first.tk.winfo_viewable()
    line("scrolled-out row winfo_ismapped()", mapped)
    line("scrolled-out row winfo_viewable()", viewable)
    line("scrolled-out row rooty", ry)
    line("...window spans y", f"{ty} to {ty + th}")
    outside = ry < ty or ry > ty + th
    line("row rect lies OUTSIDE the window", outside)

    if not outside:
        line("VERDICT finding 1", "could not push the row out — arm inconclusive")
        return

    try:
        bad = first.capture(OUT / "review-row-scrolled-out.png", settle=0)
        colors = distinct(bad)
        line("capture() on the scrolled-out row", f"SUCCEEDED, {colors} colors")
        line("VERDICT finding 1",
             "REPRODUCED — wrong pixels, no error" if colors <= 2
             else f"succeeded with {colors} colors (captured SOMETHING else)")
    except BootstackError as exc:
        line("capture() on the scrolled-out row",
             f"BootstackError: {str(exc).split('—')[0].strip()[:60]}")
        line("VERDICT finding 1", "guarded here (may be geometry luck)")


def run():
    finding_1_scrolled_out(app, rows, view)
    finding_2_destroyed_root()
    print()
    app.close()


rows = []

with bs.App(title="Review verify", padding=8, gap=6, size=(420, 240)) as app:
    bs.Label("Scroll probe", font="heading-md")
    with bs.ScrollView(scroll_direction="vertical", height=150) as view:
        for i in range(40):
            with bs.Card(padding=6) as row:
                bs.Label(f"row {i}", accent="primary" if i == 0 else "default")
            rows.append(row)

app.schedule.delay(700, run)
app.run()
