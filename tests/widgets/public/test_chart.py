"""Chart (Phase 1) — embeds a matplotlib figure as a themed widget.

matplotlib is an optional dependency (the ``viz`` extra); the whole module skips
when it is not installed.
"""
import pytest

pytest.importorskip("matplotlib")

from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import bootstack as bs  # noqa: E402
from bootstack.errors import BootstackError  # noqa: E402
from bootstack.style import get_theme_color  # noqa: E402


def test_chart_is_public():
    assert hasattr(bs, "Chart")
    assert "Chart" in bs.__all__


def test_chart_embeds_figure(app):
    fig = Figure()
    fig.add_subplot(111).plot([1, 2, 3], [4, 5, 6])
    chart = bs.Chart(fig)
    app._tk_root.update_idletasks()

    assert chart.figure is fig
    # The matplotlib canvas tk widget is realized inside the chart frame.
    assert chart._internal._widget.winfo_exists()


def test_chart_empty_then_ax(app):
    chart = bs.Chart()
    chart.ax.plot([0, 1], [1, 0])  # `ax` creates an axes on the empty figure
    chart.draw()
    app._tk_root.update_idletasks()

    assert chart.figure.axes  # an axes now exists


def test_chart_figure_setter_swaps(app):
    chart = bs.Chart()
    original = chart.figure
    replacement = Figure()

    chart.figure = replacement
    app._tk_root.update_idletasks()

    assert chart.figure is replacement
    assert chart.figure is not original


def test_chart_recolors_figure_to_theme(shown_app):
    fig = Figure()
    fig.add_subplot(111).plot([1, 2, 3])
    chart = bs.Chart(fig)
    shown_app._tk_root.update_idletasks()

    # The figure face is themed on construction.
    assert to_hex(chart.figure.get_facecolor()).lower() == get_theme_color("background").lower()

    # Toggling the theme recolors it (publisher repaint runs while visible).
    bs.toggle_theme()
    shown_app._tk_root.update_idletasks()
    assert to_hex(chart.figure.get_facecolor()).lower() == get_theme_color("background").lower()


def test_chart_without_matplotlib_raises(monkeypatch, app):
    """Constructing a Chart without matplotlib gives a friendly install error."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ModuleNotFoundError("No module named 'matplotlib'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(BootstackError, match="bootstack\\[viz\\]"):
        bs.Chart()