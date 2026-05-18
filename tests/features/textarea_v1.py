"""Visual test for TextArea v1 — form field API.

Covers: value=, label=, message=, required=, placeholder=, max_length=,
read_only=, accent=, scrollbars=, on_input=, on_changed=, on_valid=,
on_invalid=, undo/redo, textsignal=, add_validation_rule.
"""
import bootstack as bs

app = bs.App(title="TextArea — form field", minsize=(640, 780))
log_var = bs.Signal("")

def log(msg):
    log_var.set(msg)
    print(msg)


outer = bs.PackFrame(app, direction="column", gap=12, padding=12)
outer.pack(fill="both", expand=True)

# 1. label + message + scrollbars
bs.Label(outer, text="1. label= + message= + scrollbars='auto'", font="body[bold]").pack(anchor="w")
ta1 = bs.TextArea(outer, label="Notes", message="Enter your notes here.",
                  show_message=True, height=3, scrollbars="auto",
                  value="Type here. Scrollbar appears when content overflows.")
ta1.pack(fill="x")

# 2. on_input (every edit) + on_changed (on blur)
bs.Label(outer, text="2. on_input + on_changed", font="body[bold]").pack(anchor="w")
ta2 = bs.TextArea(outer, label="Tracked", height=3, scrollbars="auto")
ta2.pack(fill="x")
ta2.on_input(lambda e: log(f"on_input: value={e.data['value'][:30]!r}"))
ta2.on_changed(lambda e: log(f"on_changed (blur): value={e.data['value'][:30]!r}"))
ta2.on_modified(lambda e: log(f"on_modified: is_dirty={e.data['is_dirty']}"))

# 3. max_length
bs.Label(outer, text="3. max_length=40", font="body[bold]").pack(anchor="w")
ta3 = bs.TextArea(outer, label="Limited (40 chars)", height=2, max_length=40)
ta3.pack(fill="x")

# 4. required= + validation
bs.Label(outer, text="4. required= (blur to validate)", font="body[bold]").pack(anchor="w")
ta4 = bs.TextArea(outer, label="Required field", height=2, required=True)
ta4.pack(fill="x")
ta4.on_invalid(lambda e: log(f"on_invalid: {e.data['message']}"))
ta4.on_valid(lambda e: log("on_valid: field is valid"))

# 5. read_only
bs.Label(outer, text="5. read_only=True", font="body[bold]").pack(anchor="w")
ta5 = bs.TextArea(outer, label="Read-only", height=2, read_only=True,
                  value="This text cannot be edited.")
ta5.pack(fill="x")

# 6. placeholder
bs.Label(outer, text="6. placeholder=", font="body[bold]").pack(anchor="w")
ta6 = bs.TextArea(outer, height=2, placeholder="Click here and start typing...")
ta6.pack(fill="x")

# 7. textsignal
bs.Label(outer, text="7. textsignal=", font="body[bold]").pack(anchor="w")
sig = bs.Signal("Signal-driven content.")
ta7 = bs.TextArea(outer, height=2, textsignal=sig)
ta7.pack(fill="x")
sig_row = bs.PackFrame(outer, direction="row", gap=6)
sig_row.pack(fill="x")
bs.Button(sig_row, text="Set 'Hello'",  command=lambda: sig.set("Hello")).pack(side="left")
bs.Button(sig_row, text="Set 'World'",  command=lambda: sig.set("World")).pack(side="left")

# 8. undo/redo
bs.Label(outer, text="8. Undo / Redo (Ctrl+Z / Ctrl+Shift+Z)", font="body[bold]").pack(anchor="w")
ta8 = bs.TextArea(outer, height=3, scrollbars="vertical")
ta8.pack(fill="x")
btn_row = bs.PackFrame(outer, direction="row", gap=6)
btn_row.pack(fill="x")
bs.Button(btn_row, text="Undo",       command=ta8.undo).pack(side="left")
bs.Button(btn_row, text="Redo",       command=ta8.redo).pack(side="left")
bs.Button(btn_row, text="is_dirty?",
          command=lambda: log(f"is_dirty = {ta8.is_dirty}")).pack(side="left")
bs.Button(btn_row, text="mark_saved()",
          command=lambda: (ta8.mark_saved(), log("mark_saved()"))).pack(side="left")
ta8.on_undo(lambda e: log(f"on_undo: value={e.data['value'][:30]!r}"))
ta8.on_redo(lambda e: log(f"on_redo: value={e.data['value'][:30]!r}"))

# ── status bar ────────────────────────────────────────────────────────────────
bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()