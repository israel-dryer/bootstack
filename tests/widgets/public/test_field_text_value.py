"""The field-widget value/text contract: `.value` is the raw parsed datum,
`.text` is the formatted display string. Regression guard for the option-databag
work, which briefly made `.value` derive from the display text and broke the
`value_format` widgets (TimeField returned a string instead of a `datetime.time`).
"""
import datetime

import pytest

import bootstack as bs


# Every field widget exposes both .value and .text.
FIELD_FACTORIES = [
    ("TextField", lambda: bs.TextField(value="hello")),
    ("NumberField", lambda: bs.NumberField(value=1234.5)),
    ("PasswordField", lambda: bs.PasswordField(value="secret")),
    ("DateField", lambda: bs.DateField(value="2024-01-02")),
    ("TimeField", lambda: bs.TimeField(value="08:30")),
    ("PathField", lambda: bs.PathField(value="/tmp/x")),
    ("SpinnerField", lambda: bs.SpinnerField(value="3")),
    ("TextArea", lambda: bs.TextArea(value="multi\nline")),
    ("CodeEditor", lambda: bs.CodeEditor(value="print('hi')")),
    ("Select", lambda: bs.Select(options=["a", "b"], value="a")),
    ("SelectButton", lambda: bs.SelectButton(options=["a", "b"], value="a")),
]


def test_numberfield_signal_is_numeric_and_two_way(app):
    sig = bs.Signal(0.22)
    nf = bs.NumberField(signal=sig, min_value=0.0, max_value=0.5, step=0.1)
    app._tk_root.update_idletasks()

    # Seeds the field from the signal's numeric value.
    assert nf.value == 0.22

    # signal -> field
    sig.set(0.4)
    app._tk_root.update_idletasks()
    assert nf.value == 0.4

    # field commit -> signal, as a number (not text)
    entry = nf._internal._entry
    entry.delete(0, "end")
    entry.insert(0, "0.3")
    entry.event_generate("<FocusOut>")
    app._tk_root.update_idletasks()
    assert sig() == 0.3
    assert isinstance(sig(), float)


def test_typed_fields_signal_binds_value_not_text(app):
    import datetime

    # DateField: signal carries a date.
    dsig = bs.Signal(datetime.date(2024, 1, 2))
    df = bs.DateField(signal=dsig)
    app._tk_root.update_idletasks()
    assert df.value == datetime.date(2024, 1, 2)
    assert df.signal is dsig
    dsig.set(datetime.date(2025, 6, 15))
    app._tk_root.update_idletasks()
    assert df.value == datetime.date(2025, 6, 15)

    # TimeField: signal carries a time.
    tsig = bs.Signal(datetime.time(8, 30))
    tf = bs.TimeField(signal=tsig)
    app._tk_root.update_idletasks()
    assert tf.value == datetime.time(8, 30)
    assert isinstance(tf.value, datetime.time)


def test_datetime_signal_reads_back_object_not_string(app):
    # #227: a date/time signal used to land in a StringVar and read back its
    # string form. It must round-trip the object — both directly and via a field.
    import datetime

    dsig = bs.Signal(datetime.date(2024, 1, 2))
    assert dsig() == datetime.date(2024, 1, 2)
    assert type(dsig()) is datetime.date          # not str

    df = bs.DateField(signal=dsig)
    app._tk_root.update_idletasks()

    # field -> signal on a *programmatic* value set (was only firing on commit)
    df.value = datetime.date(2030, 3, 4)
    app._tk_root.update_idletasks()
    assert dsig() == datetime.date(2030, 3, 4)
    assert type(dsig()) is datetime.date

    # a subscriber receives the object, not a string
    seen = []
    dsig.subscribe(lambda v: seen.append(v))
    df.value = datetime.date(2031, 5, 6)
    app._tk_root.update_idletasks()
    assert seen == [datetime.date(2031, 5, 6)]

    # TimeField, same contract
    tsig = bs.Signal(datetime.time(9, 30))
    tf = bs.TimeField(signal=tsig)
    app._tk_root.update_idletasks()
    tf.value = datetime.time(14, 45)
    app._tk_root.update_idletasks()
    assert tsig() == datetime.time(14, 45)
    assert type(tsig()) is datetime.time


