"""`localize=` on the group / composite selection widgets.

Covers the group-level switch, per-item override (via `add()` and the option
data bag), and SelectButton's face/value decoupling — across RadioGroup,
ToggleGroup, ButtonGroup, Radio, RadioToggleButton, and SelectButton.
"""
import pytest

import bootstack as bs
from bootstack.i18n import add_translations


@pytest.fixture(scope="module")
def app():
    """A single shown App in the Spanish locale with a small catalog."""
    a = bs.App(locale="es")
    a.__enter__()
    root = a._tk_root
    root.deiconify()
    root.update_idletasks()
    add_translations("es", {"Save": "Guardar", "Cancel": "Cancelar", "Choices": "Opciones"})
    a.locale = "es"  # re-activate so the freshly-registered catalog is current
    root.update()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


pytestmark = pytest.mark.gui


# --------------------------------------------------------------------------
# RadioGroup
# --------------------------------------------------------------------------

def test_radiogroup_auto_translates_items_and_title(app):
    rg = bs.RadioGroup(["Save", "Cancel"], title="Choices")
    assert rg._internal.item("Save").cget("text") == "Guardar"
    assert rg._internal._label.cget("text") == "Opciones"


def test_radiogroup_group_localize_false(app):
    rg = bs.RadioGroup(["Save", "Cancel"], title="Choices", localize=False)
    assert rg._internal.item("Save").cget("text") == "Save"
    assert rg._internal._label.cget("text") == "Choices"


def test_radiogroup_per_item_override_from_databag(app):
    rg = bs.RadioGroup([{"text": "Save", "localize": False}, "Cancel"])
    assert rg._internal.item("Save").cget("text") == "Save"
    assert rg._internal.item("Cancel").cget("text") == "Cancelar"


def test_radiogroup_add_localize_override(app):
    rg = bs.RadioGroup()
    rg.add("Save", localize=False)
    rg.add("Cancel")
    assert rg._internal.item("Save").cget("text") == "Save"
    assert rg._internal.item("Cancel").cget("text") == "Cancelar"


def test_radiogroup_databag_carries_localize(app):
    rg = bs.RadioGroup([{"text": "Save", "value": "s", "localize": False}])
    rg.value = "s"
    assert rg.selection["localize"] is False


# --------------------------------------------------------------------------
# ToggleGroup
# --------------------------------------------------------------------------

def test_togglegroup_auto_and_group_off(app):
    tg = bs.ToggleGroup(["Save", "Cancel"])
    assert tg._internal.item("Save").cget("text") == "Guardar"
    tg_off = bs.ToggleGroup(["Save", "Cancel"], localize=False)
    assert tg_off._internal.item("Save").cget("text") == "Save"


def test_togglegroup_add_override(app):
    tg = bs.ToggleGroup()
    tg.add("Save", localize=False)
    tg.add("Cancel")
    assert tg._internal.item("Save").cget("text") == "Save"
    assert tg._internal.item("Cancel").cget("text") == "Cancelar"


# --------------------------------------------------------------------------
# ButtonGroup
# --------------------------------------------------------------------------

def test_buttongroup_group_and_item(app):
    bg = bs.ButtonGroup()
    k_auto = bg.add("Save")
    k_off = bg.add("Cancel", localize=False)
    assert bg._internal.item(k_auto).cget("text") == "Guardar"
    assert bg._internal.item(k_off).cget("text") == "Cancel"

    bg_off = bs.ButtonGroup(localize=False)
    k = bg_off.add("Save")
    assert bg_off._internal.item(k).cget("text") == "Save"


# --------------------------------------------------------------------------
# Radio / RadioToggleButton
# --------------------------------------------------------------------------

def test_radio_localize(app):
    assert bs.Radio("Save", "s")._internal.cget("text") == "Guardar"
    assert bs.Radio("Save", "s", localize=False)._internal.cget("text") == "Save"


