"""Destroying a `TextArea` releases what its core installed (#488).

`_MultilineCore` forwarded `bind` to its inner `Text`, so the `<Destroy>`
binding in `__init__` landed on the Text rather than the Frame. The handler's
`event.widget is not self` guard could then never pass, and the whole teardown
block was unreachable: the filter chain's redirector command and the
per-widget mousewheel bindtag both outlived the widget. `CodeEditor` is backed
by the same core.
"""
from __future__ import annotations

import bootstack as bs


def test_destroying_a_textarea_releases_what_its_core_installed(app):
    ta = bs.TextArea()
    app.tk.update()
    core = ta._internal.core
    scroll_tag = core._scroll_tag
    text_path = str(core.text)

    # Preconditions. Without them both assertions below pass against a widget
    # that never installed anything in the first place.
    assert app.tk.call("bind", scroll_tag), (
        "precondition failed - no wheel bindings to release"
    )
    assert app.tk.call("info", "commands", text_path), (
        "precondition failed - no redirector command to release"
    )

    ta.destroy()
    app.tk.update()

    # The wheel handler is bound to a per-widget bindtag, which is interpreter
    # state: it survives the widget unless the teardown sweeps it.
    assert not app.tk.call("bind", scroll_tag), (
        "the wheel bindtag outlived the widget: %r"
        % (app.tk.call("bind", scroll_tag),)
    )
    # The redirector renames the Text's own command aside and installs a Python
    # dispatcher under the original name. Tk deletes the renamed one on destroy,
    # so the dispatcher - and the chain it holds - leaks unless closed.
    assert not app.tk.call("info", "commands", text_path), (
        "the redirector command outlived the widget: %r"
        % (app.tk.call("info", "commands", text_path),)
    )