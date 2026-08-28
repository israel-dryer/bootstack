"""`TextArea` and `CodeEditor` bind a `textsignal` in both directions (#486).

Two defects with one cause: the textarea core held the bound signal privately, so
it neither exposed it nor ever wrote to it.

- `.signal` read `getattr(self._internal, "signal", None)` against an object that
  has no such attribute, so the default fired on every call and the property
  returned `None` even with a signal bound.
- `bind_signal` subscribed to the signal and drove the widget from it, but
  nothing anywhere called `self._signal.set(...)`, so an edit never travelled
  back. The documented contract is two-way.

⚠ THE ECHO GUARD IS A VALUE COMPARISON, NOT A SUSPEND FLAG, AND THAT IS LOAD
BEARING. `ChangeNotifier` emits `<<Change>>` with `when="tail"`, so the event is
delivered asynchronously — a flag raised around the write is already lowered by
the time the handler runs, and would miss the echo every time. That is the trap
`Form` hit in PR #354. `test_alternating_writes_do_not_echo` is what would catch
a regression back to a flag: a loop shows up as runaway subscriber counts, which
no single-write test can see.
"""
from __future__ import annotations

import gc

import pytest

import bootstack as bs

WIDGETS = [
    ("TextArea", lambda **kw: bs.TextArea(**kw)),
    ("CodeEditor", lambda **kw: bs.CodeEditor(**kw)),
]
IDS = [w[0] for w in WIDGETS]


def _pump(app, times: int = 4) -> None:
    """Drain the queue. `<<Change>>` is queued `when="tail"`, so idle tasks alone
    do not deliver it — only a full `update()` does."""
    for _ in range(times):
        app.tk.update()
        app.tk.update_idletasks()


def _core(widget):
    """The textarea core behind either public widget."""
    inner = widget._internal
    return inner.core if hasattr(inner, "core") else inner


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_a_signal_write_reaches_the_widget(app, name, factory):
    # The half that already worked. Here so the write-back cannot regress it.
    sig = bs.Signal("start")
    widget = factory(textsignal=sig)
    _pump(app)

    sig.set("from signal")
    _pump(app)

    assert widget.value == "from signal"


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_an_edit_reaches_the_signal(app, name, factory):
    sig = bs.Signal("start")
    widget = factory(textsignal=sig)
    _pump(app)

    widget.value = "typed by user"
    _pump(app)

    assert sig() == "typed by user"


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_a_real_text_edit_reaches_the_signal(app, name, factory):
    # The test above drives the public `value` setter. This one inserts into the
    # text widget the way a keystroke does, so the write-back is proven to ride
    # the edit path rather than the setter.
    sig = bs.Signal("")
    widget = factory(textsignal=sig)
    _pump(app)

    _core(widget).text.insert("end", "abc")
    _pump(app)

    assert sig() == "abc"


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_the_signal_property_returns_the_bound_signal(app, name, factory):
    # Identity, not equality: an `is not None` assertion would pass just as well
    # against a second, unrelated signal.
    sig = bs.Signal("bound")
    widget = factory(textsignal=sig)

    assert widget.signal is sig


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_the_signal_property_is_none_when_nothing_is_bound(app, name, factory):
    # Pinned by #460 as well. These two are annotated `| None` correctly and
    # must NOT be swept into that issue's population.
    assert factory().signal is None


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_alternating_writes_do_not_echo(app, name, factory):
    sig = bs.Signal("start")
    seen = []
    sig.subscribe(seen.append)
    widget = factory(textsignal=sig)
    _pump(app)
    baseline = len(seen)

    for i in range(10):
        sig.set("s%d" % i)
        _pump(app, 2)
        widget.value = "w%d" % i
        _pump(app, 2)

    fired = len(seen) - baseline
    # 20 writes in, so 20 notifications out. A feedback loop is unbounded, not
    # merely a little over, which is why the ceiling can be this tight.
    assert fired <= 25, "signal fired %d times for 20 writes — echo loop" % fired
    assert sig() == widget.value == "w9"


