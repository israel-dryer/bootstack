"""#472 -- an unrecognised keyword name is rejected at the seam, not discarded."""
import pytest

import bootstack as bs
from bootstack.signals import Signal

BOGUS = "bogus_xyz_383"

# A sample, not the population -- `development/probe_383_unknown_kwarg_policy.py`
# classifies all 50 by construction.
STRICT = ["TextField", "Label", "Button", "Select", "DataTable", "Row", "Grid",
          "Slider", "Tabs", "Form", "Calendar", "Tree"]

FORWARDERS = ["Chart", "MenuButton", "Picture", "StatusBar", "Toolbar"]

# Without the dep the widget raises before reaching the split, so the assertion
# below would pass without testing forwarding.
OPTIONAL_DEP = {"Chart": "matplotlib"}


@pytest.mark.parametrize("name", STRICT)
def test_unknown_keyword_is_rejected_and_named(app, name):
    with pytest.raises(TypeError) as exc:
        getattr(bs, name)(**{BOGUS: 1})
    assert name in str(exc.value)
    assert BOGUS in str(exc.value)


def test_a_typo_of_a_layout_key_is_rejected_too(app):
    """A typo of a layout key is not a layout key -- the split does not claim it."""
    with pytest.raises(TypeError) as exc:
        bs.Label("hi", filll="x")
    assert "filll" in str(exc.value)


def test_a_real_layout_key_still_passes_through(app):
    """Flex-child placement kwargs must still pass through."""
    row = bs.Row()
    lbl = bs.Label("hi", parent=row, grow=True, horizontal="stretch")
    assert lbl.text == "hi"


def test_legacy_child_kwargs_keep_their_own_message(app):
    """`side=` is a PACK key, so it keeps its migration message, not the generic one."""
    with pytest.raises(Exception) as exc:
        with bs.Row():
            bs.Label("hi", side="left")
    assert "unexpected keyword" not in str(exc.value)


@pytest.mark.parametrize("name", FORWARDERS)
def test_declared_forwarders_still_forward(app, name):
    """A forwarder still rejects, but via its internal -- not with the seam's message."""
    if name in OPTIONAL_DEP:
        pytest.importorskip(OPTIONAL_DEP[name])
    with pytest.raises(Exception) as exc:
        getattr(bs, name)(**{BOGUS: 1})
    assert "got unexpected keyword argument" not in str(exc.value)


def test_declared_forwarders_are_exactly_the_five(app):
    """A sixth opt-out should be a decision, not a drift."""
    declared = {n for n in dir(bs)
                if isinstance(getattr(bs, n, None), type)
                and getattr(getattr(bs, n), "_forwards_kwargs", False)}
    assert declared == set(FORWARDERS), (
        "the #383 opt-out list changed: %s" % sorted(declared))


# The four bespoke `textsignal=` messages a strict split would otherwise retire.

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
    assert "got unexpected keyword argument" not in msg
