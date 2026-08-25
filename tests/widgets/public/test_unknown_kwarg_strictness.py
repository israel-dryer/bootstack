"""#383 gap 3 -- an unrecognised keyword name is rejected, not discarded.

`bs.TextField(bogus_xyz=1)` used to construct silently while the internal it
wraps raised `TclError: unknown option "-bogus_xyz"`, so the public layer was
the LESS strict of the two. A typo'd real parameter (`densty="compact"`) and a
typo'd layout key (`filll="x"`) both vanished the same way.

The guard lives at the shared seam, `PublicWidgetBase._split_layout_kwargs`, so
it is default-strict: a wrapper written tomorrow is strict for free. Five
wrappers forward leftovers to their internal on purpose and opt out with a
declarative class flag -- see `test_declared_forwarders_are_exactly_the_five`,
which exists so the exemption list cannot grow unnoticed.
"""
import pytest

import bootstack as bs
from bootstack.signals import Signal

BOGUS = "bogus_xyz_383"

# One per construction shape, not all 40 -- the seam is shared, so the value of
# a 40-row parametrize is in the probe, not here.
# `development/probe_383_unknown_kwarg_policy.py` classifies all 52 by
# construction and is the instrument for the whole population.
STRICT = ["TextField", "Label", "Button", "Select", "DataTable", "Row", "Grid",
          "Slider", "Tabs", "Form", "Calendar", "Tree"]

FORWARDERS = ["Chart", "MenuButton", "Picture", "StatusBar", "Toolbar"]


@pytest.mark.parametrize("name", STRICT)
def test_unknown_keyword_is_rejected_and_named(app, name):
    with pytest.raises(TypeError) as exc:
        getattr(bs, name)(**{BOGUS: 1})
    # Naming the widget AND the key is the whole point: an error that says
    # neither is no more useful than the silent drop it replaces.
    assert name in str(exc.value)
    assert BOGUS in str(exc.value)


def test_a_typo_of_a_layout_key_is_rejected_too(app):
    """`filll="x"` is not a layout key, so it falls through the split and is
    caught here. This is the half a per-widget parameter check would miss."""
    with pytest.raises(TypeError) as exc:
        bs.Label("hi", filll="x")
    assert "filll" in str(exc.value)


def test_a_real_layout_key_still_passes_through(app):
    """The guard must not eat legitimate placement kwargs -- they are popped
    into `layout_kw` before it looks, so this is the non-over-rejection case.

    Note these are the FLEX-CHILD spellings. `fill=`/`expand=` are legacy and
    are rejected on purpose with their own message, which is the next test.
    """
    row = bs.Row()
    lbl = bs.Label("hi", parent=row, grow=True, horizontal="stretch")
    assert lbl.text == "hi"


def test_legacy_child_kwargs_keep_their_own_message(app):
    """#383 section 3: `side=` is IN `PACK_KEYS`, so the split pops it and
    `_reject_legacy_child_kwargs` reports it with the flex-vs-grid advice. The
    new guard must not shadow that with a generic 'unexpected keyword'."""
    with pytest.raises(Exception) as exc:
        with bs.Row():
            bs.Label("hi", side="left")
    assert "unexpected keyword" not in str(exc.value)


@pytest.mark.parametrize("name", FORWARDERS)
def test_declared_forwarders_still_forward(app, name):
    """These hand leftovers to their internal deliberately. They still reject a
    bogus name -- the internal does it -- but NOT with the seam's message, which
    is what distinguishes forwarding from the guard firing."""
    with pytest.raises(Exception) as exc:
        getattr(bs, name)(**{BOGUS: 1})
    assert "got unexpected keyword argument" not in str(exc.value)


def test_declared_forwarders_are_exactly_the_five(app):
    """The opt-out is a class flag precisely so it can be enumerated. If a
    sixth widget ever sets it, that is a decision and this test makes it one."""
    declared = {n for n in dir(bs)
                if isinstance(getattr(bs, n, None), type)
                and getattr(getattr(bs, n), "_forwards_kwargs", False)}
    assert declared == set(FORWARDERS), (
        "the #383 opt-out list changed: %s" % sorted(declared))


# -- section 2: the four crafted messages the seam guard would have killed ----
#
# Select, DateField, NumberField and TimeField each raise a bespoke TypeError
# for `textsignal=`, and each ran the split FIRST. Making the split strict would
# have fired the generic error before the specific one ever ran, silently
# retiring four crafted messages -- including #458's public explanation of a
# deliberate behaviour change. Each check was moved above its split.

@pytest.mark.parametrize("name, phrase", [
    ("Select", "a select binds the"),
    ("DateField", "a date field binds"),
    ("NumberField", "a number field binds"),
    ("TimeField", "a time field binds"),
])
def test_textsignal_keeps_its_crafted_message(app, name, phrase):
    with pytest.raises(TypeError) as exc:
        getattr(bs, name)(textsignal=Signal("x"))
    msg = str(exc.value)
    assert phrase in msg, msg
    # the generic guard must NOT be what fired
    assert "got unexpected keyword argument" not in msg
