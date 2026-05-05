---
title: Debugging
---

# Debugging

Tk applications can feel opaque because the layout, redraw, and event work
happens inside the Tcl/Tk engine. The good news is that Tk is also extremely
introspectable — you just need a few patterns to make what's happening
visible.

This guide collects the patterns that pay off most often: instrumenting
callbacks, using `after_idle()` to fix layout-timing surprises, borderizing
widgets to see the layout you actually built, tracking focus, and resolving
the classic "image disappeared" bug.

Each example is a runnable `bs.App(...)` snippet. Copy, paste, run.

---

## Time and trace your callbacks

The first question for almost every "weird behavior" report is *which
callback is running, and how long does it take?* A small decorator answers
both.

```python
import time
import bootstack as bs

def trace(name):
    def deco(fn):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            print(f"[{name}] start")
            result = fn(*args, **kwargs)
            ms = (time.perf_counter() - start) * 1000
            print(f"[{name}] end ({ms:.1f} ms)")
            return result
        return wrapper
    return deco

app = bs.App(title="Tracing", size=(360, 160))

@trace("on_click")
def on_click():
    total = sum(i * i for i in range(2_000_000))
    print(f"  computed {total}")

bs.Button(app, text="Run", accent="primary", command=on_click).pack(padx=20, pady=20)

app.mainloop()
```

Press the button a few times. You'll see the duration printed for each call,
and you'll feel the UI freeze for the duration — concrete proof that the
callback is blocking the event loop. This is the cheapest measurement you
can add, and it should be your first move whenever the UI hitches.

