"""SplitView review fixes (feat/splitview-review).

The review reshaped pane placement to be key-based (matching the rest of the
widget's identity model) and closed a Tk-leak:

1. `add()` takes the pane `key` positionally and places by key with
   `before=`/`after=`; the integer-index `insert()` is gone (folded into `add`).
2. `move()` repositions by key with `before=`/`after=` instead of an integer.
3. `sash_position()` raises a clean `IndexError` for an out-of-range sash index
   instead of leaking a raw `_tkinter.TclError`.

Pane bookkeeping (order after placement/move/remove) is verified to stay in sync
with the live ttk order.
"""
import tkinter

import pytest

import bootstack as bs


def _sv(app, *keys):
    sv = bs.SplitView(width=600, height=300)
    for k in keys:
        with sv.add(k):
            bs.Label(k)
    app._tk_root.update_idletasks()
    return sv


# ----- positional key + key-relative placement -----

def test_add_takes_key_positionally(app):
    sv = bs.SplitView(width=400, height=200)
    pane = sv.add("main")
    assert pane.key == "main"
    assert sv.keys() == ("main",)


def test_add_auto_generates_key_when_omitted(app):
    sv = bs.SplitView(width=400, height=200)
    assert sv.add().key  # non-empty auto key


def test_add_before(app):
    sv = _sv(app, "a", "c")
    sv.add("b", before="c")
    assert sv.keys() == ("a", "b", "c")


def test_add_after(app):
    sv = _sv(app, "a", "b")
    sv.add("mid", after="a")
    assert sv.keys() == ("a", "mid", "b")


def test_add_after_last_appends(app):
    sv = _sv(app, "a", "b")
    sv.add("end", after="b")
    assert sv.keys() == ("a", "b", "end")


def test_add_before_missing_key_raises_keyerror(app):
    sv = _sv(app, "a")
    with pytest.raises(KeyError):
        sv.add("x", before="nope")


def test_add_before_and_after_together_raises(app):
    sv = _sv(app, "a", "b")
    with pytest.raises(ValueError):
        sv.add("x", before="a", after="b")


# ----- move by key -----

def test_move_before(app):
    sv = _sv(app, "a", "b", "c")
    sv.move("c", before="a")
    assert sv.keys() == ("c", "a", "b")


def test_move_after(app):
    sv = _sv(app, "a", "b", "c")
    sv.move("a", after="b")
    assert sv.keys() == ("b", "a", "c")


def test_move_requires_exactly_one_anchor(app):
    sv = _sv(app, "a", "b")
    with pytest.raises(ValueError):
        sv.move("a")
    with pytest.raises(ValueError):
        sv.move("a", before="b", after="b")


def test_move_relative_to_self_raises(app):
    sv = _sv(app, "a", "b")
    with pytest.raises(ValueError):
        sv.move("a", after="a")


def test_move_missing_anchor_raises_keyerror(app):
    sv = _sv(app, "a", "b")
    with pytest.raises(KeyError):
        sv.move("a", after="nope")


# ----- insert is gone -----

def test_insert_method_removed(app):
    assert not hasattr(bs.SplitView, "insert")


# ----- sash_position out-of-range is a clean IndexError, not a Tk leak -----

def test_sash_position_out_of_range_raises_indexerror(app):
    sv = _sv(app, "a", "b")  # 2 panes -> 1 sash (index 0 valid)
    assert isinstance(sv.sash_position(0), int)
    for bad in (1, -1, 99):
        with pytest.raises(IndexError):
            sv.sash_position(bad)


def test_sash_position_no_sashes_raises_indexerror(app):
    sv = _sv(app, "only")  # 1 pane -> 0 sashes
    with pytest.raises(IndexError):
        sv.sash_position(0)


def test_sash_position_does_not_leak_tclerror(app):
    sv = _sv(app, "a", "b")
    try:
        sv.sash_position(5)
    except tkinter.TclError:  # pragma: no cover
        pytest.fail("sash_position leaked a raw TclError")
    except IndexError:
        pass


# ----- remove keeps order/bookkeeping consistent -----

def test_remove_middle_pane_keeps_order(app):
    sv = _sv(app, "a", "b", "c")
    sv.remove("b")
    assert sv.keys() == ("a", "c")
    assert len(sv.sash_positions) == 1  # 2 panes -> 1 sash
