"""Visual test for TextArea v1 (phases 1-3).

Covers: value=, label=, placeholder=, max_length=, read_only=, scrollbars=,
on_change=, undo/redo, is_dirty, textsignal=.
"""
import bootstack as bs

app = bs.App(title="TextArea v1", size=(640, 680))
log_var = bs.Signal("")

def log(msg):
    log_var.set(msg)
    print(msg)


outer = bs.PackFrame(app, direction="column", gap=12, padding=12)
outer.pack(fill="both", expand=True)

# 1. Basic with label
bs.Label(outer, text="1. label= + scrollbars='auto'", font="body[bold]").pack(anchor="w")
ta1 = bs.TextArea(outer, label="Notes", height=4, scrollbars="auto",
                  value="Type here. Scrollbar appears when content overflows.")
ta1.pack(fill="x")

# 2. on_change callback
bs.Label(outer, text="2. on_change + is_dirty", font="body[bold]").pack(anchor="w")
ta2 = bs.TextArea(outer, label="Tracked", height=3, scrollbars="auto")
ta2.pack(fill="x")
ta2.on_change(lambda e: log(f"on_change: op={e.data['op']}"))
ta2.on_modified(lambda e: log(f"on_modified: is_dirty={e.data['is_dirty']}"))

# 3. max_length
bs.Label(outer, text="3. max_length=40", font="body[bold]").pack(anchor="w")
ta3 = bs.TextArea(outer, label="Limited (40 chars)", height=2, max_length=40)
ta3.pack(fill="x")

# 4. read_only
bs.Label(outer, text="4. read_only=True", font="body[bold]").pack(anchor="w")
ta4 = bs.TextArea(outer, label="Read-only", height=2, read_only=True,
                  value="This text cannot be edited.")
ta4.pack(fill="x")

# 5. placeholder
bs.Label(outer, text="5. placeholder=", font="body[bold]").pack(anchor="w")
ta5 = bs.TextArea(outer, height=2, placeholder="Click here and start typing...")
ta5.pack(fill="x")

# 6. textsignal
bs.Label(outer, text="6. textsignal=", font="body[bold]").pack(anchor="w")
sig = bs.Signal("Signal-driven content.")
ta6 = bs.TextArea(outer, height=2, textsignal=sig)
ta6.pack(fill="x")

# 7. undo/redo
bs.Label(outer, text="7. Undo / Redo (also Ctrl+Z / Ctrl+Shift+Z)", font="body[bold]").pack(anchor="w")
ta7 = bs.TextArea(outer, height=3, scrollbars="vertical")
ta7.pack(fill="x")
btn_row = bs.PackFrame(outer, direction="row", gap=6)
btn_row.pack(fill="x")
bs.Button(btn_row, text="Undo", command=ta7.undo).pack(side="left")
bs.Button(btn_row, text="Redo", command=ta7.redo).pack(side="left")
ta7.on_undo(lambda e: log(f"on_undo: value={e.data['value'][:30]!r}"))
ta7.on_redo(lambda e: log(f"on_redo: value={e.data['value'][:30]!r}"))
bs.Button(btn_row, text="is_dirty?",
          command=lambda: log(f"is_dirty = {ta7.is_dirty}")).pack(side="left")
bs.Button(btn_row, text="mark_saved()",
          command=lambda: (ta7.mark_saved(), log("mark_saved() called"))).pack(side="left")

# Signal control
sig_row = bs.PackFrame(outer, direction="row", gap=6)
sig_row.pack(fill="x")
bs.Label(sig_row, text="Signal value:").pack(side="left")
bs.Button(sig_row, text="Set 'Hello'",
          command=lambda: sig.set("Hello")).pack(side="left")
bs.Button(sig_row, text="Set 'World'",
          command=lambda: sig.set("World")).pack(side="left")

# Status bar
bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()
