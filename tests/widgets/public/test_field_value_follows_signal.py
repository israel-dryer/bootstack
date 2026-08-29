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
