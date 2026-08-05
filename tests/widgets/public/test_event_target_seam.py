"""Regression tests for `emit()` and `on()` targeting different widgets (#396).

A field widget is a frame wrapping the entry the user actually types in, and the
text-editing events fire on that inner entry. Ten public wrappers overrode `on()`
to bind there — but `emit()` was never given the matching treatment and still
fired on the outer frame. So `field.emit("change", data=...)` could not reach a
handler registered by `field.on_change(...)`, flatly contradicting `emit()`'s own
documentation that it takes "the same name you pass to `on()`".

The duplication between the two routes *was* the defect, so the fix is not an
`emit()` override alongside every `on()` — that re-creates the same hazard in a
second place. Both now resolve the target through one seam,
`PublicWidgetBase._event_target(sequence)`, which a subclass overrides instead of
reimplementing `on()`.

Widgets whose `on`/`emit` already agreed (e.g. `Slider`) were unaffected, which
is why the suite never caught this — hence the control test at the bottom.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.events import ChangeEvent

# The wrappers that retarget to an inner entry/text widget.
RETARGETING = [
    ("TextField", lambda: bs.TextField()),
    ("PasswordField", lambda: bs.PasswordField()),
    ("PathField", lambda: bs.PathField()),
    ("NumberField", lambda: bs.NumberField()),
    ("SpinnerField", lambda: bs.SpinnerField()),
    ("DateField", lambda: bs.DateField()),
    ("TimeField", lambda: bs.TimeField()),
    ("Select", lambda: bs.Select(options=["a", "b"])),
    ("TextArea", lambda: bs.TextArea()),
    ("CodeEditor", lambda: bs.CodeEditor()),
]
_IDS = [n for n, _ in RETARGETING]


@pytest.mark.parametrize("name,make", RETARGETING, ids=_IDS)
def test_emit_reaches_a_handler_registered_with_on_change(app, name, make):
    widget = make()
    seen = []
    widget.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    widget.emit("change", data=ChangeEvent(value="x"))
    app._tk_root.update()

    assert seen == ["x"], f"{name}: emit() did not reach on_change()"


@pytest.mark.parametrize("name,make", RETARGETING, ids=_IDS)
def test_on_and_emit_resolve_to_the_same_widget(app, name, make):
    """The structural invariant behind the behavioral test above.

    Asserted separately because the behavioral check can only fail once the two
    have already drifted; this one states the property that must hold.
    """
    widget = make()
    sub = widget.on("change", lambda e: None)
    app._tk_root.update_idletasks()

    assert str(sub._widget) == str(widget._event_target("<<Change>>"))


def test_stream_route_retargets_identically(app):
    # `on()` with no handler takes a separate lazy path; it must not drift from
    # the direct-handler path.
    field = bs.TextField()
    seen = []
    field.on("change").listen(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field.emit("change", data=ChangeEvent(value="streamed"))
    app._tk_root.update()

    assert seen == ["streamed"]


def test_a_non_retargeted_event_still_fires_on_the_outer_widget(app):
    # The seam must only move the sequences that belong to the inner entry.
    # `<Configure>` is not one of them, so it stays on the frame.
    field = bs.TextField()
    assert str(field._event_target("<Configure>")) == str(field._internal)


def test_emit_of_a_native_event_does_not_edit_the_field(app):
    """`emit()` notifies listeners; it must not act as the user.

    Three of the names a field registers — `submit`, `focus`, `blur` — map onto
    real toolkit sequences rather than framework ones. `on()` binds those on the
    inner entry because that is where the toolkit delivers them, but *generating*
    one there hands it to the handlers the field installed for its own use.
    Measured before this guard: `emit("focus")` cleared the placeholder outright
    and `emit("blur")` ran the commit path, publishing a change the user never
    made.
    """
    field = bs.TextField(placeholder="type here")
    changes: list = []
    field.on_change(lambda e: changes.append(e.value))
    app._tk_root.update_idletasks()

    before = field._internal._entry.get()
    field.emit("focus")
    field.emit("blur")
    field.emit("submit")
    app._tk_root.update()

    assert field._internal._entry.get() == before, "emit() edited the field's text"
    assert changes == [], f"emit() of a native event published a change: {changes}"


def test_emit_of_a_native_event_fires_on_the_outer_widget(app):
    """The structural invariant behind the test above.

    `on()` still retargets these sequences — only `emit()` declines to.
    """
    field = bs.TextField()
    fired: list = []

    outer, inner = field._internal, field._entry_widget()
    try:
        for widget, label in ((outer, "outer"), (inner, "inner")):
            def spy(*a, _label=label, _real=widget.event_generate, **kw):
                fired.append(_label)
                return _real(*a, **kw)

            widget.event_generate = spy  # type: ignore[method-assign]

        field.emit("blur")
        app._tk_root.update()
    finally:
        for widget in (outer, inner):
            widget.__dict__.pop("event_generate", None)

    assert fired == ["outer"]
    assert str(field._event_target("<FocusOut>")) == str(inner), (
        "on() must still bind native sequences on the inner entry"
    )


def test_slider_is_unaffected(shown_app):
    """Control: a widget that never retargeted still round-trips.

    `shown_app`, not `app`: Tk drops `event_generate` for a virtual event on a
    composite like Slider while the window is unmapped, and the `app` fixture's
    root is withdrawn. The field wrappers above are unaffected, so they use the
    cheaper fixture.
    """
    slider = bs.Slider(value=1)
    seen = []
    slider.on_change(lambda e: seen.append(getattr(e, "value", None)))
    shown_app._tk_root.update_idletasks()

    slider.emit("change", data=ChangeEvent(value=7))
    shown_app._tk_root.update()

    assert seen == [7]
