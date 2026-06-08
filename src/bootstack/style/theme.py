"""Public `Theme` object for declaring and installing color themes.

A theme is declared in code with the keyword constructor and installed so it
can be activated by name:

```python
from bootstack.style import Theme

amber_dark = Theme(
    name="amber-dark",
    display_name="Amber Dark",
    mode="dark",
    base="dark",                      # inherit shades/surfaces, override the rest
    foreground="#f8f9fa",
    background="#18130a",
    shades={"orange": "#fd7e14"},     # only what differs from the base
    semantic={"primary": "orange[400]", "secondary": "yellow[400]"},
)
amber_dark.install()                  # register it
bs.set_theme("amber-dark")            # activate it
```

Installing only registers the theme; activation is a separate `set_theme` call
(or `install(activate=True)`). A theme can be declared and installed at module
level before an app exists — color resolution is deferred until activation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from bootstack._core.exceptions import ThemeError
from bootstack.style.theme_provider import get_theme, register_theme

ThemeMode = Literal["light", "dark"]


def _default_display_name(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


@dataclass
class Theme:
    """A color theme declared in code.

    Colors are described with a small set of base `shades` (named hues) plus
    `semantic` roles that reference a step within a shade's generated spectrum,
    e.g. `'orange[400]'`. Each shade automatically expands into a 50–950 tint/
    shade spectrum at activation time.

    Set `base` to inherit every field from an existing theme (e.g. `'dark'`,
    `'bootstrap-light'`) and override only the keys that differ. `shades` and
    `semantic` are merged with the base per key; scalar fields fall back to the
    base when omitted, and `mode` is inherited from the base when not given.    """

    name: str
    """Canonical theme name used by `set_theme` (e.g. `'amber-dark'`)."""

    mode: ThemeMode | None = None
    """Color mode, `'light'` or `'dark'`. Inherited from `base` when omitted;
    defaults to `'light'` if there is no base."""

    display_name: str | None = None
    """Human-friendly label shown in theme pickers. Derived from `name` when
    omitted."""

    base: str | None = None
    """Name of an installed theme to inherit from, or None for a fully
    self-contained theme."""

    foreground: str | None = None
    """Default text color (hex). Required when there is no `base`."""

    background: str | None = None
    """Main surface color (hex). Required when there is no `base`."""

    white: str | None = None
    """Reference white (hex). Defaults to `'#ffffff'`."""

    black: str | None = None
    """Reference black (hex). Defaults to `'#000000'`."""

    shades: dict[str, str] = field(default_factory=dict)
    """Mapping of base hue name to hex color, e.g. `{'orange': '#fd7e14'}`.
    Merged onto the base's shades."""

    semantic: dict[str, str] = field(default_factory=dict)
    """Mapping of semantic role to a shade-spectrum token, e.g.
    `{'primary': 'orange[400]'}`. Merged onto the base's semantic roles."""

    @classmethod
    def from_dict(cls, data: dict) -> Theme:
        """Build a `Theme` from a plain dict using the theme schema keys.

        Args:
            data: Mapping with `name` and any of the theme fields
                (`mode`, `display_name`, `base`, `foreground`, `background`,
                `white`, `black`, `shades`, `semantic`).
        """
        try:
            name = data["name"]
        except KeyError:
            raise ThemeError("Theme dict is missing the required 'name' key.")
        return cls(
            name=name,
            mode=data.get("mode"),
            display_name=data.get("display_name"),
            base=data.get("base"),
            foreground=data.get("foreground"),
            background=data.get("background"),
            white=data.get("white"),
            black=data.get("black"),
            shades=dict(data.get("shades") or {}),
            semantic=dict(data.get("semantic") or {}),
        )

    def to_dict(self) -> dict:
        """Return the fully resolved theme as a schema dict (base merged in)."""
        return self._resolve()

    def _resolve(self) -> dict:
        if self.base is not None:
            base_data = get_theme(self.base)
            mode = self.mode or base_data.get("mode") or "light"
            return {
                "name": self.name,
                "display_name": (
                    self.display_name
                    or base_data.get("display_name")
                    or _default_display_name(self.name)
                ),
                "mode": mode,
                "foreground": (
                    self.foreground if self.foreground is not None
                    else base_data.get("foreground")
                ),
                "background": (
                    self.background if self.background is not None
                    else base_data.get("background")
                ),
                "white": (
                    self.white if self.white is not None
                    else base_data.get("white", "#ffffff")
                ),
                "black": (
                    self.black if self.black is not None
                    else base_data.get("black", "#000000")
                ),
                "shades": {**(base_data.get("shades") or {}), **self.shades},
                "semantic": {**(base_data.get("semantic") or {}), **self.semantic},
            }

        if self.foreground is None or self.background is None:
            raise ThemeError(
                f"Theme '{self.name}' has no base, so it must define both "
                f"'foreground' and 'background'."
            )
        return {
            "name": self.name,
            "display_name": self.display_name or _default_display_name(self.name),
            "mode": self.mode or "light",
            "foreground": self.foreground,
            "background": self.background,
            "white": self.white if self.white is not None else "#ffffff",
            "black": self.black if self.black is not None else "#000000",
            "shades": dict(self.shades),
            "semantic": dict(self.semantic),
        }

    def install(self, *, activate: bool = False) -> Theme:
        """Register the theme so it can be activated by name.

        Args:
            activate: When True, also make this the active theme immediately
                (equivalent to calling `set_theme(name)` afterward).

        Returns:
            This theme, to allow `theme = Theme(...).install()`.
        """
        register_theme(self.name, self._resolve())
        if activate:
            from bootstack.style.style import set_theme
            set_theme(self.name)
        return self

    def __repr__(self) -> str:
        base = f" base={self.base}" if self.base else ""
        return f"<Theme name={self.name} mode={self.mode or '?'}{base}>"