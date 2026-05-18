"""Visual demo for TextArea v2 — form field features.

Demonstrates: focus border, accent=, label=, message=, required=,
add_validation_rule, on_input, on_changed, on_valid, on_invalid,
on_validated, validate() programmatic validation.
"""
import bootstack as bs

app = bs.App(title="TextArea — Form Field Demo", minsize=(700, 820))

# ── header ────────────────────────────────────────────────────────────────────

header = bs.PackFrame(app, direction="column", padding=(16, 12, 16, 0), gap=2)
header.pack(fill="x")
bs.Label(header, text="Submit a Support Ticket", font="heading-sm[bold]").pack(anchor="w")
bs.Label(header, text="All fields marked * are required.",
         font="caption", accent="secondary").pack(anchor="w")

bs.Separator(app).pack(fill="x", pady=8)

# ── form ──────────────────────────────────────────────────────────────────────

form = bs.PackFrame(app, direction="column", padding=(16, 0), gap=16)
form.pack(fill="both", expand=True)

# 1. Summary — required, minLength via custom rule
summary = bs.TextArea(
    form,
    label="Summary",
    message="Briefly describe the issue (10–200 characters).",
    show_message=True,
    required=True,
    height=2,
    placeholder="e.g. Login button unresponsive after password reset",
)
summary.add_validation_rule(
    "custom",
    message="Summary must be at least 10 characters.",
    func=lambda v: len(v.strip()) >= 10,
)
summary.pack(fill="x")

# 2. Description — required, accent="info"
description = bs.TextArea(
    form,
    label="Description",
    message="Include steps to reproduce, expected vs actual behaviour.",
    show_message=True,
    required=True,
    accent="info",
    height=5,
    placeholder="1. Go to...\n2. Click...\n3. Expected: ...\n4. Actual: ...",
)
description.pack(fill="x")

# 3. Steps to reproduce — optional, minLength custom rule
steps = bs.TextArea(
    form,
    label="Steps to reproduce (optional)",
    height=3,
    scrollbars="vertical",
)
steps.add_validation_rule(
    "custom",
    message="If provided, steps must be at least 20 characters.",
    func=lambda v: not v.strip() or len(v.strip()) >= 20,
)
steps.pack(fill="x")

# 4. Additional notes — read-only hint box, accent="secondary"
notes = bs.TextArea(
    form,
    label="Environment (auto-detected)",
    accent="secondary",
    height=2,
    read_only=True,
    value="Platform: Windows 11\nPython: 3.12 / Tk: 8.6",
)
notes.pack(fill="x")

# ── live event log ─────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x", pady=(8, 0))
log_frame = bs.PackFrame(app, direction="column", padding=(16, 8), gap=4)
log_frame.pack(fill="x")
bs.Label(log_frame, text="Live events", font="caption[bold]").pack(anchor="w")
log_sig = bs.Signal("(events appear here)")
bs.Label(log_frame, textsignal=log_sig, font="caption",
         surface="content").pack(fill="x")

def log(msg: str) -> None:
    log_sig.set(msg)
    print(msg)

summary.on_input(lambda e: log(f"summary on_input: {len(e.data['value'])} chars"))
summary.on_changed(lambda e: log(f"summary on_changed (blur): {e.data['value'][:40]!r}"))
summary.on_invalid(lambda e: log(f"summary INVALID: {e.data['message']}"))
summary.on_valid(lambda e: log("summary VALID ✓"))

description.on_invalid(lambda e: log(f"description INVALID: {e.data['message']}"))
description.on_valid(lambda e: log("description VALID ✓"))

steps.on_validated(lambda e: log(
    f"steps validated — is_valid={e.data['is_valid']}"
    + (f", message={e.data['message']!r}" if not e.data['is_valid'] else "")
))

# ── submit row ────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
action_row = bs.PackFrame(app, direction="row", gap=8, padding=(16, 10))
action_row.pack(fill="x")

def submit():
    all_valid = all(f.validate() for f in [summary, description, steps])
    if all_valid:
        log("✓ All fields valid — form submitted!")
    else:
        log("✗ Validation failed — fix errors above.")

bs.Button(action_row, text="Submit", command=submit, accent="primary").pack(side="left")
bs.Button(action_row, text="Reset", variant="ghost", command=lambda: (
    [setattr(f, "value", "") for f in [summary, description, steps]],
    log("Form reset."),
)).pack(side="left")

app.mainloop()