def _change_bindings(widget) -> str:
    """The Tcl script bound to `<<Change>>` on the core's text widget.

    A released binding leaves the script; an orphaned one stays in it. This is
    the only observable that moves, which is why the test below reads it —
    see the comment there.
    """
    text = _core(widget).text
    return text.tk.call("bind", str(text), "<<Change>>")


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_rebinding_releases_the_previous_hooks(app, name, factory):
    # ⚠ THIS ASSERTS ON THE HOOKS, NOT ON THE REPLACED SIGNAL'S VALUE, AND THAT
    # IS THE WHOLE POINT OF THE TEST. `_push_to_signal` is a bound method that
    # reads `self._signal` at call time, so an orphaned <<Change>> binding
    # pushes into the CURRENT signal and can never write into the replaced one.
    # An earlier version closed on `first() == "one"` and therefore passed with
    # the release deleted -- measured, one orphan binding left and both value
    # assertions still green. What a leaked hook actually costs is a duplicate
    # binding and a live subscription per rebind, which is #479's shape, so
    # those are what get asserted.
    first = bs.Signal("one")
    second = bs.Signal("two")
    widget = factory(textsignal=first)
    _pump(app)
    stale_bind_id = _core(widget)._signal_change_bind_id
    assert stale_bind_id, "precondition failed — nothing was bound to push"

    _core(widget).bind_signal(second)
    _pump(app)
    widget.value = "after rebind"
    _pump(app)

    assert stale_bind_id not in _change_bindings(widget), (
        "the previous <<Change>> push binding is still installed"
    )
    assert not first._subscribers, (
        "the replaced signal still has %d subscriber(s)" % len(first._subscribers)
    )
    assert second() == "after rebind"
    assert first() == "one", "the replaced signal is still receiving edits"


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_a_non_text_signal_is_refused_at_construction(app, name, factory):
    # Matches what the entry-backed fields already do, where the clash surfaces
    # through the signal's own variable. Without this the first edit would call
    # set() with a str inside a Tk callback, where the failure is invisible.
    with pytest.raises(TypeError, match="Expected int, got str"):
        factory(textsignal=bs.Signal(123))


def test_the_refusal_matches_the_entry_backed_fields(app):
    """The consistency claim, asserted rather than assumed."""
    messages = {}
    for label, factory in [("TextField", bs.TextField)] + WIDGETS:
        try:
            factory(textsignal=bs.Signal(123))
        except TypeError as exc:
            messages[label] = str(exc)

    assert len(messages) == 3, "a widget accepted an int textsignal: %s" % (messages,)
    assert len(set(messages.values())) == 1, "refusal messages diverge: %s" % (messages,)


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_a_destroyed_widget_stops_receiving_and_raises_nothing(app, name, factory):
    # A live subscription outliving its widget is #479's shape: the emit happens
    # inside a Tk trace, where an exception never reaches Python. The
    # background-error channel IS the observable here.
    root = app.tk
    seen = []
    root.tk.createcommand("bgerror", lambda *a: seen.append(a[0] if a else ""))
    try:
        sig = bs.Signal("start")
        widget = factory(textsignal=sig)
        _pump(app)

        _core(widget).destroy()
        _pump(app)
        gc.collect()

        sig.set("after destroy")
        _pump(app)

        assert not seen, "background error after destroy: %s" % (seen[:1],)
    finally:
        try:
            root.deletecommand("bgerror")
        except Exception:
            pass


# ── the placeholder is chrome, not content (round 1, finding 1) ────────────
#
# The write-back lives on the core, which holds the raw document. The composite
# above inserts the placeholder INTO that document to render it, so the core
# cannot tell the user's content from the widget's chrome on its own -- and the
# first version of the write-back pushed the placeholder string into the
# caller's signal. `TextArea` is the whole population: `CodeEditor` has no
# placeholder.
#
# The composite already treats a visible placeholder as "not content" in three
# other places -- `value` returns "", and both `<<Input>>` and `<<Changed>>` are
# suppressed -- so the signal was the one observable of the same widget that
# disagreed with the rest. The entry-backed family answered the same question by
# detaching the textvariable while the placeholder shows (`textentry_part.py`,
# "so the Signal is never set to the placeholder text").


def _blur(app, widget) -> None:
    """Drive a real `<FocusOut>` at the core text, which is where the composite
    binds the handler that shows the placeholder."""
    _core(widget).text.event_generate("<FocusOut>")
    _pump(app)


def test_the_placeholder_never_reaches_the_bound_signal(app):
    sig = bs.Signal("hello")
    ta = bs.TextArea(placeholder="Type something here", textsignal=sig)
    _pump(app)

    ta.value = ""
    _pump(app)
    _blur(app, ta)

    # Precondition: without it this passes vacuously whenever the placeholder
    # simply never appeared, which is the state the defect needs.
    assert ta._internal._showing_placeholder is True, (
        "precondition failed — the placeholder is not showing, so nothing was tested"
    )
    assert sig() == "", "the placeholder was written into the caller's signal: %r" % (sig(),)


def test_every_observable_agrees_while_the_placeholder_shows(app):
    # The invariant the finding actually broke: `text` and `value` are a pair and
    # must agree on whether the field is empty (`composites/field.py`). A signal
    # is a fourth reader of the same widget and does not get its own answer.
    sig = bs.Signal("hello")
    ta = bs.TextArea(placeholder="Type something here", textsignal=sig)
    _pump(app)

    changes: list = []
    inputs: list = []
    pushes: list = []
    ta.on_change(lambda e: changes.append(e.value))
    ta.on_input(lambda e: inputs.append(e.text))
    sig.subscribe(pushes.append)

    ta.value = ""
    _pump(app)
    changes.clear()
    inputs.clear()
    pushes.clear()

    _blur(app, ta)

    assert ta._internal._showing_placeholder is True, (
        "precondition failed — the placeholder is not showing, so nothing was tested"
    )
    assert ta.value == ""
    assert changes == [], "on_change reported the placeholder as a change: %r" % (changes,)
    assert inputs == [], "on_input reported the placeholder as input: %r" % (inputs,)
    assert pushes == [], "the signal reported the placeholder as content: %r" % (pushes,)
    assert sig() == ""


