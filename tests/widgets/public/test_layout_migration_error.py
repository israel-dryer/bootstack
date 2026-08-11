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

⚠ "Real" is per CONTAINER, not global. Checking every message against
`FLEX_CHILD_KEYS` is too weak: `grow` is in that set, so a message recommending
`grow=` to a GRID cell passed this file while `Grid` silently dropped the
kwarg — the same silent no-op #426 exists to remove. A grid cell filters its
child options to `GRID_KEYS`, which has no `grow`, so it gets its own advice
string and is checked against `GRID_CHILD_KEYS`.
"""
from __future__ import annotations

import re

import pytest

from bootstack.errors import BootstackError
from bootstack.widgets._core.container import (
    FLEX_CHILD_KEYS, GRID_CHILD_KEYS, GRID_CHILD_ADVICE, _LEGACY_CHILD_KEYS,
    _reject_legacy_child_kwargs,
)


def _message_for(**layout_kw: object) -> str:
    with pytest.raises(BootstackError) as excinfo:
        _reject_legacy_child_kwargs(dict(layout_kw), where="Picture")
    return str(excinfo.value)


def _grid_message_for(**layout_kw: object) -> str:
    with pytest.raises(BootstackError) as excinfo:
        _reject_legacy_child_kwargs(
            dict(layout_kw), where="Grid", advice=GRID_CHILD_ADVICE
        )
    return str(excinfo.value)


def _recommended(message: str) -> set[str]:
    """The per-child kwargs a message tells the user to write.

    Container-level options are deliberately named without a trailing `=` in
    the message, so this picks up only the per-child remedies.
    """
    return set(re.findall(r"\b([a-z_]+)=", message))


def test_every_kwarg_the_message_recommends_is_a_real_flex_child_key():
    """The invariant. A remedy the engine does not accept is worse than none."""
    recommended = _recommended(_message_for(fill="x"))
    assert recommended, "the message must name at least one replacement kwarg"

    unreal = recommended - FLEX_CHILD_KEYS
    assert not unreal, (
        f"the migration error recommends {sorted(unreal)}, which "
        f"a flex container does not accept; valid keys are "
        f"{sorted(FLEX_CHILD_KEYS)}"
    )


def test_every_kwarg_the_grid_message_recommends_is_honored_by_a_grid_cell():
    """The same invariant for the other placement kind, where it differs.

    `grow=` is the specific trap: it is a real flex-child key, so a global
    check against `FLEX_CHILD_KEYS` accepts it, but a grid cell filters child
    options to `GRID_KEYS` and drops it without a word.
    """
    recommended = _recommended(_grid_message_for(fill="x"))
    assert recommended, "the message must name at least one replacement kwarg"

    unreal = recommended - GRID_CHILD_KEYS
    assert not unreal, (
        f"the grid-cell migration error recommends {sorted(unreal)}, which a "
        f"grid cell silently drops; valid keys are {sorted(GRID_CHILD_KEYS)}"
    )


def test_the_grid_message_does_not_recommend_grow():
    """The specific regression: `grow=` on a grid cell is a silent no-op."""
    assert "grow=" not in _grid_message_for(fill="x")


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


def test_a_grid_cell_really_drops_grow_but_honors_the_alignment_keys(app):
    """Why the grid message must differ - the behavior the wording rests on.

    Without this, the wording tests could drift back to recommending `grow=`
    and only a reader would notice. The flex arm is the control: the SAME
    kwarg on a `Column` is recorded, so the Grid result is about the container,
    not about the kwarg being rejected everywhere.
    """
    import bootstack as bs

    grid_child = bs.Label("x", parent=bs.Grid(columns=2, parent=app), grow=1)
    assert "grow" not in grid_child._placement.options, (
        "a Grid cell now honors grow=; if that is intended, GRID_CHILD_KEYS "
        "and the grid advice string should say so"
    )

    flex_child = bs.Label("y", parent=bs.Column(parent=app), grow=1)
    assert flex_child._placement.options.get("grow") == 1, (
        "control failed: grow= is not recorded on a flex child either, so the "
        "Grid assertion above proves nothing about Grid"
    )

    # The remedy the grid message actually names must have a visible effect.
    aligned = bs.Label(
        "z", parent=bs.Grid(columns=2, parent=app), horizontal="left", vertical="top"
    )
    assert aligned._placement.options["sticky"] == "wn"
