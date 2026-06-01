"""Take light and dark screenshots of widget hero files.

Looks for a hero file in docs/screenshots/<name>.py first. If none exists,
falls back to docs/examples/<name>.py. This lets hero shots stay lean and
visually focused while the full examples carry interactive content.

Output: docs/_static/examples/<name>-light.png
                               <name>-dark.png

Usage:
    python docs/scripts/take_screenshots.py
    python docs/scripts/take_screenshots.py button          # single widget
    python docs/scripts/take_screenshots.py button --light  # one theme only
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO        = Path(__file__).parent.parent.parent
SCREENSHOTS = REPO / "docs" / "screenshots"
EXAMPLES    = REPO / "docs" / "examples"
OUTPUT      = REPO / "docs" / "_static" / "examples"

THEMES = [
    ("light", "bootstrap-light"),
    ("dark",  "bootstrap-dark"),
]

# Injected into each subprocess via python -c
_RUNNER = r"""
import os, importlib.util
import bootstack as bs
from PIL import ImageGrab

theme   = os.environ["BS_THEME"]
output  = os.environ["BS_OUTPUT"]
example = os.environ["BS_EXAMPLE"]
delay   = int(os.environ.get("BS_DELAY", "800"))


def _patch(cls):
    orig_init = cls.__init__
    orig_run  = cls.run

    def _init(self, *args, **kwargs):
        settings = dict(kwargs.pop("settings", None) or {})
        settings["theme"] = theme
        orig_init(self, *args, settings=settings, **kwargs)

    def _run(self):
        def _grab():
            x = self.tk.winfo_rootx()
            y = self.tk.winfo_rooty()
            w = self.tk.winfo_width()
            h = self.tk.winfo_height()
            from pathlib import Path
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            inset = 2  # trim window-border artifact from captured edges
            ImageGrab.grab(bbox=(x + inset, y + inset, x + w - inset, y + h - inset)).save(output)
            self.tk.destroy()

        def _capture():
            self.tk.attributes('-topmost', True)
            self.tk.lift()
            self.tk.update_idletasks()
            self.tk.after(150, _grab)

        # Position on the primary monitor at startup — moving the window at
        self.tk.attributes('-topmost', True)
        # Schedule geometry and focus after the mainloop starts — the App's
        # __exit__ shows the window after orig_run() begins, so geometry set
        # before orig_run() gets overridden by the WM.
        self.tk.after(0,  lambda: self.tk.geometry('+200+100'))
        self.tk.after(50, self.tk.focus_force)
        self.tk.after(delay, _capture)
        orig_run(self)

    cls.__init__ = _init
    cls.run      = _run


_patch(bs.App)
_patch(bs.AppShell)

spec = importlib.util.spec_from_file_location("_example", example)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
"""


def resolve_source(name: str) -> Path | None:
    """Return the hero file if one exists, otherwise the example file."""
    hero = SCREENSHOTS / f"{name}.py"
    if hero.exists():
        return hero
    fallback = EXAMPLES / f"{name}.py"
    return fallback if fallback.exists() else None


def run_example(example: Path, theme: str, output: Path, delay: int = 800):
    env = {
        **os.environ,
        "BS_THEME":   theme,
        "BS_OUTPUT":  str(output),
        "BS_EXAMPLE": str(example),
        "BS_DELAY":   str(delay),
    }
    result = subprocess.run(
        [sys.executable, "-c", _RUNNER],
        env=env,
        timeout=15,
        cwd=str(REPO),
    )
    return result.returncode == 0


def main():
    args = sys.argv[1:]

    filter_name = None
    themes = THEMES
    for arg in args:
        if arg == "--light":
            themes = [t for t in THEMES if t[0] == "light"]
        elif arg == "--dark":
            themes = [t for t in THEMES if t[0] == "dark"]
        elif not arg.startswith("--"):
            filter_name = arg

    # Collect widget names from both directories, deduplicated
    names = sorted({p.stem for p in list(SCREENSHOTS.glob("*.py")) + list(EXAMPLES.glob("*.py"))})
    if filter_name:
        names = [n for n in names if n == filter_name]

    if not names:
        print(f"No examples found{f' matching {filter_name!r}' if filter_name else ''}.")
        sys.exit(1)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    ok = failed = 0
    for name in names:
        source = resolve_source(name)
        if source is None:
            continue
        tag = "hero" if source.parent == SCREENSHOTS else "example"
        for suffix, theme in themes:
            out = OUTPUT / f"{name}-{suffix}.png"
            print(f"  {name:20s} [{suffix:5s}] ({tag})  ", end="", flush=True)
            try:
                success = run_example(source, theme, out)
                if success:
                    print(f"OK  {out.relative_to(REPO)}")
                    ok += 1
                else:
                    print("FAIL  non-zero exit")
                    failed += 1
            except subprocess.TimeoutExpired:
                print("FAIL  timeout")
                failed += 1
            except Exception as exc:
                print(f"FAIL  {exc}")
                failed += 1

    print(f"\n{ok} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()
