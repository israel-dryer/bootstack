"""Take light and dark screenshots of every example in docs/examples/.

Runs each example in a subprocess with a monkey-patched bs.App/bs.AppShell
that forces the theme, waits for the window to render, captures it, saves
the image, then quits.

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

REPO     = Path(__file__).parent.parent.parent
EXAMPLES = REPO / "docs" / "examples"
OUTPUT   = REPO / "docs" / "_static" / "examples"

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
        def _capture():
            self.tk.update_idletasks()
            x = self.tk.winfo_rootx()
            y = self.tk.winfo_rooty()
            w = self.tk.winfo_width()
            h = self.tk.winfo_height()
            from pathlib import Path
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(output)
            self.tk.destroy()

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

    # Filter by widget name if provided
    filter_name = None
    themes = THEMES
    for arg in args:
        if arg == "--light":
            themes = [t for t in THEMES if t[0] == "light"]
        elif arg == "--dark":
            themes = [t for t in THEMES if t[0] == "dark"]
        elif not arg.startswith("--"):
            filter_name = arg

    examples = sorted(EXAMPLES.glob("*.py"))
    if filter_name:
        examples = [e for e in examples if e.stem == filter_name]

    if not examples:
        print(f"No examples found{f' matching {filter_name!r}' if filter_name else ''}.")
        sys.exit(1)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    ok = failed = 0
    for example in examples:
        name = example.stem
        for suffix, theme in themes:
            out = OUTPUT / f"{name}-{suffix}.png"
            print(f"  {name:20s} [{suffix:5s}]  ", end="", flush=True)
            try:
                success = run_example(example, theme, out)
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
