"""#465 — Select exposes the field family's validation surface.

Reported externally against 0.3.2: a Select accepted `add_validation_rule()`
and ran it, but exposed no way to read the outcome, so a caller could attach a
rule, watch it fail, and have nowhere to read the message from.

The cause was not a missing property. `Select` did not inherit
`FieldAddonMixin` — nothing recorded a decision to exclude it, the family was
uniform 7/7 with it, and `Select` already used the mixin's addon machinery
internally (its dropdown arrow IS an addon). It hand-copied one method out of
that mixin in #357 and left the rest behind.

So these tests pin the whole surface the inheritance restores, not just the two
members the report named:

  .valid / .error       Signals, and the SAME objects the entry updates
  on_valid / on_invalid / on_validate   the family's event shorthands
  insert_addon / update_addon / remove_addon / addons

⚠ Each test must be able to FAIL while the member exists. A `hasattr` check
passes the moment the property is defined and says nothing about whether it
reports the truth — that is the vacuity shape #458's round 1 shipped.
"""
import pytest
import bootstack as bs


def _select(app):
    """A Select with a rule that fails when nothing is selected."""
    sel = bs.Select([("One", "1"), ("Two", "2")], value="1")
    sel.add_validation_rule("required")
    app._tk_root.update_idletasks()
    return sel


# ── .valid / .error ───────────────────────────────────────────────────────────

def test_select_starts_valid_with_no_message(app):
    sel = _select(app)
    assert sel.valid() is True
    assert sel.error() == ""


def test_select_error_carries_the_message_after_a_failing_rule(app):
    sel = _select(app)
    sel.value = None
    assert sel.validate() is False
    assert sel.valid() is False
    assert sel.error() != ""


def test_select_valid_recovers_when_the_value_becomes_good(app):
    """Both directions. A snapshot that only ever goes False would pass a
    one-way test while being useless to bind to."""
    sel = _select(app)
    sel.value = None
    sel.validate()
    assert sel.valid() is False

    sel.value = "2"
    assert sel.validate() is True
    assert sel.valid() is True
    assert sel.error() == ""


def test_select_signals_are_the_entry_s_own_objects(app):
    """The one test that catches a 'fix' returning a fresh detached Signal —
    that would read True forever and satisfy every behavioural test above only
    by accident of ordering."""
    sel = _select(app)
    assert sel.valid is sel._internal._entry._valid_signal
    assert sel.error is sel._internal._entry._error_signal


def test_select_error_binds_to_a_label(app):
    """The reporter's actual use case: surface the message somewhere."""
    sel = _select(app)
    label = bs.Label(textsignal=sel.error)

    sel.value = None
    sel.validate()
    assert label.text == sel.error()
    assert label.text != ""

    sel.value = "1"
    sel.validate()
    assert label.text == ""


def test_select_error_notifies_subscribers(app):
    sel = _select(app)
    seen = []
    sel.error.subscribe(seen.append)

    sel.value = None
    sel.validate()
    assert seen and seen[-1] != ""


# ── events ────────────────────────────────────────────────────────────────────

def test_select_emits_valid_and_invalid(app):
    """These fired before #465 too — nothing was listening, because
    _SELECT_EVENTS carried only `change`."""
    sel = _select(app)
    fired = []
    sel.on_invalid(lambda e: fired.append(("invalid", e.message)))
    sel.on_valid(lambda e: fired.append(("valid", e.message)))

    sel.value = None
    sel.validate()
    sel.value = "1"
    sel.validate()

    kinds = [f[0] for f in fired]
    assert kinds == ["invalid", "valid"]
    assert fired[0][1] != ""


def test_select_on_validate_fires_for_both_outcomes(app):
    sel = _select(app)
    runs = []
    sel.on_validate(lambda e: runs.append(e.is_valid))

    sel.value = None
    sel.validate()
    sel.value = "1"
    sel.validate()

    assert runs == [False, True]


def test_select_validation_events_return_a_cancellable_subscription(app):
    sel = _select(app)
    fired = []
    sub = sel.on_invalid(fired.append)

    sel.value = None
    sel.validate()
    assert len(fired) == 1

    sub.cancel()
    sel.validate()
    assert len(fired) == 1


# ── addons ────────────────────────────────────────────────────────────────────

