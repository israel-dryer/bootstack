"""`on_color` (text-on-accent) is consistent and readable across themes.

Accent text is button/pill/badge labels (bold, large), so the WCAG bar is 3.0,
not 4.5. A saturated colored accent (blue/purple/green/red) takes WHITE in both
light and dark themes; a genuinely light accent (bright yellow `warning`, bright
cyan `info`) takes BLACK. The light-mode white gate previously used 4.5, which
sent mid-tone colored accents (e.g. dracula-light's purple primary, white ~3.7)
to black — inconsistent with the same accent in dark mode.
"""
import bootstack as bs
from bootstack.style.style import get_style


def _luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _is_white(c):
    return c.lower() in ("#ffffff", "#fff")


def _is_black(c):
    return c.lower() in ("#000000", "#000")


def test_light_theme_colored_accent_takes_white(app):
    # dracula-light primary is a mid-tone purple — white at ~3.7, which clears the
    # 3.0 button bar; it must read white (it previously fell to black).
    bs.set_theme("dracula-light")
    b = get_style().style_builder
    for token in ("primary", "secondary", "danger"):
        assert _is_white(b.on_color(b.color(token))), token


def test_light_accents_keep_black_text(app):
    # Bright cyan info / bright yellow warning must keep dark text (white unreadable).
    bs.set_theme("bootstrap-light")
    b = get_style().style_builder
    assert _is_black(b.on_color(b.color("info")))      # bright cyan
    assert _is_black(b.on_color(b.color("warning")))   # bright yellow


def test_on_color_clears_the_button_contrast_bar(app):
    # Whatever on_color picks, it clears the 3.0 (large/bold) WCAG bar for every
    # accent in every built-in theme.
    from bootstack.style import get_themes

    accents = ("primary", "secondary", "info", "success", "warning", "danger")
    worst = 99.0
    for theme in (t["name"] for t in get_themes()):
        bs.set_theme(theme)
        b = get_style().style_builder
        for a in accents:
            acc = b.color(a)
            worst = min(worst, _contrast(b.on_color(acc), acc))
    assert worst >= 3.0, f"an accent label is below the 3.0 bar ({worst:.2f})"
