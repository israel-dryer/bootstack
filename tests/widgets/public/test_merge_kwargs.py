"""Unit tests for the option-merging helper behind `editor_options`.

The helper is where a caller's option dict meets the keyword arguments the
framework derived for the same call. Splatting both into one call raised
`TypeError: got multiple values for keyword argument` naming an internal class
the caller never wrote; merging gives that meeting point one rule.

These need no Tk root — they exercise the helper directly.
"""
from __future__ import annotations

import pytest

from bootstack.errors import BootstackError
from bootstack.widgets._core.kwargs import merge_kwargs, reject_reserved


def test_user_options_win_over_defaults():
    assert merge_kwargs({"a": 1, "b": 2}, {"b": 3}) == {"a": 1, "b": 3}


def test_tolerates_no_user_options():
    assert merge_kwargs({"a": 1}, None) == {"a": 1}
    assert merge_kwargs({"a": 1}, {}) == {"a": 1}


def test_does_not_mutate_its_inputs():
    defaults, user = {"a": 1}, {"b": 2}
    merge_kwargs(defaults, user)
    assert defaults == {"a": 1} and user == {"b": 2}


def test_reserved_key_raises_with_guidance():
    with pytest.raises(BootstackError) as excinfo:
        merge_kwargs({}, {"parent": object()},
                     reserved={"parent": "the form places each editor."},
                     context="Form editor_options")
    message = str(excinfo.value)
    # The message names the API the caller invoked, the key they wrote, and
    # what to do instead — none of which the old TypeError carried.
    assert "Form editor_options" in message
    assert "parent=" in message
    assert "the form places each editor." in message


def test_unlisted_keys_are_allowed_through():
    reject_reserved({"anchor": "se"}, {"parent": "…"}, "Form editor_options")
