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


@pytest.mark.parametrize("name,factory", WIDGETS, ids=IDS)
def test_rebinding_leaves_the_previous_signal_alone(app, name, factory):
    first = bs.Signal("one")
    second = bs.Signal("two")
    widget = factory(textsignal=first)
    _pump(app)

    _core(widget).bind_signal(second)
    _pump(app)
    widget.value = "after rebind"
    _pump(app)

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
