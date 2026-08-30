"""#482 -- a field's `value` must follow a programmatic signal write.

The four TextEntryPart-backed fields reported the PREVIOUS value until something
committed the field, while the entry showed the new text. `TextArea`/`CodeEditor`
and the value-space fields already followed and are controls here.
"""
import pytest

import bootstack as bs

LAGGED = ["TextField", "PasswordField", "PathField", "SpinnerField"]
ALREADY_FOLLOWED = ["TextArea", "CodeEditor"]


def _build(shown_app, name, sig):
    return getattr(bs, name)(textsignal=sig)


@pytest.mark.parametrize("name", LAGGED + ALREADY_FOLLOWED)
def test_value_follows_a_programmatic_signal_write(shown_app, name):
    sig = bs.Signal("hello")
    widget = _build(shown_app, name, sig)

    sig.set("world")
    shown_app.tk.winfo_toplevel().update()

    assert widget.value == "world"


@pytest.mark.parametrize("name", LAGGED)
def test_a_second_write_is_followed_too(shown_app, name):
    # The first write could pass by committing the seed. Drive it twice so the
    # test cannot be satisfied by construction alone.
    sig = bs.Signal("one")
    widget = _build(shown_app, name, sig)
    root = shown_app.tk.winfo_toplevel()

    sig.set("two")
    root.update()
    assert widget.value == "two"

    sig.set("three")
    root.update()
    assert widget.value == "three"


def test_typing_is_still_uncommitted_until_blur(shown_app):
    # The contract this fix must NOT break: `value` is the committed value, so it
    # does not follow keystrokes. Only a write the user did not type commits.
    sig = bs.Signal("a")
    field = bs.TextField(textsignal=sig)
    entry = field._internal._entry
    root = shown_app.tk.winfo_toplevel()
    entry.focus_force()
    root.update()

    entry.delete(0, "end")
    entry.insert("end", "typed")
    root.update()

    assert entry.get() == "typed"
    assert field.value == "a"

    entry.event_generate("<FocusOut>")
    root.update()
    assert field.value == "typed"


def test_a_programmatic_write_still_emits_exactly_what_it_did_before(shown_app):
    # The family disagrees about whether a programmatic set is a change, and the
    # standing disposition is to leave that alone. This fix moves `value`, not
    # events: three writes must still be three <<Input>> and zero <<Change>>.
    sig = bs.Signal("a")
    field = bs.TextField(textsignal=sig)
    inputs, changes = [], []
    field.on_input(lambda e: inputs.append(e))
    field.on_change(lambda e: changes.append(e))
    root = shown_app.tk.winfo_toplevel()
    root.update()

    for value in ("b", "c", "d"):
        sig.set(value)
        root.update()

    assert len(inputs) == 3
    assert changes == []


def test_a_write_onto_a_placeholdered_field_is_committed(shown_app):
    sig = bs.Signal("")
    field = bs.TextField(textsignal=sig, placeholder="Type here")
    root = shown_app.tk.winfo_toplevel()
    root.update()

    sig.set("written by code")
    root.update()

    assert field.value == "written by code"
    assert field._internal._entry.get() == "written by code"


@pytest.mark.parametrize("name", ["TextField", "SpinnerField"])
def test_a_formatted_write_leaves_the_display_and_the_signal_alone(shown_app, name):
    # Round 1. Re-deriving the value must not normalize the display: this runs
    # inside the variable's own write trace, where Tcl suppresses the entry's
    # trace, so a write here moved the signal while the entry kept its old text
    # -- and the later blur then found nothing left to normalize, making the
    # divergence permanent. Normalizing belongs on commit, at blur/Return.
    sig = bs.Signal("1")
    widget = getattr(bs, name)(textsignal=sig, value_format="#,##0.00")
    entry = widget._internal._entry
    root = shown_app.tk.winfo_toplevel()
    root.update()

    sig.set("1234.5")
    root.update()

    assert widget.value == 1234.5
    assert sig() == "1234.5"
    assert entry.get() == "1234.5"

    entry.focus_force()
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()

    assert entry.get() == "1,234.50"
    assert sig() == "1,234.50"


