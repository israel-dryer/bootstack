"""Tests for IntlFormatter locale-aware formatting.

Regression coverage for two bugs:

* date/time/datetime presets passed the locale into Babel's positional
  ``tzinfo`` slot, crashing on every time-component and datetime preset.
* the explicit-precision currency path built its pattern with a literal
  ``\\u00A4`` (double backslash) instead of the ¤ currency placeholder, and
  left ``currency_digits`` at its default so the precision was ignored.

These run headless — IntlFormatter needs no App.
"""
from __future__ import annotations

import re
from datetime import date, datetime, time
from decimal import Decimal

import pytest

from bootstack.i18n import IntlFormatter

TIME_SPECS = ["shortTime", "longTime", "hour", "minute", "second", "millisecond"]
DATE_SPECS = [
    "longDate", "shortDate", "monthAndDay", "monthAndYear", "quarterAndYear",
    "day", "dayOfWeek", "month", "quarter", "year",
    "longDateLongTime", "shortDateShortTime",
]
DATETIME_SPECS = DATE_SPECS + ["longTime", "shortTime", "hour", "minute", "second", "millisecond"]


# ---------- regression: positional-locale-as-tzinfo crash ----------

@pytest.mark.parametrize("loc", ["en_US", "de_DE", "fr_FR", "ja_JP"])
@pytest.mark.parametrize("spec", TIME_SPECS)
def test_time_specs_do_not_crash(loc, spec):
    out = IntlFormatter(locale=loc).format(time(14, 30, 5), spec)
    assert isinstance(out, str) and out != ""


@pytest.mark.parametrize("loc", ["en_US", "de_DE"])
@pytest.mark.parametrize("spec", DATETIME_SPECS)
def test_datetime_specs_do_not_crash(loc, spec):
    # A naive datetime used to crash on every datetime/time preset.
    out = IntlFormatter(locale=loc).format(datetime(2025, 9, 2, 14, 30, 5), spec)
    assert isinstance(out, str) and out != ""


@pytest.mark.parametrize("loc", ["en_US", "de_DE"])
@pytest.mark.parametrize("spec", DATE_SPECS)
def test_date_specs_do_not_crash(loc, spec):
    out = IntlFormatter(locale=loc).format(date(2025, 9, 2), spec)
    assert isinstance(out, str) and out != ""


# ---------- currency precision ----------

def _frac_digits(s: str, mark: str = ".") -> int:
    """Count digits after the locale's decimal mark (ignoring a trailing symbol)."""
    m = re.search(re.escape(mark) + r"(\d+)", s)
    return len(m.group(1)) if m else 0


@pytest.mark.parametrize("prec", [0, 1, 2, 3])
def test_currency_precision_honored(prec):
    out = IntlFormatter(locale="en_US").format(
        1234.5, {"type": "currency", "currency": "USD", "precision": prec}
    )
    assert "1,234" in out                  # grouping intact
    assert _frac_digits(out) == prec       # precision wins over the currency default


def test_currency_precision_de_uses_comma_decimal():
    out = IntlFormatter(locale="de_DE").format(
        1234.5, {"type": "currency", "currency": "EUR", "precision": 2}
    )
    assert _frac_digits(out, ",") == 2


def test_currency_precision_not_garbled():
    # Regression: the pattern used to render the literal text "¤#,##0.00".
    out = IntlFormatter(locale="en_US").format(
        1234.5, {"type": "currency", "currency": "USD", "precision": 2}
    )
    assert "u00A4" not in out
    assert "#" not in out                  # no raw CLDR pattern leaking through
    assert "$" in out


def test_currency_preset_unaffected():
    assert IntlFormatter(locale="en_US").format(1234.5, "currency") == "$1,234.50"


# ---------- smoke: unchanged number/date wiring still correct ----------

def test_locale_wiring_smoke():
    f = IntlFormatter(locale="de_DE")
    assert f.format(1234.56, "decimal") == "1.234,56"
    long_date = f.format(date(2025, 9, 2), "longDate")
    assert "September" in long_date and "2025" in long_date


# --- Decimal values format like any other number ---------------------------

@pytest.mark.parametrize("spec", [
    "decimal", "currency", "percent", "#,##0.00",
    "thousands", "millions", "largeNumber", "exponential",
])
def test_decimal_formats_like_the_equivalent_float(spec):
    # A Decimal matched no branch in `format()` and fell through to `str(value)`,
    # so `value_format` was silently ignored — worst on `currency`, which is the
    # format you reach for precisely when the value is a Decimal.
    fmt = IntlFormatter(locale="en_US")
    assert fmt.format(Decimal("12345.6789"), spec) == fmt.format(12345.6789, spec)


def test_decimal_is_not_rounded_through_float():
    # Babel formats a Decimal natively. Coercing to float first would round away
    # the precision the caller chose Decimal to keep.
    fmt = IntlFormatter(locale="en_US")
    pattern = "#,##0.0000000000000000000"
    exact = Decimal("0.1234567890123456789")
    assert fmt.format(exact, pattern) == "0.1234567890123456789"
    assert fmt.format(exact, pattern) != fmt.format(float(exact), pattern)