def test_radio_toggle_button_localize(app):
    assert bs.RadioToggleButton("Cancel", "c")._internal.cget("text") == "Cancelar"
    assert bs.RadioToggleButton("Cancel", "c", localize=False)._internal.cget("text") == "Cancel"


# --------------------------------------------------------------------------
# SelectButton — face translates, value stays in value-space
# --------------------------------------------------------------------------

def test_selectbutton_face_translates_value_raw(app):
    sb = bs.SelectButton(["Save", "Cancel"], value="Save")
    assert sb.text == "Guardar"
    assert sb.value == "Save"
    sb.value = "Cancel"
    assert sb.text == "Cancelar"
    assert sb.value == "Cancel"


def test_selectbutton_localize_false(app):
    sb = bs.SelectButton(["Save", "Cancel"], value="Save", localize=False)
    assert sb.text == "Save"
    assert sb.value == "Save"


def test_selectbutton_decoupled_value(app):
    sb = bs.SelectButton([("Save", "s"), ("Cancel", "c")], value="s")
    assert sb.text == "Guardar"
    assert sb.value == "s"


def test_selectbutton_live_locale_change(app):
    sb = bs.SelectButton(["Save", "Cancel"], value="Save", localize=False)
    sb_on = bs.SelectButton(["Save", "Cancel"], value="Save")
    app.locale = "en"
    app._tk_root.update()
    assert sb_on.text == "Save"  # no translation registered for en
    app.locale = "es"
    app._tk_root.update()
    assert sb_on.text == "Guardar"
    assert sb.text == "Save"  # localize=False stays raw across changes


# --------------------------------------------------------------------------
# Select (editable combobox) — entry face translates, value stays value-space
# --------------------------------------------------------------------------

def test_select_plain_face_translates_value_raw(app):
    s = bs.Select(["Save", "Cancel"], value="Save")
    assert s.text == "Guardar"
    assert s.value == "Save"
    assert s.selection == {"text": "Save", "value": "Save"}
    assert s.selected_index == 0
    s.value = "Cancel"
    assert s.text == "Cancelar"
    assert s.value == "Cancel"


def test_select_localize_false(app):
    s = bs.Select(["Save", "Cancel"], value="Save", localize=False)
    assert s.text == "Save"
    assert s.value == "Save"


def test_select_decoupled_value(app):
    s = bs.Select([("Save", "s"), ("Cancel", "c")], value="s")
    assert s.text == "Guardar"
    assert s.value == "s"
    assert s.selection == {"text": "Save", "value": "s"}


def test_select_per_item_override(app):
    s = bs.Select([{"text": "GitHub", "value": "gh", "localize": False}, "Save"], value="gh")
    assert s.text == "GitHub"
    assert s.value == "gh"
    s.value = "Save"
    assert s.text == "Guardar"


def test_select_custom_value(app):
    s = bs.Select(["Save"], allow_custom_values=True)
    s.value = "anything"
    assert s.text == "anything"
    assert s.value == "anything"


def test_select_popup_rows_translate_and_search(app):
    s = bs.Select(["Save", "Cancel"], value="Save", searchable=True)
    app._tk_root.update()
    sb = s._internal
    sb._show_selection_options()
    app._tk_root.update()
    assert [b.cget("text") for b in sb._item_labels] == ["Guardar", "Cancelar"]
    # search matches the displayed (translated) labels
    sb.entry_widget.delete(0, "end")
    sb.entry_widget.insert(0, "guar")
    sb._apply_search_filter(sb._popup_state)
    app._tk_root.update()
    visible = [b.cget("text") for b in sb._item_labels if b.winfo_manager()]
    assert visible == ["Guardar"]


def test_select_live_locale_change(app):
    s = bs.Select(["Save", "Cancel"], value="Save")
    app.locale = "en"
    app._tk_root.update()
    assert s.text == "Save"  # no en translation
    assert s.value == "Save"
    app.locale = "es"
    app._tk_root.update()
    assert s.text == "Guardar"
    assert s.value == "Save"
