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
