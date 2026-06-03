"""TextArea — full feature demo.

Demonstrates basic usage, scrollbar modes, placeholder, label and message,
max length, reactive signal binding, states, undo/redo, and change handling.

Run with:
    python docs/examples/textarea.py
"""

import bootstack as bs

with bs.App(title="TextArea Demo", padding=20, gap=16) as app:

    # Basic usage
    bs.Label("Basic", font="heading-sm")
    bs.TextArea(placeholder="Start typing…", height=3)

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.TextArea(
        label="Description",
        message="Markdown supported.",
        placeholder="Write a short description…",
        height=4,
    )

    # Max length
    bs.Label("Max Length", font="heading-sm")
    bs.TextArea(
        label="Bio",
        placeholder="Tell us about yourself…",
        max_length=200,
        message="Maximum 200 characters.",
        height=3,
    )

    # Scrollbars
    bs.Label("Scrollbars", font="heading-sm")
    with bs.HStack(gap=8):
        bs.TextArea(label="auto",     scrollbars="auto",     height=3)
        bs.TextArea(label="vertical", scrollbars="vertical", height=3)
        bs.TextArea(label="none",     scrollbars="none",     height=3)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    content = bs.Signal("")
    bs.TextArea(label="Notes", textsignal=content, height=3)
    bs.Label(textsignal=content, accent="secondary")

    # States
    bs.Label("States", font="heading-sm")
    bs.TextArea(value="Editable content.", label="Normal",    height=3)
    bs.TextArea(value="Read-only content.", label="Read only", height=3, read_only=True)

    # Undo / redo
    bs.Label("Undo / Redo", font="heading-sm")
    ta = bs.TextArea(label="Try editing, then click Undo", height=3)
    with bs.HStack(gap=8):
        bs.Button("Undo", on_click=lambda: ta.undo())
        bs.Button("Redo", on_click=lambda: ta.redo())

    # Dirty tracking
    bs.Label("Dirty Tracking", font="heading-sm")
    dirty_sig = bs.Signal("not modified")
    ta2 = bs.TextArea(label="Edit me", height=3)
    ta2.on_input(lambda e: dirty_sig.set("modified" if ta2.is_dirty else "not modified"))
    bs.Label(textsignal=dirty_sig, accent="secondary")

    # Handling changes
    bs.Label("Handling Changes", font="heading-sm")
    last = bs.Signal("(none)")
    ta3 = bs.TextArea(label="Type and blur to commit", height=3)
    ta3.on_change(lambda e: last.set(f"{len(ta3.value)} chars"))
    bs.Label(textsignal=last, accent="secondary")

app.run()