def test_a_placeholder_does_not_switch_the_write_back_off(app):
    # The control that bounds the guard. Suppressing the write-back entirely
    # whenever `placeholder=` was passed would satisfy both tests above while
    # reinstating exactly the one-way binding #486 exists to remove -- so this
    # asserts an edit still travels, on a widget that HAS a placeholder, and
    # that the placeholder comes back afterwards without polluting anything.
    sig = bs.Signal("hello")
    ta = bs.TextArea(placeholder="Type something here", textsignal=sig)
    _pump(app)

    ta.value = "typed by user"
    _pump(app)
    assert sig() == "typed by user", "the write-back is off on a placeholder widget"

    ta.value = ""
    _pump(app)
    _blur(app, ta)

    assert ta._internal._showing_placeholder is True
    assert sig() == ""


def test_a_code_write_while_the_placeholder_shows_is_not_reverted(app):
    # The reader seam has to have a writer to match it. `_on_signal_change`
    # writing the core's raw document leaves `_showing_placeholder` standing;
    # the reader then answers "" for a document that is not empty, and the push
    # sends that "" straight back over the caller's write -- so `sig.set(...)`
    # from application code is silently LOST. Found by driving the demo, not by
    # the suite, and it is why the write goes through the composite's setter.
    sig = bs.Signal("hello")
    ta = bs.TextArea(placeholder="Type something here", textsignal=sig)
    _pump(app)

    ta.value = ""
    _pump(app)
    _blur(app, ta)
    assert ta._internal._showing_placeholder is True, (
        "precondition failed -- the placeholder is not showing, so nothing was tested"
    )

    sig.set("written by code")
    _pump(app)

    assert sig() == "written by code", "the widget reverted the caller's write: %r" % (sig(),)
    assert ta.value == "written by code"
    assert ta._internal._showing_placeholder is False, (
        "the placeholder is still marked as showing over real content"
    )


# ── the EDIT door, not the setter door ─────────────────────────────────────
#
# Every other test in this file writes `widget.value = ...`. That is one of two
# doors into the write-back, and the other one -- an actual edit -- was untested.
# Two problems in this branch came out of that gap: a code write while the
# placeholder showed was silently reverted, and the round 1 record justified the
# fix with an invariant that does not hold for the family.
#
# ⚠ THESE DRIVE `text.insert` / `text.delete`, NOT SYNTHESIZED KEYS, AND THAT IS
# MEASURED RATHER THAN STYLISTIC. A `<KeyPress-a>` generated in the shared-root
# suite does NOTHING: the root is withdrawn, so `focus_force` is a silent no-op
# on an unmapped widget, the key never reaches the Text's class bindings, and the
# document stays empty -- a test built on it passes or fails for reasons that have
# nothing to do with the write-back. `insert` rides the same `WidgetRedirector`
# a keystroke does, which is the leg this file needs to cover; the key-to-insert
# leg above it belongs to the toolkit.


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_an_incremental_edit_reaches_the_signal(app, name, factory):
    # Asserted after EVERY character, not just at the end: a write-back that only
    # fired on whole-document replacement -- which is all the setter tests can
    # see -- would still pass a single end-state assertion.
    sig = bs.Signal("")
    widget = factory(textsignal=sig)
    _pump(app)
    text = _core(widget).text

    for i, ch in enumerate("abc", start=1):
        text.insert("end", ch)
        _pump(app)
        assert sig() == "abc"[:i], (
            "the signal did not follow edit %d: %r" % (i, sig())
        )

    text.delete("1.0", "end")
    _pump(app)
    assert sig() == ""


def test_clearing_by_editing_then_blurring_keeps_the_placeholder_out(app):
    # The finding's scenario reached through the edit door instead of the setter.
    sig = bs.Signal("hello")
    ta = bs.TextArea(placeholder="Type something here", textsignal=sig)
    _pump(app)
    text = _core(ta).text

    text.delete("1.0", "end")
    _pump(app)
    assert sig() == "", "clearing by editing did not reach the signal: %r" % (sig(),)

    _blur(app, ta)

    assert ta._internal._showing_placeholder is True, (
        "precondition failed -- the placeholder is not showing, so nothing was tested"
    )
    assert sig() == "", "the placeholder was written into the signal: %r" % (sig(),)
    assert ta.value == ""
