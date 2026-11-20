"""A field too narrow for its content keeps its buttons.

When a `Select`, `DateField` or `NumberField` is narrower than its content, the
text box shrinks and the arrow, calendar button or steppers stay full size.
"""
from __future__ import annotations

import time

import pytest

import bootstack as bs

pytestmark = pytest.mark.gui


def _pump(root, condition, timeout=3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_a_squeezed_select_keeps_its_arrow_button(shown_app):
    win = bs.Window(title="squeeze", size=(150, 120), padding=8, horizontal_items="stretch")
    try:
        with win:
            select = bs.Select(["Balloon, red"], value="Balloon, red")
        win.show()
        field = select.tk
        assert _pump(field, lambda: field.winfo_ismapped() and field.winfo_width() > 1), (
            "precondition: the field is mapped"
        )
        assert field.winfo_width() < field.winfo_reqwidth(), (
            "precondition: the field is narrower than it asks for"
        )

        button = select.addons["dropdown"]
        assert button.winfo_width() >= button.winfo_reqwidth(), (
            f"the arrow button is {button.winfo_width()} px wide and asks for {button.winfo_reqwidth()}"
        )
    finally:
        win.close()


def test_buttons_after_the_entry_keep_their_order(shown_app):
    win = bs.Window(title="order", size=(320, 120), padding=8, horizontal_items="stretch")
    try:
        with win:
            number = bs.NumberField(5)
        win.show()
        minus, plus = number.addons["decrement"], number.addons["increment"]
        assert _pump(plus, lambda: minus.winfo_ismapped() and plus.winfo_ismapped()), (
            "precondition: both steppers are mapped"
        )

        assert minus.winfo_x() < plus.winfo_x(), "the steppers swapped places"
    finally:
        win.close()
