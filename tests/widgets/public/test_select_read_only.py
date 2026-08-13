"""#453 — `read_only` on `Select` is a real setting, not the entry's ttk state.

A `Select` is already untypeable by default; that is NOT read-only. Read-only
additionally closes the option list, from both entrances, and dims the dropdown
arrow to say so. It suppresses `allow_custom_values`/`searchable` rather than
discarding them, so clearing it restores whichever was asked for.

Every test here fails against the pre-fix source for a BEHAVIORAL reason, not
an `AttributeError` — `read_only` was accepted and ignored before, so nothing
raises either way.
"""
import bootstack as bs


def _popup_opens(sel) -> bool:
    """Drive the real popup entry point and report whether the list came up."""
    inner = sel._internal
    inner._popup_open = False
    inner._show_selection_options()
    opened = bool(inner._popup_open)
    if opened:
        try:
            inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
        except Exception:
            inner._popup_open = False
    return opened


def _click_opens(sel) -> bool:
    """Drive the entry-click entrance by generating the real `<Button-1>`.

    This is the path #453 reported: clicking the text area rather than the
    arrow. It is a separate entrance from `_popup_opens` and was the one that
    stayed live under `read_only=True`.

    It generates the event rather than calling the handler by name, so the test
    exercises whatever binding the widget actually installed — otherwise this
    would raise `AttributeError` against the unfixed source and prove nothing.
    Both the old and new bindings defer through `after_idle`, hence the update.
    """
    inner = sel._internal
    entry = sel._entry_widget()
    # Settle pending idle work FIRST. The unfixed source installed the click
    # binding from `after_idle`, so clicking before idle ran hit no binding at
    # all and this helper reported False — passing the read-only test for the
    # wrong reason and missing the very defect #453 reported.
    entry.update()
    inner._popup_open = False
    entry.event_generate("<Button-1>", x=5, y=5)
    entry.update()
    opened = bool(inner._popup_open)
    if opened:
        try:
            inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
        except Exception:
            inner._popup_open = False
    return opened


def _typeable(sel) -> bool:
    entry = sel._entry_widget()
    return not entry.instate(["readonly"]) and not entry.instate(["disabled"])


def _arrow_dimmed(sel) -> bool:
    return sel._internal._addons["dropdown"].instate(["disabled"])


# --------------------------------------------------------------------------
# The report: read_only must close both entrances
# --------------------------------------------------------------------------

def test_read_only_blocks_the_popup_from_the_arrow(app):
    sel = bs.Select(["A", "B", "C"], value="A", read_only=True, parent=app)
    assert _popup_opens(sel) is False


def test_read_only_blocks_the_popup_from_an_entry_click(app):
    # #453 as reported: the arrow looked inactive but clicking the text area
    # still opened the list and changed the value.
    sel = bs.Select(["A", "B", "C"], value="A", read_only=True, parent=app)
    assert _click_opens(sel) is False


def test_a_plain_select_still_opens_from_both_entrances(app):
    # The control. Read-only must close the list; being merely untypeable —
    # which every Select is by default — must not.
    sel = bs.Select(["A", "B", "C"], value="A", parent=app)
    assert _typeable(sel) is False
    assert _popup_opens(sel) is True
    assert _click_opens(sel) is True


# --------------------------------------------------------------------------
# The getter reports the setting, not the widget's internal state
# --------------------------------------------------------------------------

def test_a_plain_select_is_not_read_only(app):
    # Pre-fix this read True for every Select ever built, because the property
    # read the ttk state the widget sets for its own "no free typing" reason.
    sel = bs.Select(["A", "B", "C"], parent=app)
    assert sel.read_only is False


def test_read_only_survives_being_combined_with_typing_modes(app):
    # Pre-fix, construction applied `state="readonly"` and the entry state was
    # then recomputed from the typing modes, discarding the request outright.
    for kwargs in ({"allow_custom_values": True}, {"searchable": True}):
        sel = bs.Select(["A", "B", "C"], read_only=True, parent=app, **kwargs)
        assert sel.read_only is True, kwargs
        assert _typeable(sel) is False, kwargs
        assert _popup_opens(sel) is False, kwargs


# --------------------------------------------------------------------------
# The dropdown arrow tracks read-only, not the entry's ttk state
# --------------------------------------------------------------------------

def test_the_arrow_is_lit_on_a_plain_select_even_after_a_state_sync(app):
    # `Field` dims every addon while the entry is `readonly`, and a Select is
    # `readonly` by default. The arrow survived only because construction never
    # fired <<StateChanged>>; the first sync dimmed it on an ordinary Select.
    sel = bs.Select(["A", "B", "C"], parent=app)
    sel._internal._entry.event_generate("<<StateChanged>>")
    sel._internal.update_idletasks()
    assert _arrow_dimmed(sel) is False


def test_the_arrow_is_dimmed_when_read_only(app):
    # Passes against the unfixed source too, and deliberately kept: dimming was
    # the ONE thing `read_only=True` did before, as an accident of routing
    # `state="readonly"` through Field's addon sync. It is the symptom the
    # reporter read as meaning read-only, so it is now pinned as intended.
    sel = bs.Select(["A", "B", "C"], read_only=True, parent=app)
    assert _arrow_dimmed(sel) is True


