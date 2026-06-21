"""#242 — `.text` setter must write through a bound textsignal/textvariable.

When a `textsignal=` (or a localized key) owns a widget's text, ttk ignores the
`text` option, so a naive `.text` setter (`configure(text=...)`) silently no-ops.
The fix routes the setter through the bound variable when present (the Button
pattern), keeping the displayed text AND the bound signal in sync.

Only widgets whose `.text` IS the displayed text get the writable fix: Button
(reference) and Label/Badge. Widgets that SEPARATE a display string from a raw
value — Select/SelectButton (selected-option label vs `.value`) and the typed
fields (`'Jan 2, 2024'` vs a `date`) — keep `.text` read-only and derived; this
file guards that those stay live and untouched by the fix.
"""
import datetime

import pytest

import bootstack as bs


# ----- Label: the dead-setter bug (#242) -----

def test_label_text_round_trip_unbound(app):
    lbl = bs.Label("Plain")
    assert lbl.text == "Plain"
    lbl.text = "New"
    assert lbl.text == "New"


def test_label_text_round_trip_with_textsignal(app):
    sig = bs.Signal("Initial")
    lbl = bs.Label(textsignal=sig)
    assert lbl.text == "Initial"

    # Setter writes through the bound variable and keeps the signal in sync.
    lbl.text = "Changed"
    assert lbl.text == "Changed"
    assert sig() == "Changed"

    # Signal writes flow back to .text.
    sig.set("ViaSignal")
    assert lbl.text == "ViaSignal"


# ----- Badge inherits the fix from Label -----

def test_badge_text_round_trip_with_textsignal(app):
    sig = bs.Signal("1")
    badge = bs.Badge(textsignal=sig)
    assert badge.text == "1"
    badge.text = "9+"
    assert badge.text == "9+"
    assert sig() == "9+"


# ----- display-vs-raw widgets stay live and read-only (must NOT break) -----

def test_select_text_is_live_selected_label(app):
    # .text is the display label of the selection; .value is the raw value.
    sel = bs.Select(options=["Apple", "Banana", "Cherry"])
    sel.value = "Banana"
    assert sel.text == "Banana"
    assert sel.value == "Banana"


def test_selectbutton_text_is_live_selected_label(app):
    sb = bs.SelectButton(options=["One", "Two", "Three"])
    sb.value = "Three"
    assert sb.text == "Three"


def test_datefield_separates_display_text_from_raw_value(app):
    # The display/raw split the fix must not conflate: .text is the formatted
    # string, .value is the parsed date object.
    df = bs.DateField(value=datetime.date(2024, 1, 2))
    assert isinstance(df.value, datetime.date)
    assert df.text and df.text != str(df.value)  # formatted display, not the repr