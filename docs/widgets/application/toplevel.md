---
title: Toplevel
---

# Toplevel

`Toplevel` creates a **secondary window** that shares the application's theme and event loop.

Use it for dialogs, tool palettes, inspectors, or any auxiliary window.

---

## Quick start

```python
import bootstack as bs

app = bs.App(title="Main Window")

def open_window():
    win = bs.Toplevel(title="Settings", minsize=(400, 300))
    bs.Label(win, text="Secondary window").pack(padx=20, pady=20)

bs.Button(app, text="Open Window", command=open_window).pack(pady=20)

app.mainloop()
```

---

## When to use

Use `Toplevel` when:

- you need a secondary window (settings panel, inspector, tool palette)

- you need a custom dialog beyond what the built-in dialogs provide

Consider a different control when:

- you need the main application window â€” use [App](app.md)

- you need a standard dialog â€” see [Dialogs](../dialogs/index.md)

---

## Additional resources

### Related widgets

- [App](app.md) â€” main application window

- [AppShell](appshell.md) â€” app window with built-in navigation

### API reference

- [`bootstack.Toplevel`](../../reference/app/Toplevel.md)
