"""The unified theme walk recolors tree widgets via `_bs_apply_theme`.

`Style.apply_theme_walk` is the single mechanism: on a theme change it applies
every *visible* widget from the root; on a container-show it applies every
*stale* widget in the shown subtree (regardless of `winfo_viewable()`, which is
unreliable for a widget embedded in a scrollable page's canvas).
"""
import tkinter as tk

import bootstack as bs
from bootstack.style.style import get_style


def _stub(parent):
    """A tk widget exposing `_bs_apply_theme`, like a migrated canvas widget."""
    w = tk.Frame(parent)
    w._applied = 0
    w._bs_apply_theme = lambda: setattr(w, "_applied", w._applied + 1)
    return w


def test_walk_applies_stale_widget_on_container_show(app):
    container = tk.Frame(app.tk)
    container.pack()
    w = _stub(container)
    style = get_style()
    w._bs_theme_version = -1  # never themed → stale

    style.apply_theme_walk(container, only_stale=True)

    assert w._applied == 1
    assert w._bs_theme_version == style._theme_version  # stamped


def test_walk_skips_uptodate_widget_when_only_stale(app):
    container = tk.Frame(app.tk)
    container.pack()
    w = _stub(container)
    style = get_style()
    w._bs_theme_version = style._theme_version  # already current

    style.apply_theme_walk(container, only_stale=True)

    assert w._applied == 0  # no redundant repaint when navigating without a theme change


def test_datatable_recolors_via_apply_hook(app):
    bs.set_theme("gruvbox-light")
    table = bs.DataTable(
        rows=[{"id": 1, "name": "Ada"}],
        selection_mode="multi",
        show_selection_controls=True,
    )
    tv = table._internal
    tv._tree.selection_set(tv._tree.get_children("")[0])
    tv._update_selection_markers()
    before = tv._marker_icon_specs()[1]

    bs.set_theme("tokyo-night-dark")
    get_style()._apply_theme_to_widget(tv)  # the per-widget step the walk runs

    assert tv._marker_icon_specs()[1] != before
