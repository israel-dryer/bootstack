"""#246 — TextArea and CodeEditor reactive .valid / .error signals.

Both widgets should expose:
  .valid  — Signal[bool], starts True, updates on each validation run
  .error  — Signal[str], starts "", contains the error message on failure

Validation runs:
  - On blur (FocusOut on the inner text widget) when rules are present
  - On manual validate() call

These tests cover:
  - Initial signal state (valid=True, error="")
  - Signal updates after manual validate()
  - Signal updates after blur-triggered validation
  - Signal subscriber notification
  - Both widgets share the same contract
"""
import pytest
import bootstack as bs


# ── TextArea ──────────────────────────────────────────────────────────────────

def test_textarea_valid_signal_initial_state(app):
    ta = bs.TextArea(required=True)
    assert ta.valid() is True
    assert ta.error() == ""


def test_textarea_valid_signal_fails_on_empty_required(app):
    ta = bs.TextArea(required=True, value="")
    result = ta.validate()
    assert result is False
    assert ta.valid() is False
    assert ta.error() != ""


def test_textarea_valid_signal_passes_on_content(app):
    ta = bs.TextArea(required=True, value="hello")
    result = ta.validate()
    assert result is True
    assert ta.valid() is True
    assert ta.error() == ""


def test_textarea_valid_signal_resets_after_correction(app):
    ta = bs.TextArea(required=True, value="")
    ta.validate()
    assert ta.valid() is False

    ta.value = "fixed"
    ta.validate()
    assert ta.valid() is True
    assert ta.error() == ""


def test_textarea_valid_signal_notifies_subscriber(app):
    ta = bs.TextArea(required=True, value="")
    collected = []
    ta.valid.subscribe(lambda v: collected.append(v))

    ta.validate()   # fails → False
    assert False in collected

    ta.value = "ok"
    ta.validate()   # passes → True
    assert True in collected


def test_textarea_error_signal_notifies_subscriber(app):
    ta = bs.TextArea(required=True, value="")
    errors = []
    ta.error.subscribe(lambda msg: errors.append(msg))

    ta.validate()
    assert any(e != "" for e in errors)


def test_textarea_blur_triggers_validation(app):
    ta = bs.TextArea(required=True, value="")
    # Simulate blur: call the internal handler directly (event_generate does not
    # call Python bindings without a running event loop — the integration is
    # covered by the manual validate() tests above; this checks the blur path).
    ta._internal._on_focus_out(None)
    assert ta.valid() is False


def test_textarea_manual_validate_runs_blur_rules(app):
    # stringLength defaults to trigger="blur"; manual validate() must still run it.
    ta = bs.TextArea(value="hi")
    ta.add_validation_rule("stringLength", min=10, message="Too short.")
    result = ta.validate()
    assert result is False
    assert ta.valid() is False
    assert ta.error() == "Too short."


def test_textarea_no_rules_valid_stays_true(app):
    ta = bs.TextArea(value="whatever")
    ta.validate()
    assert ta.valid() is True
    assert ta.error() == ""


# ── CodeEditor ────────────────────────────────────────────────────────────────

def test_codeeditor_valid_signal_initial_state(app):
    ed = bs.CodeEditor(value="")
    assert ed.valid() is True
    assert ed.error() == ""


def test_codeeditor_valid_signal_fails_on_required_empty(app):
    ed = bs.CodeEditor(value="")
    ed.add_validation_rule("required")
    result = ed.validate()
    assert result is False
    assert ed.valid() is False
    assert ed.error() != ""


def test_codeeditor_valid_signal_passes_on_content(app):
    ed = bs.CodeEditor(value="print('hi')")
    ed.add_validation_rule("required")
    result = ed.validate()
    assert result is True
    assert ed.valid() is True
    assert ed.error() == ""


def test_codeeditor_valid_signal_resets_after_correction(app):
    ed = bs.CodeEditor(value="")
    ed.add_validation_rule("required")
    ed.validate()
    assert ed.valid() is False

    ed.value = "x = 1"
    ed.validate()
    assert ed.valid() is True
    assert ed.error() == ""


def test_codeeditor_valid_signal_notifies_subscriber(app):
    ed = bs.CodeEditor(value="")
    ed.add_validation_rule("required")
    collected = []
    ed.valid.subscribe(lambda v: collected.append(v))

    ed.validate()   # fails → False
    assert False in collected

    ed.value = "ok"
    ed.validate()   # passes → True
    assert True in collected


def test_codeeditor_blur_triggers_validation(app):
    ed = bs.CodeEditor(value="")
    ed.add_validation_rule("required")
    # Simulate blur via the internal handler (event_generate does not call
    # Python bindings without a running event loop).
    ed._internal._on_focus_out_validate(None)
    assert ed.valid() is False


def test_codeeditor_manual_validate_runs_blur_rules(app):
    # stringLength defaults to trigger="blur"; manual validate() must still run it.
    ed = bs.CodeEditor(value="hi")
    ed.add_validation_rule("stringLength", min=10, message="Too short.")
    result = ed.validate()
    assert result is False
    assert ed.valid() is False
    assert ed.error() == "Too short."


def test_codeeditor_no_rules_valid_stays_true(app):
    ed = bs.CodeEditor(value="")
    ed.validate()
    assert ed.valid() is True
    assert ed.error() == ""
