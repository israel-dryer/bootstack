"""Public `Theme` object for declaring and installing color themes.

A theme is a *family*: you declare the semantic accent colors once (as the
midpoint `[500]` of each ramp) plus a light and/or dark background block, and the
family generates both mode variants. Each accent expands into a 50–950 tint/shade
spectrum; the framework selects the right step per mode (a darker solid on light,
a brighter one on dark) so you never hand-write per-mode shades.

```python
from bootstack.style import Theme

Theme(
    name="bootstrap",
    primary="#0d6efd", success="#198754", danger="#dc3545",
    info="#0dcaf0", warning="#ffc107",          # the [500] anchors
    light=dict(background="#ffffff", foreground="#212529"),
    dark=dict(background="#212529",  foreground="#f8f9fa"),
).install()                                      # registers bootstrap-light + -dark

bs.set_theme("bootstrap-dark")                   # activate a generated variant
```

Installing registers the generated variants (`<name>-light` / `<name>-dark`);
activation is a separate `set_theme` call (or `install(activate=True)`). Themes
can be declared and installed at module level before an app exists — color
resolution is deferred until activation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from bootstack._core.exceptions import ThemeError
from bootstack.style.theme_provider import register_theme

ThemeMode = Literal["light", "dark"]

# Accent roles that take a `[500]` anchor and generate their own ramp.
_ACCENT_ROLES = ("primary", "success", "info", "warning", "danger")

# Which ramp step a SOLID (button fill, etc.) uses per mode. On light a darker
# step reads against white; on dark a brighter step reads against the dark
# background. `warning`/`info` stay at the bright `[500]` on light — they can't
# carry white text at any shade (they use dark on-color), so darkening them only
# mutes them.
_SOLID_STOP = {
    "light": {"primary": 600, "success": 600, "danger": 600, "info": 500, "warning": 500},
    "dark":  {"primary": 400, "success": 400, "danger": 400, "info": 400, "warning": 400},
}
# Neutral (gray) step used for the `secondary` role per mode.
_SECONDARY_STOP = {"light": 700, "dark": 400}


def _default_display_name(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


@dataclass
class Theme:
    """A color theme family declared in code.

    Declare the semantic accent colors as `[500]` anchors plus a `light` and/or
    `dark` block (`background`/`foreground`). Each accent generates a 50–950
    ramp; the framework picks the per-mode step for solids, washes, borders, and
    emphasis text. `install()` registers the generated `<name>-light` and
    `<name>-dark` variants.

    Args:
        name: Family name; generated variants are `<name>-light` / `<name>-dark`.
        primary: Primary accent color (the `[500]` ramp midpoint), as hex.
        success: Success accent color (hex).
        info: Info accent color (hex).
        warning: Warning accent color (hex).
        danger: Danger accent color (hex).
        secondary: Optional colored secondary accent (hex). When omitted,
            `secondary` derives from the neutral ramp.
        neutral: Gray base for the neutral ramp (borders, muted text, secondary).
        light: `{'background': ..., 'foreground': ...}` for the light variant, or
            None to skip it.
        dark: `{'background': ..., 'foreground': ...}` for the dark variant.
        surfaces: Optional surface overrides — either a flat
            `{'chrome': '#...'}` (both modes) or per-mode
            `{'light': {...}, 'dark': {...}}`. Pins surfaces the auto-derivation
            can't produce well (e.g. chrome on a very-dark background).
        display_name: Human label base; the mode is appended (` Light`/` Dark`).
        white: Reference white. Defaults to `'#ffffff'`.
        black: Reference black. Defaults to `'#000000'`.
    """

    name: str

    primary: str | None = None
    success: str | None = None
    info: str | None = None
    warning: str | None = None
    danger: str | None = None
    secondary: str | None = None

    neutral: str = "#adb5bd"

    light: dict[str, str] | None = None
    dark: dict[str, str] | None = None

    surfaces: dict | None = None
    display_name: str | None = None
    white: str = "#ffffff"
    black: str = "#000000"

    def _schema(self, mode: ThemeMode) -> dict | None:
        block = self.light if mode == "light" else self.dark
        if block is None:
            return None
        if "background" not in block or "foreground" not in block:
            raise ThemeError(
                f"Theme '{self.name}' {mode} block must define both "
                f"'background' and 'foreground'."
            )

        solid = _SOLID_STOP[mode]
        shades: dict[str, str] = {"gray": self.neutral}
        semantic: dict[str, str] = {}

        for role in _ACCENT_ROLES:
            anchor = getattr(self, role)
            if anchor:
                shades[role] = anchor
                semantic[role] = f"{role}[{solid[role]}]"

        if self.secondary:
            shades["secondary"] = self.secondary
            semantic["secondary"] = f"secondary[{solid['primary']}]"
        else:
            semantic["secondary"] = f"gray[{_SECONDARY_STOP[mode]}]"

        base_label = self.display_name or _default_display_name(self.name)
        schema: dict = {
            "name": f"{self.name}-{mode}",
            "display_name": f"{base_label} {mode.title()}",
            "mode": mode,
            "foreground": block["foreground"],
            "background": block["background"],
            "white": self.white,
            "black": self.black,
            "shades": shades,
            "semantic": semantic,
        }
        if self.surfaces:
            override = self.surfaces.get(mode, None)
            if override is None and not ({"light", "dark"} & set(self.surfaces)):
                override = self.surfaces  # flat dict → applies to both modes
            if override:
                schema["surfaces"] = dict(override)
        return schema

    def variants(self) -> list[dict]:
        """Return the generated per-mode schema dicts (light first, then dark)."""
        return [s for s in (self._schema("light"), self._schema("dark")) if s]

    def install(self, *, activate: bool | str = False) -> Theme:
        """Register the generated variants so they can be activated by name.

        Args:
            activate: True activates the light variant; pass a variant name
                (e.g. `'bootstrap-dark'`) to activate that one.

        Returns:
            This theme, to allow `theme = Theme(...).install()`.
        """
        schemas = self.variants()
        if not schemas:
            raise ThemeError(
                f"Theme '{self.name}' defines neither a 'light' nor a 'dark' block."
            )
        for schema in schemas:
            register_theme(schema["name"], schema)
        if activate:
            from bootstack.style.style import set_theme
            target = activate if isinstance(activate, str) else schemas[0]["name"]
            set_theme(target)
        return self

    def __repr__(self) -> str:
        modes = "+".join(m for m, b in (("light", self.light), ("dark", self.dark)) if b)
        return f"<Theme {self.name} ({modes or 'empty'})>"
