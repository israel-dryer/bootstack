---
title: Performance
---

# Performance

Tk has a single event loop. Every callback, every redraw, every layout pass
runs on it — and any callback that takes more than a few tens of
milliseconds is going to be felt as a stutter or freeze. Most "slow Tk"
problems are really *blocked event loop* problems.

This guide focuses on the four moves that solve almost every responsiveness
issue: get blocking work off the loop, chunk large updates, cache expensive
resources, and measure what's actually slow. Each is shown as a runnable
`bs.App(...)` snippet.

---

## Run blocking work off the event loop

Anything that takes longer than ~50 ms — file I/O, network requests, heavy
computation — should run on a worker thread. Then post the result back to
the UI via `after()`, because Tk widgets must only be touched from the main
thread.

The `concurrent.futures` thread pool gives you a clean pattern:

```python
from concurrent.futures import ThreadPoolExecutor
import time
import bootstack as bs

app = bs.App(title="Background work", size=(420, 200))
status = bs.Signal("Idle")

bs.Label(app, signal=status, font="body[bold]").pack(padx=20, pady=(20, 8))

bar = bs.Progressbar(app, mode="indeterminate")
bar.pack(fill="x", padx=20)

executor = ThreadPoolExecutor(max_workers=2)

def slow_work():
    # Pretend this is a network call or expensive computation.
    time.sleep(2.0)
    return "Loaded 1,234 rows"

def on_done(result):
    status.set(result)
    bar.stop()

def start():
    status.set("Working...")
    bar.start(10)
    future = executor.submit(slow_work)
    # Poll the future from the event loop, then post the result back.
    def check():
        if future.done():
            app.after(0, on_done, future.result())
        else:
            app.after(50, check)
    check()

bs.Button(app, text="Run", accent="primary", command=start).pack(pady=12)

app.mainloop()
```

Two things worth noting:

- `slow_work()` runs on the worker thread. It must not touch any widget.
- `on_done()` runs on the main thread (it's invoked through `after()`), so
  it's safe to update `status` and stop the progress bar there.

The `app.after(0, ...)` form schedules a callback for the next event-loop
turn. It's the canonical way to hop from a worker thread back to the UI.

When you need to schedule a `concurrent.futures` callback to run on the UI
thread, route it through `after()` — calling widget methods from
`Future.add_done_callback` directly will run them on the worker thread and
you'll get sporadic, hard-to-debug Tk errors.

---

## Chunk large updates with `after()`

Inserting 50,000 rows into a `TreeView` in one go will freeze the UI for
seconds. Splitting the work across event-loop turns keeps the UI
interactive — and gives the user a chance to see incremental progress.

```python
import bootstack as bs

app = bs.App(title="Chunked load", size=(480, 360))

tree = bs.TreeView(app, columns=("id", "value"), show="headings")
tree.heading("id", text="ID")
tree.heading("value", text="Value")
tree.pack(fill="both", expand=True, padx=12, pady=(12, 8))

status = bs.Signal("0 / 50,000")
bs.Label(app, signal=status).pack(pady=(0, 8))

TOTAL = 50_000
CHUNK = 500
data = [(i, f"row-{i}") for i in range(TOTAL)]

def insert_chunk(start=0):
    end = min(start + CHUNK, TOTAL)
    for i in range(start, end):
        tree.insert("", "end", values=data[i])
    status.set(f"{end:,} / {TOTAL:,}")
    if end < TOTAL:
        app.after_idle(insert_chunk, end)

insert_chunk()
app.mainloop()
```

Tune `CHUNK` until each chunk takes roughly 16 ms — that gives you ~60 fps
worth of interactivity while the load progresses. `after_idle` (rather than
`after(0, ...)`) lets the event loop service pending input and redraws
between chunks, which is exactly what you want.

Most data-display widgets benefit from this pattern. For larger datasets,
also consider feeding the widget through a [DataSource](datasource.md)
that loads pages on demand instead of materializing the whole set.

---

## Cache expensive resources

Reconstructing fonts and images is far more expensive than it looks.
`bs.Font` and `bs.Image` both cache for you — but only if you let them.

### Fonts

```python
import bootstack as bs

# ~~ slow: builds a fresh Font every iteration ~~
def make_label_slow(parent, text):
    return bs.Label(parent, text=text, font=bs.Font("body[bold]"))

# fast: build once, reuse forever
HEADING = bs.Font("heading-md[bold]")
BODY_BOLD = bs.Font("body[bold]")

def make_label(parent, text, *, heading=False):
    return bs.Label(parent, text=text, font=HEADING if heading else BODY_BOLD)
```

The `bs.Font` object caches its underlying Tk font internally on first use.
If you build a hundred `bs.Font("body[bold]")` instances, you'll create a
hundred Tk font objects — each of which has measurement and metric tables.
Module-level constants are the right answer.

### Images

`bs.Image.open()` is already cached by absolute path: calling it a thousand
times for the same file decodes once and returns the same `PhotoImage`
object every time after that. You can confirm this:

```python
import bootstack as bs

app = bs.App()
for _ in range(1000):
    bs.Image.open("assets/logo.png")
print(bs.Image.cache_info())  # ImageCacheInfo(items=1)
app.destroy()
```

If you're scaling images at runtime, do the resize *once* with PIL and feed
the result to `bs.Image.from_pil(..., key="logo-64")` — passing an explicit
`key` lets subsequent calls hit the cache instead of redecoding.

---

## Measure before you optimize

The trace decorator from
[Debugging → Time and trace your callbacks](debugging.md#time-and-trace-your-callbacks)
is the right starting point. Drop it on suspect callbacks and let the
numbers tell you where to look.

```python
import time
import bootstack as bs

def trace(name):
    def deco(fn):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            ms = (time.perf_counter() - start) * 1000
            print(f"[{name}] {ms:.1f} ms")
            return result
        return wrapper
    return deco

app = bs.App(title="Measure", size=(360, 160))

@trace("rebuild")
def rebuild():
    # Imagine this rebuilds a complex panel.
    sum(i * i for i in range(500_000))

bs.Button(app, text="Rebuild", command=rebuild).pack(padx=20, pady=20)
app.mainloop()
```

Two rules of thumb worth internalizing:

- **16 ms** is one frame at 60 fps. Anything longer is a visible hitch.
- **50 ms** is the threshold where users start to perceive the UI as
  unresponsive. Treat it as a budget, not a target.

If a callback exceeds the budget, the next move is one of: chunk it
(above), move it off the loop (above), or cache its inputs (above). In
practice, those three patterns cover the vast majority of UI performance
work.

---

## Common pitfalls

- **Touching widgets from a worker thread.** Always hop back via
  `after()`. Symptoms: random `RuntimeError`, segfaults, or silent missed
  updates.
- **Rebuilding the whole panel on every change.** If a signal change rebuilds
  hundreds of widgets, switch to updating widget content in place. See
  [Reactivity](reactivity.md) for binding patterns.
- **Recreating fonts and images per call.** Cache them as module
  constants or use `bs.Image`/`bs.Font` with explicit keys.
- **Loading large datasets synchronously.** Page through a
  [DataSource](datasource.md), or chunk inserts with `after_idle`.
- **Optimizing without measuring.** Trace first; the bottleneck is rarely
  where you'd guess.

---

## Next steps

- [Debugging](debugging.md) — diagnose what's actually slow.
- [Reactivity](reactivity.md) — efficient signal-driven updates.
- [DataSource](datasource.md) — paged data loading for large sets.
- [Architecture → Images & DPI](../architecture/images-and-dpi.md) — image
  performance and DPI scaling.
