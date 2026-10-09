"""Paint time of stretched fields at a narrow and a wide window width.

A field's border and fill are image elements, and ttk paints a stretched image
element by repeating the image's middle column across the parcel, one draw per
repeat. The field images are 26 to 40 pixels wide, so before the fix a field's
paint time grew with its width. With the images pre-tiled, wide and narrow paint
in about the same time.

Each arm adds 60 stretched `TextField`s to a mapped window and times the
`update()` that paints them; the median of five runs is printed. Run it on
`main` and on the branch and compare the `1280px` rows; the `400px` rows are the
control. Also printed: how many photo images the window holds and their size,
which is what the pre-tiled copies cost.

The window is mapped offscreen and fully transparent. On Windows the foreground
window is recorded first and handed back after mapping, so running this does not
take focus from what you are typing in.

Run:  py -3.12 development/probe_535_wide_field_paint.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import statistics
import sys
import time

import bootstack as bs

FIELDS = 60
RUNS = 5
WIDTHS = (400, 1280)

user32 = None
if sys.platform == "win32":
    import ctypes

    user32 = ctypes.windll.user32
foreground = user32.GetForegroundWindow() if user32 else None


def give_back_focus():
    if user32 and foreground:
        user32.SetForegroundWindow(foreground)


app = bs.App(title="wide field paint", theme="bootstrap-dark", padding=14, gap=6,
             horizontal_items="stretch")
root = app.tk
root.attributes("-alpha", 0.0)
root.geometry(f"{WIDTHS[0]}x800+-3000+0")
with app:
    host = bs.Column(gap=4, horizontal_items="stretch")
root.deiconify()
root.update()
give_back_focus()


def paint_ms(width: int) -> float:
    root.geometry(f"{width}x800+-3000+0")
    root.update()
    times = []
    for _ in range(RUNS):
        with host:
            fields = [bs.TextField(str(i), label=f"Field {i}") for i in range(FIELDS)]
        start = time.perf_counter()
        root.update()
        times.append((time.perf_counter() - start) * 1000)
        for field in fields:
            field.destroy()
        root.update()
    return statistics.median(times)


try:
    print(f"bootstack {bs.__file__}")
    for width in WIDTHS:
        print(f"  {width:>4}px  paint {FIELDS} stretched TextFields: {paint_ms(width):7.1f} ms")
    photos = [n for n in root.tk.call("image", "names") if root.tk.call("image", "type", n) == "photo"]
    pixels = sum(int(root.tk.call("image", "width", n)) * int(root.tk.call("image", "height", n)) for n in photos)
    print(f"  photo images: {len(photos)}, {pixels * 4 / 1e6:.2f} MB")
finally:
    give_back_focus()
    root.destroy()
    give_back_focus()
