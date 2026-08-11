"""The flex-child migration error must recommend kwargs that actually exist.

A legacy `fill=`/`expand=`/`anchor=`/`sticky=`/`side=` on a `Row`/`Column`/`Grid`
child raises a migration error pointing at the replacement. The error fired
correctly but named `align_self=` and `justify_self=`, which were the
design-stage names and never shipped — so a user who followed the advice
verbatim landed on a raw `TclError` naming a Tk option they never wrote
(issue #426).

The regression guarded here is the PROPERTY rather than the wording: every
`name=` the message recommends must be a real per-child layout key. That keeps
the test meaningful if the message is reworded, and makes it impossible to
reintroduce a remedy that does not exist.
"""
from __future__ import annotations

import re

import pytest

from bootstack.errors import BootstackError
from bootstack.widgets._core.container import (
    FLEX_CHILD_KEYS, _LEGACY_CHILD_KEYS, _reject_legacy_child_kwargs,
)


def _message_for(**layout_kw: object) -> str:
    with pytest.raises(BootstackError) as excinfo:
        _reject_legacy_child_kwargs(dict(layout_kw), where="Picture")
    return str(excinfo.value)


def test_every_kwarg_the_message_recommends_is_a_real_flex_child_key():
    """The invariant. A remedy the engine does not accept is worse than none."""
    message = _message_for(fill="x")

    recommended = {name for name in re.findall(r"\b([a-z_]+)=", message)}
    assert recommended, "the message must name at least one replacement kwarg"

    unreal = recommended - FLEX_CHILD_KEYS
    assert not unreal, (
        f"the migration error recommends {sorted(unreal)}, which "
        f"Row/Column/Grid do not accept; valid keys are {sorted(FLEX_CHILD_KEYS)}"
    )


def test_the_design_stage_names_are_gone():
    """`align_self`/`justify_self` were renamed before release and never shipped."""
    message = _message_for(fill="x")
    assert "align_self" not in message
    assert "justify_self" not in message


def test_the_message_points_at_both_the_grow_and_the_cross_axis_remedy():
    """A stretched child needs the cross-axis key; `grow=` alone will not do it.

    This is the case that sent the reporter to the error in the first place - a
    `Picture` with `grow=1` stayed one pixel wide on the cross axis.
    """
    message = _message_for(fill="x")
    assert "grow=" in message
    assert "horizontal=" in message
    assert "vertical=" in message


def test_the_message_names_the_offending_kwarg_and_the_call_site():
    message = _message_for(fill="x")
    assert "fill" in message
    assert "Picture" in message


@pytest.mark.parametrize("legacy", sorted(_LEGACY_CHILD_KEYS))
def test_every_legacy_key_still_raises(legacy):
    """The guard itself must keep firing - the fix was to the wording only."""
    message = _message_for(**{legacy: "x"})
    assert legacy in message


def test_a_valid_flex_child_key_does_not_raise():
    """Control: the guard rejects only the legacy set, not everything."""
    _reject_legacy_child_kwargs({"grow": 1, "horizontal": "stretch"}, where="Picture")
