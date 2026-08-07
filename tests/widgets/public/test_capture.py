"""Tests for `widget.capture()` (#427).

A capture reads pixels from the display, so what these can assert is limited on
purpose. Whether the saved image shows *this* application depends on what else
the machine has on screen, which no assertion can control — that question is
settled by `development/verify_427_capture.py`, which toggles the theme between
two captures and proves the pixels track this window. An earlier version of that
probe passed every geometry check while capturing a browser, which is exactly
why nothing here pretends to verify content.

What is asserted instead are the invariants that hold regardless of what is on
screen: the rectangle captured, the format chosen, the errors raised, and the
always-on-top setting left as it was found.
"""
from __future__ import annotations

import pytest
from PIL import Image

import bootstack as bs
from bootstack.errors import BootstackError

pytestmark = pytest.mark.gui


def test_capture_writes_the_file_and_returns_its_path(shown_app, tmp_path):
    label = bs.Label("capture me")
    shown_app.tk.update_idletasks()

    target = tmp_path / "shot.png"
    written = label.capture(target, settle=0)

    assert written == target
    assert written.is_file() and written.stat().st_size > 0


def test_capture_matches_the_widget_rectangle(shown_app, tmp_path):
    """The grab is the widget's own rect, not the window's."""
    label = bs.Label("measure me")
    shown_app.tk.update_idletasks()
    expected = (label.tk.winfo_width(), label.tk.winfo_height())

    with Image.open(label.capture(tmp_path / "rect.png", settle=0)) as img:
        assert img.size == expected


def test_inset_trims_every_edge(shown_app, tmp_path):
    label = bs.Label("trim me")
    shown_app.tk.update_idletasks()
    full = (label.tk.winfo_width(), label.tk.winfo_height())

    with Image.open(label.capture(tmp_path / "inset.png", inset=2, settle=0)) as img:
        assert img.size == (full[0] - 4, full[1] - 4)


def test_extension_selects_the_format(shown_app, tmp_path):
    """`.png`, `.jpg` and `.pdf` are the formats #425 asked for."""
    label = bs.Label("format me")
    shown_app.tk.update_idletasks()

    for suffix, expected in ((".png", "PNG"), (".jpg", "JPEG")):
        written = label.capture(tmp_path / f"shot{suffix}", settle=0)
        with Image.open(written) as img:
            assert img.format == expected

    # Pillow writes PDF but cannot read it back, so check the magic bytes.
    pdf = label.capture(tmp_path / "shot.pdf", settle=0)
    assert pdf.read_bytes()[:4] == b"%PDF"


def test_missing_parent_folders_are_created(shown_app, tmp_path):
    label = bs.Label("nested")
    shown_app.tk.update_idletasks()

    written = label.capture(tmp_path / "a" / "b" / "shot.png", settle=0)
    assert written.is_file()


def test_unknown_extension_raises_a_bootstack_error(shown_app, tmp_path):
    label = bs.Label("bad format")
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="extension selects the format"):
        label.capture(tmp_path / "shot.wat", settle=0)


def test_detached_widget_cannot_be_captured(shown_app, tmp_path):
    """The guard that stops a capture from silently grabbing whatever is behind."""
    label = bs.Label("gone")
    shown_app.tk.update_idletasks()
    label.detach()
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="not visible on screen"):
        label.capture(tmp_path / "detached.png", settle=0)


def test_inset_larger_than_the_widget_raises(shown_app, tmp_path):
    label = bs.Label("tiny")
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="trims away the whole capture"):
        label.capture(tmp_path / "over.png", inset=9999, settle=0)


def test_capture_restores_a_window_that_was_not_topmost(shown_app, tmp_path):
    """Capturing raises the window; it must put the setting back afterward."""
    root = shown_app.tk
    root.attributes("-topmost", False)
    root.update_idletasks()

    bs.Label("restore me").capture(tmp_path / "restore.png", settle=0)

    assert not root.attributes("-topmost")


def test_capture_leaves_a_deliberately_topmost_window_pinned(shown_app, tmp_path):
    """An application that pinned its window must not be un-pinned by a capture.

    This is the control for the test above: the same code path, opposite
    starting state, so a fix that simply forced the flag off would fail here.
    """
    root = shown_app.tk
    root.attributes("-topmost", True)
    root.update_idletasks()
    try:
        bs.Label("still pinned").capture(tmp_path / "pinned.png", settle=0)
        assert root.attributes("-topmost")
    finally:
        root.attributes("-topmost", False)