def test_select_takes_addons_alongside_its_dropdown(app):
    """`Select` already used this machinery — the dropdown arrow is an addon —
    so the risk here is the new public surface disturbing the built-in one."""
    sel = bs.Select([("A", "a")], value="a")
    app._tk_root.update_idletasks()
    assert "dropdown" in sel.addons

    sel.insert_addon("button", "before", name="search", icon="search")
    assert "search" in sel.addons
    assert "dropdown" in sel.addons

    sel.update_addon("search", icon="x-lg")
    sel.remove_addon("search")
    assert "search" not in sel.addons
    assert "dropdown" in sel.addons


def test_select_keeps_the_family_row_alignment_default(app):
    """#394 — Select carried its own copy of this until #465; it now comes from
    the mixin. If the inheritance is ever unwound, a Select sits low beside the
    fields it shares a Row with, which is a silent visual regression."""
    assert bs.Select._flex_vertical_default == bs.TextField._flex_vertical_default == "top"


# ── the hand-copy is gone ─────────────────────────────────────────────────────

def test_select_validation_comes_from_the_shared_mixin(app):
    """The defect was a partial hand-copy. Pin the inheritance itself, or the
    next narrow fix re-copies a subset and the family diverges again."""
    from bootstack.widgets._core.field_mixin import FieldAddonMixin

    assert issubclass(bs.Select, FieldAddonMixin)
    # add_validation_rule must be the mixin's, not a local re-definition
    assert "add_validation_rule" not in vars(bs.Select)


# ── the value kind is the OPTIONS', not the widget's (review round 1) ─────────
#
# Inheriting the mixin also brings `_VALIDATION_KIND`, and the mixin's default
# says "text". That is false for a Select: `SelectBox._validation_value` decodes
# the displayed label back to the option's value before a rule sees it, so a
# decoupled option list hands the rule the option's real Python object. A
# `range` rule over numeric or date option values works — it worked before #465
# and it has to keep working, or the fix breaks running apps at construction.
# Measured on both sides in development/probe_465_select_range_kind.py.

def test_select_range_rule_works_on_numeric_option_values(app):
    sel = bs.Select([("One", 1), ("Seven", 7), ("Twelve", 12)], value=7)
    app._tk_root.update_idletasks()
    sel.add_validation_rule("range", min=5, max=10)      # must not raise

    assert sel.validate() is True                        # 7 is in 5..10
    sel.value = 12
    assert sel.validate() is False                       # and 12 is not
    sel.value = 7
    assert sel.validate() is True


def test_select_range_rule_works_on_date_option_values(app):
    import datetime as dt

    jan, jun, dec = dt.date(2024, 1, 1), dt.date(2024, 6, 1), dt.date(2024, 12, 1)
    sel = bs.Select([("Jan", jan), ("Jun", jun), ("Dec", dec)], value=jun)
    app._tk_root.update_idletasks()
    sel.add_validation_rule("range", min=jan, max=dt.date(2024, 8, 1))

    assert sel.validate() is True
    sel.value = dec
    assert sel.validate() is False


def test_select_does_not_gate_rules_by_value_kind(app):
    """`None` is the whole opt-out, and it must stay local to Select — a fix
    that dropped the gate on the mixin instead would satisfy the two tests
    above and quietly un-gate the seven fields that DO have a fixed kind."""
    assert bs.Select._VALIDATION_KIND is None
    for widget in (bs.TextField, bs.PasswordField, bs.PathField, bs.SpinnerField,
                   bs.NumberField, bs.DateField, bs.TimeField):
        assert widget._VALIDATION_KIND is not None, widget.__name__


# -- the rule-type guard came with the inheritance (review round 2) ----------


def test_select_rejects_a_non_string_rule_type(app):
    """The one thing about a `Select` a caller can observe changing.

    On `main` the hand-copied `add_validation_rule` forwarded anything at all,
    so passing a rule OBJECT instead of the rule-type string was accepted and
    the field then reported valid forever -- #465's own defect one level down.
    The mixin's guard came along with the inheritance and the CHANGELOG
    announces it, so it is pinned rather than left to a claim.
    """
    sel = bs.Select([("One", "1")], value="1")
    app._tk_root.update_idletasks()

    with pytest.raises(TypeError):
        sel.add_validation_rule(object())

    # ...and the guard must not have swallowed the working spelling with it
    sel.add_validation_rule("required")
    assert sel.validate() is True
