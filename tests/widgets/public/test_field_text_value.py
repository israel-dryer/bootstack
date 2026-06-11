"""The field-widget value/text contract: `.value` is the raw parsed datum,
`.text` is the formatted display string. Regression guard for the option-databag
work, which briefly made `.value` derive from the display text and broke the
`value_format` widgets (TimeField returned a string instead of a `datetime.time`).
"""
import datetime

import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            a._tk_root.destroy()
        except Exception:
            pass


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
