"""Chart — embeds a matplotlib figure as a themed widget, with a managed
reactive render path (``render=`` + ``signal=``).

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


# ----- Phase 2: managed render + reactive signals -----------------------------


def test_managed_render_draws(app):
    def render(ax):
        ax.plot([0, 1, 2], [2, 1, 2])

    chart = bs.Chart(render=render)
    app._tk_root.update_idletasks()

    axes = chart.figure.axes
    assert len(axes) == 1
    assert len(axes[0].lines) == 1


def test_render_receives_signal_value_and_rerenders(app):
    n = bs.Signal(3)

    def render(ax, count):
        ax.plot(range(count), range(count))

    chart = bs.Chart(render=render, signal=n)
    app._tk_root.update_idletasks()
    assert chart.figure.axes[0].lines[0].get_xdata().tolist() == [0, 1, 2]

    n.set(6)  # debounce=0 -> re-renders synchronously
    app._tk_root.update_idletasks()
    assert chart.figure.axes[0].lines[0].get_xdata().tolist() == [0, 1, 2, 3, 4, 5]


def test_render_arity_one_ignores_data(app):
    n = bs.Signal(5)

    def render(ax):  # no data param — bound signal still drives re-render
        ax.plot([0, 1], [1, 0])

    chart = bs.Chart(render=render, signal=n)
    app._tk_root.update_idletasks()
    assert len(chart.figure.axes[0].lines) == 1

    n.set(9)
    app._tk_root.update_idletasks()
    assert len(chart.figure.axes[0].lines) == 1  # one axes, one line, no crash


def test_managed_render_uses_semantic_color_cycle(app):
    def render(ax):
        ax.plot([0, 1], [0, 1])  # series 1 -> primary
        ax.plot([0, 1], [1, 0])  # series 2 -> success

    chart = bs.Chart(render=render)
    app._tk_root.update_idletasks()

    lines = chart.figure.axes[0].lines
    assert to_hex(lines[0].get_color()).lower() == get_theme_color("primary[500]").lower()
    assert to_hex(lines[1].get_color()).lower() == get_theme_color("success[500]").lower()


def test_signal_without_render_raises(app):
    with pytest.raises(BootstackError, match="render="):
        bs.Chart(signal=bs.Signal(1))


def test_managed_rerenders_on_theme_change(shown_app):
    def render(ax):
        ax.plot([1, 2, 3])

    chart = bs.Chart(render=render)
    shown_app._tk_root.update_idletasks()
    assert to_hex(chart.figure.get_facecolor()).lower() == get_theme_color("background").lower()

    bs.toggle_theme()
    shown_app._tk_root.update_idletasks()
    assert to_hex(chart.figure.get_facecolor()).lower() == get_theme_color("background").lower()


def test_rapid_signal_changes_coalesce_to_one_render(app):
    """A burst of signal changes renders once (per idle), not once per change."""
    calls = {"n": 0}
    value = bs.Signal(0)

    def render(ax, v):
        calls["n"] += 1
        ax.plot(range(max(1, v)))

    bs.Chart(render=render, signal=value)
    app._tk_root.update_idletasks()
    base = calls["n"]  # the synchronous render at construction

    for v in range(1, 6):  # five rapid changes, no idle pump between
        value.set(v)
    app._tk_root.update_idletasks()  # single coalesced flush

    assert calls["n"] == base + 1


# ----- animation (blitting) ---------------------------------------------------


def test_animate_sets_up_artists_and_returns_handle(shown_app):
    created = {"n": 0}

    def setup(ax):
        created["n"] += 1
        (line,) = ax.plot([], [])
        ax.set_xlim(0, 10)
        ax.set_ylim(-1, 1)
        return line

    def update(frame, line):
        line.set_data([0, frame], [0, 1])

    chart = bs.Chart()
    anim = chart.animate(setup, update, interval=20)
    shown_app._tk_root.update()  # let the first draw start the animation

    assert created["n"] == 1               # setup ran exactly once
    assert len(chart.figure.axes) == 1
    assert len(chart._internal._anim_artists) == 1
    assert anim.running is True


def test_animation_handle_stop_start(shown_app):
    def setup(ax):
        (line,) = ax.plot([], [])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return line

    chart = bs.Chart()
    anim = chart.animate(setup, lambda frame, line: None, interval=20)
    shown_app._tk_root.update()

    anim.stop()
    assert anim.running is False
    anim.start()
    assert anim.running is True


def test_animation_recolors_on_theme_change(shown_app):
    def setup(ax):
        (line,) = ax.plot([], [])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return line

    chart = bs.Chart()
    chart.animate(setup, lambda frame, line: None, interval=20)
    shown_app._tk_root.update()
    before = to_hex(chart.figure.get_facecolor()).lower()

    bs.toggle_theme()
    shown_app._tk_root.update()
    after = to_hex(chart.figure.get_facecolor()).lower()

    assert after == get_theme_color("background").lower()
    assert after != before


def test_animation_pauses_when_hidden_resumes_when_shown(shown_app):
    def setup(ax):
        (line,) = ax.plot([], [])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return line

    chart = bs.Chart()
    anim = chart.animate(setup, lambda frame, line: None, interval=20)
    shown_app._tk_root.update()
    assert anim.running is True                       # visible -> playing
    assert chart._internal._anim_running_now is True

    chart.detach()                                    # hide it (<Unmap>)
    shown_app._tk_root.update()
    assert anim.running is False                      # hidden -> paused
    assert chart._internal._anim_running_now is False

    chart.attach()                                    # show it again (<Map>)
    shown_app._tk_root.update()
    assert anim.running is True                       # shown -> resumed
    assert chart._internal._anim_running_now is True


def test_theme_change_while_hidden_applies_on_return(shown_app):
    """A theme changed while the chart is hidden is applied when it reappears."""
    def setup(ax):
        (line,) = ax.plot([], [])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return line

    chart = bs.Chart()
    chart.animate(setup, lambda frame, line: None, interval=20)
    shown_app._tk_root.update()

    chart.detach()                                    # hide on "another page"
    shown_app._tk_root.update()
    bs.toggle_theme()                                 # theme changes while hidden
    shown_app._tk_root.update()
    chart.attach()                                    # navigate back
    shown_app._tk_root.update()

    assert to_hex(chart.figure.get_facecolor()).lower() == get_theme_color("background").lower()