# --------------------------------------------------------------------------
# Runtime: read_only suppresses the typing modes, it does not overwrite them
# --------------------------------------------------------------------------

def test_clearing_read_only_restores_typing_when_custom_values_were_asked_for(app):
    # Passes against the unfixed source as well, but only by luck: writing
    # state="normal" happened to be the right answer when custom values were
    # on. The mirror test below is the one that caught it being wrong.
    sel = bs.Select(["A", "B", "C"], allow_custom_values=True, parent=app)
    sel.read_only = True
    assert _typeable(sel) is False
    sel.read_only = False
    # Restores what was asked for, rather than falling back to a plain select.
    assert _typeable(sel) is True
    assert sel.read_only is False


def test_clearing_read_only_does_not_grant_typing_to_a_plain_select(app):
    # The mirror case. Pre-fix the setter wrote state="normal" unconditionally,
    # silently turning a plain Select into a free-text field.
    sel = bs.Select(["A", "B", "C"], parent=app)
    sel.read_only = True
    sel.read_only = False
    assert _typeable(sel) is False
    assert _popup_opens(sel) is True


def test_read_only_survives_a_disabled_round_trip(app):
    # Clearing `disabled` sends state="normal", which cleared read-only too.
    sel = bs.Select(["A", "B", "C"], read_only=True, parent=app)
    sel.disabled = True
    sel.disabled = False
    assert sel.read_only is True
    assert _popup_opens(sel) is False


def test_the_list_keeps_exactly_one_entrance_across_a_runtime_mode_flip(app):
    # Click-to-open is bound for the widget's whole life and gated in the
    # handler, so flipping back out of a typing mode restores the entrance.
    sel = bs.Select(["A", "B", "C"], parent=app)
    assert _click_opens(sel) is True

    sel._internal.configure(allow_custom_values=True)
    assert _typeable(sel) is True
    assert _click_opens(sel) is False   # a click must place a text cursor now
    assert _popup_opens(sel) is True    # ...so the arrow is the only way in

    sel._internal.configure(allow_custom_values=False)
    assert _typeable(sel) is False
    assert _click_opens(sel) is True


# --------------------------------------------------------------------------
# Reachability: a typeable entry must never be left with no way to the list
# --------------------------------------------------------------------------

def test_search_forces_the_dropdown_button_like_custom_values_does(app):
    # `show_dropdown_button=False` is honored only while the entry is not
    # typeable. It covered allow_custom_values but not enable_search, leaving
    # that combination with no entrance at all.
    from bootstack.widgets._impl.composites.selectbox import SelectBox

    box = SelectBox(
        app._child_master(),
        items=["A", "B"],
        enable_search=True,
        show_dropdown_button=False,
    )
    box.pack()
    assert "dropdown" in box._addons


def test_a_runtime_flip_does_not_build_a_button_that_was_refused(app):
    # The mirror of the test above, and the boundary between them: membership
    # is decided ONCE, at construction. Turning typing on later must not insert
    # a button the caller explicitly refused — the reachability rule buys its
    # exception at build time, where the caller can still see the trade.
    from bootstack.widgets._impl.composites.selectbox import SelectBox

    box = SelectBox(
        app._child_master(),
        items=["A", "B"],
        show_dropdown_button=False,
    )
    box.pack()
    assert "dropdown" not in box._addons

    box.configure(allow_custom_values=True)
    assert "dropdown" not in box._addons

    box.configure(enable_search=True)
    assert "dropdown" not in box._addons


# --------------------------------------------------------------------------
# TimeField: the same setting reached through a different public property
# --------------------------------------------------------------------------
# `TimeField` is the only field family member whose internal is a SelectBox,
# so it is the only one whose `read_only` had to stop writing the ttk state.
# The state is an OUTPUT of the interaction rules now and is re-derived on
# every change, so writing it was overwritten within the same call.

def test_timefield_read_only_is_not_discarded(app):
    tf = bs.TimeField(parent=app)
    tf.read_only = True
    assert tf.read_only is True
    assert tf._internal._entry.instate(["readonly"]) is True


def test_timefield_read_only_closes_the_list(app):
    # The point of the property: a locked field must not offer the time list.
    tf = bs.TimeField(parent=app)
    tf.read_only = True
    assert tf._internal._popup_allowed() is False


def test_timefield_clearing_read_only_restores_typing(app):
    # A TimeEntry is built with allow_custom_values=True, so clearing read-only
    # must give typing back rather than leaving a permanently locked field.
    #
    # Passes against the unfixed source too, and only because BOTH writes were
    # no-ops there — it pins the end state, not the transition. The three tests
    # around it are the ones that fail behaviorally pre-fix.
    tf = bs.TimeField(parent=app)
    tf.read_only = True
    tf.read_only = False
    assert tf.read_only is False
    assert tf._internal._entry.instate(["readonly"]) is False


def test_timefield_read_only_survives_a_disabled_round_trip(app):
    # Clearing `disabled` sends state="normal". Read-only is held as its own
    # flag now, so it is re-derived rather than cleared as a side effect.
    tf = bs.TimeField(parent=app)
    tf.read_only = True
    tf.disabled = True
    tf.disabled = False
    assert tf.disabled is False
    assert tf.read_only is True
