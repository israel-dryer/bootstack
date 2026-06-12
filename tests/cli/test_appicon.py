"""Tests for the `bootstack appicon` designer command (non-GUI parts)."""

from __future__ import annotations

import argparse

import pytest

from bootstack.cli import appicon


def test_parser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    appicon.add_parser(sub)
    args = parser.parse_args(["appicon"])
    assert callable(args.func)


@pytest.mark.parametrize(
    "color, ok",
    [
        ("#fff", True),
        ("#0d6efd", True),
        ("#0d6efdff", True),
        ("primary", False),
        ("0d6efd", False),
        ("#xyz", False),
        ("#0d6ef", False),
    ],
)
def test_is_hex(color, ok):
    assert appicon._is_hex(color) is ok
