"""Controls for the #427 review fixes — proves each guard had something to catch.

A guard that is never exercised is indistinguishable from a guard that is not
needed, so each check here reproduces the PRE-FIX behavior directly rather than
trusting the description of it. Run with `py -3.12`.
"""
from __future__ import annotations

import tkinter
from tkinter import ttk

from PIL import Image

print("1. PIL crops past the edge by PADDING WITH BLACK, silently")
desktop = Image.new("RGB", (1920, 1080), "white")
outside = desktop.crop((1930, 10, 2200, 300))  # the pre-fix line, verbatim
colors = outside.getcolors()
print(f"   crop((1930, 10, 2200, 300)) -> size={outside.size} colors={colors}")
assert colors == [(outside.size[0] * outside.size[1], (0, 0, 0))], colors
print("   CONFIRMED: an all-black image, no exception. Nothing to debug.\n")

print("2. The pre-fix save() gate (mode == 'RGBA') misses a palette image")
palette = Image.new("P", (4, 4))
pre_fix_would_convert = palette.mode == "RGBA"
print(f"   mode={palette.mode!r} -> pre-fix converts? {pre_fix_would_convert}")
assert not pre_fix_would_convert
try:
    palette.save("_probe_427.jpg")
except OSError as exc:
    print(f"   CONFIRMED: unconverted .jpg save raises -> {exc}\n")
else:  # pragma: no cover - would mean Pillow started accepting mode P
    raise SystemExit("   Pillow accepted mode P as JPEG; finding is stale")
finally:
    import os

    if os.path.exists("_probe_427.jpg"):
        os.remove("_probe_427.jpg")

print("3. A negative inset EXPANDS the rectangle past the widget")
x, y, width, height, inset = 100, 100, 60, 20, -8
left, top = x + inset, y + inset
right, bottom = x + width - inset, y + height - inset
print(f"   widget=({x}, {y}) {width}x{height}, inset={inset}")
print(f"   -> ({left}, {top}) to ({right}, {bottom})")
assert right - left == width - 2 * inset == 76
print("   CONFIRMED: 60x20 widget yields a 76x36 grab, and the pre-fix")
print("   `right <= left` guard cannot see it — the box only got bigger.\n")

print("4. winfo_ismapped() on a destroyed widget — raw TclError, or clean 0?")
root = tkinter.Tk()
root.geometry("200x100+50+50")
root.deiconify()
root.update()
label = ttk.Label(root, text="probe")
label.pack()
root.update()
print(f"   alive: ismapped={label.winfo_ismapped()} exists={label.winfo_exists()}")
label.destroy()
root.update()
print(f"   destroyed: exists={label.winfo_exists()}")
try:
    mapped = label.winfo_ismapped()
except tkinter.TclError as exc:
    print(f"   CONFIRMED: ismapped() RAISES -> {type(exc).__name__}: {exc}")
    print("   Pre-fix, that escaped capture() as a raw toolkit error.")
else:  # pragma: no cover - would mean the finding was wrong
    print(f"   ismapped() returned {mapped} without raising.")
    print("   The pre-fix path gave a clean BootstackError; finding overstated.")
root.destroy()