def test_a_number_field_is_untouched_by_the_fix(shown_app):
    # Round 1. `NumberEntryPart` subclasses `TextEntryPart`, so it inherits the
    # helper even though `NumberField` already followed and is out of scope.
    # Its bounds are applied by its `commit()` override at blur, not before --
    # pinned so the helper cannot start reaching them and leave `value` clamped
    # while the display shows the number the caller wrote.
    field = bs.NumberField(value=5, min_value=0, max_value=10, value_format="#,##0.00")
    entry = field._internal._entry
    root = shown_app.tk.winfo_toplevel()
    root.update()

    field.value = 99
    root.update()

    assert field.value == 99.0
    assert entry.get() == "99.00"

    entry.focus_force()
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()

    assert field.value == 10
    assert entry.get() == "10.00"


def _focus_cycle(entry, root):
    # Synthesized rather than driven through `focus_force()`: this exercises the
    # same two bindings -- `_store_prev_value` on FocusIn, `_handle_focus_out` on
    # FocusOut -- without depending on a window manager to grant focus, where a
    # silent no-op would leave the snapshot at its construction value and fail
    # these tests for a reason that is not the product.
    entry.event_generate("<FocusIn>")
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()


def test_the_deferred_change_on_a_later_focus_cycle_moves_with_value(shown_app):
    # Round 2. `_prev_changed_value` is snapshotted from `_value` on FocusIn and
    # compared on blur, so a `_value` that already followed the write changes what
    # the NEXT cycle reports. On `main` that cycle carried the write's <<Change>>,
    # late and attributed to a focus the user made rather than to the write. It no
    # longer does. Pinned so the CHANGELOG's account of it cannot drift.
    root = shown_app.tk.winfo_toplevel()
    sig = bs.Signal("hello")
    field = bs.TextField(textsignal=sig)
    changes = []
    field.on_change(lambda e: changes.append((e.prev_value, e.value)))
    root.update()

    sig.set("world")
    root.update()
    # Precondition: the write took the unfocused branch. Without this the cycle
    # below proves nothing -- it would be silent for a field that never followed.
    assert field.value == "world"
    assert changes == []

    _focus_cycle(field._internal._entry, root)

    assert changes == []


def test_typing_the_pre_write_text_back_is_now_a_change(shown_app):
    # Round 2, the mirror of the above and the direction that GAINS an event:
    # <<Change>> now compares against the value the field actually holds, so
    # returning the field to what it showed before the write is a real change.
    # `main` was silent here, having compared against the same stale value twice.
    root = shown_app.tk.winfo_toplevel()
    sig = bs.Signal("hello")
    field = bs.TextField(textsignal=sig)
    changes = []
    field.on_change(lambda e: changes.append((e.prev_value, e.value)))
    entry = field._internal._entry
    root.update()

    sig.set("world")
    root.update()
    assert field.value == "world"

    entry.event_generate("<FocusIn>")
    root.update()
    entry.delete(0, "end")
    entry.insert("end", "hello")
    root.update()
    entry.event_generate("<FocusOut>")
    root.update()

    assert changes == [("world", "hello")]


def test_value_follows_a_clear_of_the_bound_signal(shown_app):
    # Round 2. `clear()` reaches the field down the same path as `set()` --
    # `Signal.clear` is `set(None)`, which a realized text signal takes as ''.
    # The field must read as empty rather than holding the value it was told had
    # been cleared, which is what 0.4.0 shipped `clear()` for.
    root = shown_app.tk.winfo_toplevel()
    sig = bs.Signal("hello", allow_empty=True)
    field = bs.TextField(textsignal=sig)
    root.update()

    sig.clear()
    root.update()

    assert sig() == ""
    assert field._internal._entry.get() == ""
    assert field.value is None
