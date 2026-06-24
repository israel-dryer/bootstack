"""The Gauge canvas background recolors with the theme (unified theme walk).

The meter canvas takes the surface *token* (not a frozen color), so the unified
theme walk re-resolves its background against the active theme on every change.
The painted content (arcs/face/text) redraws via the widget's `_bs_apply_theme`.
"""
import bootstack as bs
from bootstack.style.style import get_style


def _expected_bg():
    return get_style().style_builder.color("background")


def test_gauge_canvas_background_recolors_across_themes(app):
    bs.set_theme("gruvbox-light")
    gauge = bs.Gauge(value=50, max_value=100)
    m = gauge._internal
    app.tk.update_idletasks()

    # canvas carries the surface TOKEN, not a resolved hex — so the theme walk
    # re-resolves it fresh each change instead of re-applying a frozen color.
    assert getattr(m._canvas, "_surface", None) == "background"

    # Apply each theme through the engine's per-widget hook (the harness window
    # isn't mapped, so the viewable-gated walk is exercised in the GUI suite).
    style = get_style()
    for theme in ("tokyo-night-dark", "dracula-dark", "gruvbox-light"):
        bs.set_theme(theme)
        style._apply_theme_to_widget(m._canvas)
        assert m._canvas.cget("background") == _expected_bg(), theme


def test_gauge_uses_unified_apply_hook(app):
    gauge = bs.Gauge(value=10)
    m = gauge._internal
    # migrated off the legacy per-widget repaint onto the unified hook
    assert hasattr(m, "_bs_apply_theme")
    assert not hasattr(m, "_theme_repaint")