For background work that *shouldn't* freeze the UI, see
[Performance → Run blocking work off the event loop](performance.md#run-blocking-work-off-the-event-loop).

---

## Use `after_idle()` for layout-timing bugs

A common source of confusion: you create a widget, immediately ask for its
size, and get `1` back. The widget hasn't been laid out yet — Tk schedules
geometry resolution for the *next* idle moment, which happens after your
constructor returns.

The fix is to defer the size-dependent code with `after_idle()`:

```python
import bootstack as bs

app = bs.App(title="after_idle()", size=(400, 200))

card = bs.Card(app)
card.pack(fill="both", expand=True, padx=20, pady=20)
bs.Label(card, text="Resize me").pack()

# WRONG: runs before layout has resolved
print("immediately:", card.winfo_width(), "x", card.winfo_height())

# RIGHT: runs after the event loop has done its first idle pass
def report_size():
    print("after idle:", card.winfo_width(), "x", card.winfo_height())

card.after_idle(report_size)

app.mainloop()
```

If you ever find yourself reading for `winfo_width`, `winfo_height`,
`winfo_x`, or `winfo_y` and getting `1` or `0`, the call is too early.
Wrap it in `after_idle()`.

The same pattern applies to focus-on-startup, scroll-to-position, and
resize-to-content logic — anything that depends on geometry being settled.

---

## Borderize widgets to see the layout

When the UI looks "off" but you can't tell which container is misbehaving,
make every container visible. `bs.Frame` accepts `show_border=True` and any
`surface=` token, which together let you light up the widget tree without
modifying the layout.

```python
import bootstack as bs

app = bs.App(title="Borderized", size=(480, 240))

# Each container shows its bounds and a contrasting surface.
outer = bs.Frame(app, surface="card", show_border=True, padding=8)
outer.pack(fill="both", expand=True, padx=12, pady=12)

left = bs.Frame(outer, surface="content", show_border=True, padding=8)
left.pack(side="left", fill="both", expand=True, padx=(0, 8))

right = bs.Frame(outer, surface="overlay", show_border=True, padding=8)
right.pack(side="right", fill="y")

bs.Label(left, text="Main pane").pack(anchor="nw")
bs.Label(right, text="Sidebar").pack(anchor="nw")

app.mainloop()
```

Once the borders show what's actually happening, the bug usually becomes
obvious — a missing `expand=True`, a `fill` on the wrong axis, a child that's
larger than its parent. Strip the borders and surfaces back out once you've
fixed the issue.

For the spacing/alignment vocabulary you'll need to interpret what you see,
read [Spacing & alignment](spacing-and-alignment.md).

---

## Track focus with bindings

Focus bugs ("why is Tab going there?", "why didn't this entry receive
keystrokes?") are easy to diagnose with a pair of bindings. Print the
widget that gains and loses focus and the picture clears up fast.

```python
import bootstack as bs

app = bs.App(title="Focus tracker", size=(360, 220))

def on_focus_in(event):
    w = event.widget
    print(f"FocusIn  -> {w.winfo_class()}  {w}")

def on_focus_out(event):
    w = event.widget
    print(f"FocusOut <- {w.winfo_class()}  {w}")

# bind_all so every widget reports — invaluable when the focus
# is going somewhere unexpected.
app.bind_all("<FocusIn>", on_focus_in)
app.bind_all("<FocusOut>", on_focus_out)

form = bs.PackFrame(app, direction="vertical", gap=8, padding=16)
form.pack(fill="both", expand=True)
bs.Label(form, text="Username").pack(anchor="w")
bs.Entry(form).pack(fill="x")
bs.Label(form, text="Password").pack(anchor="w")
bs.Entry(form, show="*").pack(fill="x")
bs.Button(form, text="Submit", accent="primary").pack(anchor="e")

app.mainloop()
```

`bind_all` is overkill for production code — it fires for every widget — but
it's perfect for diagnosis. Tab through the form and watch the order. If the
order surprises you, fix it with `takefocus=False` on widgets that shouldn't
receive focus, or by reordering construction.

---

## The "image disappeared" bug

This bug catches everyone exactly once: you load an image inside a function,
display it, and the image is blank. The reason is that Tk's `PhotoImage`
needs a live Python reference for the image data to survive — and as soon
as your function returns, Python garbage-collects it.

Reproduce:

```python
import bootstack as bs

app = bs.App(title="Disappearing image", size=(320, 240))

def add_logo(parent):
    # WRONG: photo is local. As soon as add_logo returns, the
    # PhotoImage is collected and the label shows blank.
    photo = bs.Image.transparent(64, 64)  # any image works for the demo
    bs.Label(parent, image=photo).pack(padx=20, pady=20)

add_logo(app)
app.mainloop()
```

Two ways to fix it. The simplest is `bs.Image` — bootstack's image cache
keeps a strong reference for you, so loading by path is safe even from
inside a function:

```python
def add_logo(parent):
    photo = bs.Image.open("assets/logo.png")  # cached, kept alive
    bs.Label(parent, image=photo).pack(padx=20, pady=20)
```

If you're constructing a `PhotoImage` directly (or any image whose lifetime
you manage yourself), keep the reference on the widget:

```python
def add_logo(parent):
    photo = bs.PhotoImage(file="assets/logo.png")
    label = bs.Label(parent, image=photo)
    label.image = photo  # the survival reference
    label.pack(padx=20, pady=20)
```

If an image renders in development but disappears in production, the cause
is almost always this. See [Platform → Images & DPI](../platform/images-and-dpi.md)
for more on image lifecycle and DPI considerations.

---

## Inspect the widget tree

When a layout is misbehaving and borders aren't enough, walk the tree.

```python
def dump_tree(widget, depth=0):
    indent = "  " * depth
    print(f"{indent}{widget.winfo_class()}  {widget}")
    for child in widget.winfo_children():
        dump_tree(child, depth + 1)

# call it on demand, e.g. from a debug menu or after construction:
dump_tree(app)
```

Pair this with `winfo_parent()`, `winfo_geometry()`, and `winfo_manager()`
on individual widgets when you need to confirm who owns what.

---

## Common pitfalls

- **Reading geometry inside `__init__`.** Wrap it in `after_idle()`.
- **Blocking the event loop.** If a callback runs longer than ~50 ms, the
  UI hitches. Trace it (above) to confirm, then move work off the loop —
  see [Performance](performance.md).
- **Losing image references.** Use `bs.Image` or attach the `PhotoImage`
  to the widget (`label.image = photo`).
- **Mixing `ttk.*` with `bs.*` styling.** bootstack styles its own widgets
  through the bootstyle system; raw `ttk` widgets won't pick up accent
  tokens. Stick to `bs.*` unless you have a specific reason not to.
- **Forgetting `bind_all` is global.** Useful for diagnosis, dangerous in
  production. Remove it once the bug is found.

---

## Next steps

- [Performance](performance.md) — keep the event loop responsive.
- [Reactivity](reactivity.md) — debugging signals and event flow.
- [Platform → Images & DPI](../platform/images-and-dpi.md) — image lifecycle and DPI.
- [Platform → Geometry & layout](../platform/geometry-and-layout.md) — how Tk
  resolves geometry, and why timing matters.
