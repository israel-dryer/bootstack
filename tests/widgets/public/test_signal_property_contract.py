"""What `.signal` promises, per widget (#460).

Five public `signal` properties, covering seven widgets, were annotated
`Signal | None` and could never return `None`. They forwarded with
`getattr(self._internal, 'signal', None)`, so the default fired only when the
attribute was absent — and it never is, because the internal `signal` and
`textsignal` are properties that lazily create on first access. The default was
dead code and the `| None` half was unreachable, not merely unobserved.

⚠ THE BEHAVIOR DID NOT CHANGE, SO THE BEHAVIOR CANNOT REGRESSION-TEST THE FIX.
Every assertion about a live signal here passes identically at the pre-fix
commit. What this file pins is the CONTRACT — which widgets hand back a signal
and which hand back `None` — plus, in `test_no_public_signal_property_promises_a_none_it_cannot_produce`,
the annotation itself. That last test is the one that fails on the old code.

⚠ The always-`None` group is pinned on purpose. `TextArea` and `CodeEditor`
return `None` even when a signal IS bound (their internals store it privately),
and the `ValueSignalMixin` widgets return `None` only while unbound. Both are
correct to annotate `| None`, and a later "consistency" sweep that widens #460
over them would be a defect, not a cleanup.
"""
from __future__ import annotations

import inspect

import pytest

import bootstack as bs

# Widgets whose `.signal` is ALWAYS live: the internal manufactures one on first
# read, so there is no unbound state in which the property yields `None`.
ALWAYS_LIVE = [
    ("TextField", lambda **kw: bs.TextField(**kw), "textsignal", "seed"),
    ("PasswordField", lambda **kw: bs.PasswordField(**kw), "textsignal", "seed"),
    ("PathField", lambda **kw: bs.PathField(**kw), "textsignal", "seed"),
    ("SpinnerField", lambda **kw: bs.SpinnerField(**kw), "textsignal", "seed"),
    ("Checkbox", lambda **kw: bs.Checkbox("c", **kw), "signal", True),
    ("Switch", lambda **kw: bs.Switch("s", **kw), "signal", True),
    ("ToggleButton", lambda **kw: bs.ToggleButton("t", **kw), "signal", True),
]

# Widgets whose `.signal` is `None` until something is bound — correctly
# annotated `| None`, and NOT part of #460's sweep.
NONE_WHEN_UNBOUND = [
    ("TextArea", lambda **kw: bs.TextArea(**kw)),
    ("CodeEditor", lambda **kw: bs.CodeEditor(**kw)),
    ("NumberField", lambda **kw: bs.NumberField(**kw)),
    ("DateField", lambda **kw: bs.DateField(**kw)),
    ("TimeField", lambda **kw: bs.TimeField(**kw)),
    ("Select", lambda **kw: bs.Select(options=["a", "b"], **kw)),
    ("SelectButton", lambda **kw: bs.SelectButton(options=["a", "b"], **kw)),
]


def _signal_property(obj) -> property:
    """The `signal` property actually in effect for `obj`, walking the MRO."""
    for base in type(obj).__mro__:
        found = base.__dict__.get("signal")
        if isinstance(found, property):
            return found
    raise AssertionError("%s exposes no `signal` property" % type(obj).__name__)


@pytest.mark.parametrize("name,factory,_kw,_seed", ALWAYS_LIVE, ids=[c[0] for c in ALWAYS_LIVE])
def test_an_unbound_signal_property_still_hands_back_a_signal(app, name, factory, _kw, _seed):
    got = factory().signal

    assert got is not None, "%s.signal returned None with nothing bound" % name
    assert hasattr(got, "subscribe"), "%s.signal returned %r, not a Signal" % (name, got)


@pytest.mark.parametrize("name,factory,kw,seed", ALWAYS_LIVE, ids=[c[0] for c in ALWAYS_LIVE])
def test_a_bound_signal_property_hands_back_that_exact_signal(app, name, factory, kw, seed):
    # Identity, not truthiness. An `is not None` assertion passes just as well
    # when the delegation points at the wrong attribute and manufactures a
    # second, unrelated signal — which is the one way this fix could break.
    sig = bs.Signal(seed)

    got = factory(**{kw: sig}).signal

    assert got is sig, "%s.signal returned %r, not the bound signal" % (name, got)


@pytest.mark.parametrize("name,factory", NONE_WHEN_UNBOUND, ids=[c[0] for c in NONE_WHEN_UNBOUND])
def test_the_widgets_outside_the_sweep_still_report_none_when_unbound(app, name, factory):
    assert factory().signal is None, (
        "%s.signal is no longer None when unbound — it is annotated `| None` on "
        "purpose and is not part of #460's sweep" % name
    )


def test_no_public_signal_property_promises_a_none_it_cannot_produce(app):
    """The completeness check, by construction rather than by grep.

    Reads every widget's declared return annotation and compares it against what
    the property actually yields with nothing bound. This is the assertion that
    fails at the pre-fix commit — seven times.
    """
    offenders = []
    for name, factory, _kw, _seed in ALWAYS_LIVE:
        widget = factory()
        annotation = inspect.signature(_signal_property(widget).fget).return_annotation
        if "None" in str(annotation):
            offenders.append("%s (-> %s, but never returns None)" % (name, annotation))

    assert not offenders, "public `signal` properties promising an unreachable None: %s" % (
        ", ".join(offenders),
    )


def test_the_none_returning_properties_still_declare_their_none(app):
    """The mirror of the test above, so the sweep cannot overshoot.

    A pass that stripped `| None` from every `signal` property would satisfy the
    completeness check and silently mis-annotate seven other widgets.
    """
    missing = []
    for name, factory in NONE_WHEN_UNBOUND:
        widget = factory()
        annotation = inspect.signature(_signal_property(widget).fget).return_annotation
        if "None" not in str(annotation):
            missing.append("%s (-> %s, but returns None when unbound)" % (name, annotation))

    assert not missing, "properties that return None without declaring it: %s" % (", ".join(missing),)
