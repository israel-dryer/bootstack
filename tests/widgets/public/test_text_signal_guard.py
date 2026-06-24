"""A `Signal` in the plain `text=` slot raises instead of rendering its name.

A `Signal` is truthy and stringifies to its name, so passing one as `text=`
silently renders something like `"SIG2"`. The text-bearing widgets that pair a
`text=` caption with a `textsignal=` binding (`Label`, `Button`, `MenuButton`)
guard against the mistake with a `TypeError` pointing at `textsignal=`.
"""
import pytest

import bootstack as bs


@pytest.mark.parametrize("cls", [bs.Label, bs.Button, bs.MenuButton])
def test_signal_in_text_slot_raises(app, cls):
    sig = bs.Signal("hello")
    with pytest.raises(TypeError, match="textsignal="):
        cls(sig)


@pytest.mark.parametrize("cls", [bs.Label, bs.Button, bs.MenuButton])
def test_plain_text_still_works(app, cls):
    w = cls("plain")
    assert w.text == "plain"


@pytest.mark.parametrize("cls", [bs.Label, bs.Button, bs.MenuButton])
def test_textsignal_binding_still_works(app, cls):
    sig = bs.Signal("bound")
    w = cls(textsignal=sig)
    assert w.text == "bound"
