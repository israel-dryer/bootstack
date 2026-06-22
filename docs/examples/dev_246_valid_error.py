"""Dev demo for #246 — TextArea and CodeEditor reactive .valid / .error signals.

Demonstrates the new .valid (Signal[bool]) and .error (Signal[str]) properties
added to TextArea and CodeEditor. Validation runs on blur or via validate().

Run with:
    python docs/examples/dev_246_valid_error.py
"""
import bootstack as bs

with bs.App(title="#246 - .valid / .error signals", padding=20, gap=16) as app:

    # TextArea ---------------------------------------------------------------
    bs.Label("TextArea Validation", font="heading-sm")

    ta = bs.TextArea(label="Notes", required=True, height=4, placeholder="Type at least 10 chars...")
    ta.add_validation_rule("stringLength", min=10, message="Minimum 10 characters.")

    ta_status = bs.Signal("valid: True")
    ta.valid.subscribe(lambda ok: ta_status.set(f"valid: {ok}"))

    bs.Label(textsignal=ta_status, accent="secondary")
    bs.Label(textsignal=ta.error, accent="secondary")

    with bs.Row(gap=8):
        bs.Button("Validate", on_click=lambda: ta.validate())
        bs.Button("Clear", accent="secondary", on_click=lambda: ta.clear())

    bs.Divider()

    # CodeEditor -------------------------------------------------------------
    bs.Label("CodeEditor Validation", font="heading-sm")

    ed = bs.CodeEditor(language="python", height=6)
    ed.add_validation_rule("required", message="Editor cannot be empty.")
    ed.add_validation_rule("stringLength", min=20, message="Minimum 20 characters.")

    ed_status = bs.Signal("valid: True")
    ed.valid.subscribe(lambda ok: ed_status.set(f"valid: {ok}"))

    bs.Label(textsignal=ed_status, accent="secondary")
    bs.Label(textsignal=ed.error, accent="secondary")

    with bs.Row(gap=8):
        bs.Button("Validate", on_click=lambda: ed.validate())
        bs.Button("Seed content", accent="secondary", on_click=lambda: ed.insert("print('hello, world!')\n"))

app.run()