@pytest.mark.parametrize("name, make", [
    ("NumberField", lambda: bs.NumberField(textsignal=bs.Signal("0"))),
    ("DateField", lambda: bs.DateField(textsignal=bs.Signal(""))),
    ("TimeField", lambda: bs.TimeField(textsignal=bs.Signal(""))),
])
def test_typed_fields_reject_textsignal(app, name, make):
    # A typed field binds its value via signal=; textsignal= is removed and must
    # fail loudly (not be silently swallowed by **kwargs).
    with pytest.raises(TypeError, match="textsignal"):
        make()


def test_value_signal_unsubscribes_on_destroy(app):
    # A Signal usually outlives the widgets bound to it; destroying a bound field
    # must release its subscription so the field is not pinned in memory.
    sig = bs.Signal(0.0)
    before = len(sig._subscribers)
    nf = bs.NumberField(signal=sig, step=0.1)
    app._tk_root.update_idletasks()
    assert len(sig._subscribers) == before + 1  # bound

    nf.destroy()
    app._tk_root.update_idletasks()
    assert len(sig._subscribers) == before  # released


def test_push_to_signal_reconciles_numeric_types(app):
    # int field value -> float-typed signal widens cleanly.
    fsig = bs.Signal(0.0)
    nf = bs.NumberField(signal=fsig, step=1)
    nf._push_to_signal(5)
    assert fsig() == 5.0 and isinstance(fsig(), float)

    # Fractional value -> int-typed signal is incompatible: it must NOT raise
    # into the Tk loop; the signal simply keeps its prior value.
    isig = bs.Signal(2)
    nf2 = bs.NumberField(signal=isig, step=1)
    nf2._push_to_signal(0.3)
    assert isig() == 2

    # An integral float -> int-typed signal coerces back to int.
    nf2._push_to_signal(7.0)
    assert isig() == 7 and isinstance(isig(), int)


def test_numberfield_stepping_stays_on_step_grid(app):
    nf = bs.NumberField(value=0.0, min_value=0.0, max_value=1.0, step=0.05)
    entry = nf._internal._entry
    values = []
    for _ in range(8):
        entry.event_generate("<<Increment>>")
        app._tk_root.update_idletasks()
        values.append(nf.value)
    # No accumulated float error — every value is a clean multiple of 0.05.
    assert values == [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]


@pytest.mark.parametrize("name, make", FIELD_FACTORIES, ids=[f[0] for f in FIELD_FACTORIES])
def test_field_exposes_text_as_str(app, name, make):
    w = make()
    assert hasattr(w, "text"), f"{name} is missing the .text property"
    assert isinstance(w.text, str), f"{name}.text should be a str, got {type(w.text).__name__}"


def test_timefield_value_is_typed_text_is_formatted(app):
    tf = bs.TimeField(value="08:30")
    # .value is the raw datum (regression: was returning the formatted string)
    assert isinstance(tf.value, datetime.time), f"value type={type(tf.value).__name__}"
    # .text is the formatted display
    assert isinstance(tf.text, str) and tf.text != str(tf.value)
    # round-trips a time object through the value setter
    tf.value = datetime.time(15, 30)
    assert tf.value == datetime.time(15, 30)
    assert "30" in tf.text


def test_datefield_value_is_typed_text_is_formatted(app):
    df = bs.DateField(value="2024-01-02")
    assert df.value == datetime.date(2024, 1, 2)
    assert df.text != str(df.value)        # 'January 2, 2024' vs '2024-01-02'
    assert "2024" in df.text


def test_numberfield_value_is_numeric(app):
    nf = bs.NumberField(value=1234.5)
    assert nf.value == 1234.5 and isinstance(nf.value, float)
    assert isinstance(nf.text, str)


def test_select_text_is_label_value_is_value(app):
    s = bs.Select(options=[("Dark Mode", "dark")], value="dark")
    assert s.value == "dark"        # value-space
    assert s.text == "Dark Mode"    # display label


def test_decimal_seeded_field_displays_formatted(app):
    # A currency field seeded with a Decimal showed the raw number until you
    # edited it — the commit parsed to a float, which then formatted, so the
    # field appeared to fix itself. The formatter ignored Decimal entirely.
    from decimal import Decimal

    field = bs.TextField(value=Decimal("3.50"), value_format="currency")
    app._tk_root.update_idletasks()
    assert field.text == "$3.50"
    assert field.value == Decimal("3.50")
