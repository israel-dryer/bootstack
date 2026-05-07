---
title: ScrolledText
---

# ScrolledText

`ScrolledText` is a multi-line text widget with integrated scrollbars and consistent mouse wheel support.

It wraps a `tkinter.Text` widget inside a themed container and delegates Text methods so you can use it like a normal
Text widget — just with better scrolling behavior and consistent theming.

Use `ScrolledText` for logs, notes, editors, and any situation where **text content** needs to scroll.

<figure markdown>
![scrolledtext states](../../assets/widgets-scrolledtext-states.png)
</figure>

---

## Quick start

```python
import bootstack as bs

app = bs.App()

st = bs.ScrolledText(app, height=10)
st.pack(fill="both", expand=True, padx=20, pady=20)

st.insert("end", "Insert your text here.\n" * 20)

app.mainloop()
```

---

## When to use

Use `ScrolledText` when:

- you need multi-line, scrollable text content (logs, notes, simple editors)
- you want integrated scrollbars and consistent wheel behavior

### Consider a different control when...

- you need a form-ready, validated single-line field — use [TextEntry](textentry.md)
- you need to scroll arbitrary widgets — use [ScrollView](../layout/scrollview.md)

---

## Examples and patterns

### Value model

`ScrolledText` is a direct wrapper around `tkinter.Text`:

- content is addressed by Text indices (`"1.0"`, `"end-1c"`, etc.)
- there is no commit-time value model

```python
st.insert("end", "Hello")
text = st.get("1.0", "end-1c")
```

### Scroll direction: `scroll_direction`

- `"vertical"` (default)
- `"horizontal"`
- `"both"`

```python
# Horizontal scrolling (wrap defaults to 'none' automatically)
code = bs.ScrolledText(app, scroll_direction="both")
```

When `scroll_direction` is `"horizontal"` or `"both"`, `wrap` is set to `"none"` automatically
unless you pass an explicit `wrap=` kwarg.

Horizontal scrolling uses **Shift + Mouse Wheel**.

### Wrapping: `wrap`

Override the automatic wrap setting if needed:

```python
# Force word wrap even with horizontal scrolling enabled
st = bs.ScrolledText(app, scroll_direction="both", wrap="word")
```

### Scrollbar visibility: `scrollbar_visibility`

- `"always"` (default)
- `"never"`
- `"hover"`
- `"scroll"` — auto-hide after `autohide_delay` milliseconds

```python
st = bs.ScrolledText(app, scrollbar_visibility="hover")
st = bs.ScrolledText(app, scrollbar_visibility="scroll", autohide_delay=1200)

# Change at runtime
st.configure(scrollbar_visibility="always")
```

### Scrollbar style: `scrollbar_style`

Apply an accent color to the scrollbars:

```python
st = bs.ScrolledText(app, scrollbar_style="primary")
st = bs.ScrolledText(app, scrollbar_style="danger")
```

### Padding: `padding`

Add inset space around the text area:

```python
st = bs.ScrolledText(app, padding=8)
```

### Access underlying Text: `text`

Use `st.text` to access the inner `tkinter.Text` widget directly:

```python
text_widget = st.text
text_widget.tag_configure("highlight", background="yellow")
```

### Events

For keyboard and focus events, bind to the inner `text` widget — not the outer container:

```python
# Correct: binds to the Text widget where keyboard events fire
st.text.bind("<KeyRelease>", lambda e: print("changed"))
st.text.bind("<FocusOut>",   lambda e: print("focus out"))
```

Using `st.bind(...)` binds to the outer `Frame` container, where keyboard events do not fire.

---

## Behavior

- Scrolling and mouse wheel behavior are handled internally for cross-platform consistency.
- `st.insert`, `st.get`, `st.delete`, and other `tkinter.Text` methods are available directly on `st` via delegation.
- The container and scrollbars participate in bootstack theming via `accent`.

For scrolling arbitrary widgets (forms, panels, composites), use [ScrollView](../layout/scrollview.md) instead.

---

## Additional resources

### Related widgets

- [TextEntry](textentry.md) — single-line, form-ready text control
- [Entry](../primitives/entry.md) — low-level single-line text input
- [ScrollView](../layout/scrollview.md) — scroll container for arbitrary widgets
- [Scrollbar](../layout/scrollbar.md) — scrollbar primitive used internally

### API reference

- [`bootstack.ScrolledText`](../../reference/widgets/ScrolledText.md)