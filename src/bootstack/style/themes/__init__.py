"""Built-in color theme families, defined as `Theme` instances.

Each family declares its semantic accent colors (the `[500]` ramp anchors) plus a
light and dark background block; `install()` generates and registers both
`<name>-light` and `<name>-dark` variants. The framework picks the per-mode ramp
step for solids, washes, borders, and emphasis — there is no per-mode shade
boilerplate. Installed into the registry by `install_builtin_themes`, called from
the theme provider.

The non-bootstrap families adapt well-known, open-licensed designer palettes
(Nord, Solarized, Catppuccin, Gruvbox, Dracula, Tokyo Night, One, Everforest) to
the framework's semantic roles.
"""
from __future__ import annotations

from bootstack.style.theme import Theme

# --- Bootstrap (the neutral reference) -------------------------------------
BOOTSTRAP = Theme(
    name="bootstrap",
    primary="#0d6efd", success="#198754", info="#0dcaf0", warning="#ffc107", danger="#dc3545",
    light=dict(background="#ffffff", foreground="#212529"),
    dark=dict(background="#212529", foreground="#f8f9fa"),
)

# --- PyData (professional teal) --------------------------------------------
PYDATA = Theme(
    name="pydata",
    display_name="PyData",
    primary="#0a7d91", success="#198754", info="#0dcaf0", warning="#ffc107", danger="#dc3545",
    secondary="#8045e5",
    neutral="#677384",
    light=dict(background="#ffffff", foreground="#222832"),
    dark=dict(background="#14181e", foreground="#ced6dd"),
)

# --- Nord (cool arctic) -----------------------------------------------------
NORD = Theme(
    name="nord",
    primary="#5e81ac", success="#a3be8c", info="#88c0d0", warning="#ebcb8b", danger="#bf616a",
    secondary="#b48ead",
    neutral="#4c566a",
    light=dict(background="#eceff4", foreground="#2e3440"),
    dark=dict(background="#2e3440", foreground="#eceff4"),
)

# --- Solarized (precision classic) -----------------------------------------
SOLARIZED = Theme(
    name="solarized",
    primary="#268bd2", success="#859900", info="#2aa198", warning="#b58900", danger="#dc322f",
    secondary="#6c71c4",
    neutral="#839496",
    light=dict(background="#f6f1e9", foreground="#586e75"),
    dark=dict(background="#002b36", foreground="#93a1a1"),
)

# --- Catppuccin (soft pastel) ----------------------------------------------
CATPPUCCIN = Theme(
    name="catppuccin",
    primary="#8839ef", success="#40a02b", info="#179299", warning="#df8e1d", danger="#d20f39",
    secondary="#ea76cb",
    neutral="#8c8fa1",
    light=dict(background="#eff1f5", foreground="#4c4f69"),
    dark=dict(background="#1e1e2e", foreground="#cdd6f4"),
)

# --- Gruvbox (warm retro) ---------------------------------------------------
GRUVBOX = Theme(
    name="gruvbox",
    primary="#458588", success="#98971a", info="#689d6a", warning="#d79921", danger="#cc241d",
    secondary="#d65d0e",
    neutral="#928374",
    light=dict(background="#f2ede9", foreground="#3c3836"),
    dark=dict(background="#282828", foreground="#ebdbb2"),
)

# --- Dracula (vibrant) ------------------------------------------------------
DRACULA = Theme(
    name="dracula",
    primary="#bd93f9", success="#50fa7b", info="#8be9fd", warning="#ffb86c", danger="#ff5555",
    secondary="#ff79c6",
    neutral="#6272a4",
    light=dict(background="#f8f8f2", foreground="#282a36"),
    dark=dict(background="#282a36", foreground="#f8f8f2"),
)

# --- Tokyo Night (deep blue/purple) ----------------------------------------
TOKYO_NIGHT = Theme(
    name="tokyo-night",
    display_name="Tokyo Night",
    primary="#7aa2f7", success="#9ece6a", info="#7dcfff", warning="#e0af68", danger="#f7768e",
    secondary="#bb9af7",
    neutral="#565f89",
    light=dict(background="#e1e2e7", foreground="#343b58"),
    dark=dict(background="#1a1b26", foreground="#c0caf5"),
)

# --- One (Atom, clean neutral) ---------------------------------------------
ONE = Theme(
    name="one",
    primary="#4078f2", success="#50a14f", info="#0184bc", warning="#c18401", danger="#e45649",
    secondary="#a626a4",
    neutral="#a0a1a7",
    light=dict(background="#fafafa", foreground="#383a42"),
    dark=dict(background="#282c34", foreground="#abb2bf"),
)

# --- Everforest (green-leaning, soft) --------------------------------------
EVERFOREST = Theme(
    name="everforest",
    primary="#3a94c5", success="#8da101", info="#35a77c", warning="#dfa000", danger="#f85552",
    secondary="#df69ba",
    neutral="#939f91",
    light=dict(background="#edf3ed", foreground="#5c6a72"),
    dark=dict(background="#2d353b", foreground="#d3c6aa"),
)

#: All built-in theme families, in display order.
BUILTIN_THEMES = [
    BOOTSTRAP, PYDATA, NORD, SOLARIZED, CATPPUCCIN,
    GRUVBOX, DRACULA, TOKYO_NIGHT, ONE, EVERFOREST,
]


def install_builtin_themes() -> None:
    """Register every built-in theme variant into the theme registry (idempotent)."""
    for theme in BUILTIN_THEMES:
        theme.install()
