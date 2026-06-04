"""Take light and dark screenshots of widget hero files.

Looks for a hero file in docs/screenshots/<name>.py first. If none exists,
falls back to docs/examples/<name>.py. This lets hero shots stay lean and
visually focused while the full examples carry interactive content.

Scene-aware: if a screenshots/<name>.py defines a SCENES dict, each scene is
captured separately. Scene functions must be self-contained callables that
create their own bs.App and call app.run().

Output (no scenes):  docs/_static/examples/<name>-light.png
                                            <name>-dark.png
Output (scenes):     docs/_static/examples/<name>-<scene>-light.png
                                            <name>-<scene>-dark.png

Usage:
    python docs/scripts/take_screenshots.py
    python docs/scripts/take_screenshots.py button            # single widget
    python docs/scripts/take_screenshots.py button --light    # one theme only
    python docs/scripts/take_screenshots.py button --scene hero  # one scene only
"""

from __future__ import annotations

import json
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
import os, importlib.util, sys
import bootstack as bs
from PIL import ImageGrab

theme      = os.environ["BS_THEME"]
output     = os.environ["BS_OUTPUT"]
example    = os.environ["BS_EXAMPLE"]
delay      = int(os.environ.get("BS_DELAY", "800"))
scene_name = os.environ.get("BS_SCENE", "")
probe_mode = os.environ.get("BS_PROBE", "")


def _patch(cls):
    orig_init = cls.__init__
    orig_run  = cls.run

    def _init(self, *args, **kwargs):
        settings = dict(kwargs.pop("settings", None) or {})
        settings["theme"] = theme
        orig_init(self, *args, settings=settings, **kwargs)

    def _run(self):
        def _grab():
            # If the example set app._capture_target to a Toplevel, capture
            # that window directly instead of the app (useful for dialog heroes).
            target = getattr(self, '_capture_target', None)
            if target is not None:
                target.update_idletasks()
                import re
                m = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', target.geometry())
                rx = target.winfo_rootx()
                ry = target.winfo_rooty()
                cw = target.winfo_width()
                ch = target.winfo_height()
                gy = int(m.group(4)) if m else ry
                title_h = ry - gy
                pad = 10  # breathing room outside the dialog window
                x, y = rx - pad, gy - pad
                w, h = cw + pad * 2, ch + title_h + pad * 2
                inset = 0
            else:
                x = self.tk.winfo_rootx()
                y = self.tk.winfo_rooty()
                w = self.tk.winfo_width()
                h = self.tk.winfo_height()
                inset = 2  # trim window-border artifact from captured edges
            from pathlib import Path
            from PIL import Image
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            img = ImageGrab.grab(bbox=(x + inset, y + inset, x + w - inset, y + h - inset))
            max_w = 720
            if img.width > max_w:
                ratio = max_w / img.width
                img = img.resize((max_w, max(1, int(img.height * ratio))), Image.LANCZOS)
            img.save(output)
            self.tk.destroy()

        def _capture():
            self.tk.attributes('-topmost', True)
            self.tk.lift()
            self.tk.update_idletasks()
            self.tk.after(150, _grab)

        self.tk.attributes('-topmost', True)
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

if probe_mode:
    import json
    print(json.dumps(list(getattr(mod, 'SCENES', {}).keys())))
    sys.exit(0)

if scene_name and hasattr(mod, 'SCENES') and scene_name in mod.SCENES:
    mod.SCENES[scene_name]()
# else: exec_module already ran the app (non-scene scripts)
"""


def probe_scenes(source: Path) -> list[str]:
    """Return scene names from a screenshot script, or [] if none."""
    env = {
        **os.environ,
        "BS_THEME":   "bootstrap-light",
        "BS_OUTPUT":  "",
        "BS_EXAMPLE": str(source),
        "BS_PROBE":   "1",
    }
    try:
        result = subprocess.run(
            [sys.executable, "-c", _RUNNER],
            env=env,
            timeout=10,
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout.strip()) if result.stdout.strip() else []
    except Exception:
        return []


def resolve_source(name: str) -> Path | None:
    """Return the hero file if one exists, otherwise the example file."""
    hero = SCREENSHOTS / f"{name}.py"
    if hero.exists():
        return hero
    fallback = EXAMPLES / f"{name}.py"
    return fallback if fallback.exists() else None


def run_example(example: Path, theme: str, output: Path, delay: int = 800,
                scene: str = "") -> bool:
    env = {
        **os.environ,
        "BS_THEME":   theme,
        "BS_OUTPUT":  str(output),
        "BS_EXAMPLE": str(example),
        "BS_DELAY":   str(delay),
    }
    if scene:
        env["BS_SCENE"] = scene
    result = subprocess.run(
        [sys.executable, "-c", _RUNNER],
        env=env,
        timeout=20,
        cwd=str(REPO),
    )
    return result.returncode == 0


def main():
    args = sys.argv[1:]

    filter_name  = None
    filter_scene = None
    themes       = THEMES

    for i, arg in enumerate(args):
        if arg == "--light":
            themes = [t for t in THEMES if t[0] == "light"]
        elif arg == "--dark":
            themes = [t for t in THEMES if t[0] == "dark"]
        elif arg == "--scene" and i + 1 < len(args):
            filter_scene = args[i + 1]
        elif not arg.startswith("--") and (i == 0 or args[i - 1] != "--scene"):
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

        is_hero   = source.parent == SCREENSHOTS
        tag       = "hero" if is_hero else "example"
        scenes    = probe_scenes(source) if is_hero else []

        if filter_scene and scenes:
            scenes = [s for s in scenes if s == filter_scene]

        for suffix, theme in themes:
            if scenes:
                for scene in scenes:
                    out = OUTPUT / f"{name}-{scene}-{suffix}.png"
                    label = f"{name}:{scene}"
                    print(f"  {label:28s} [{suffix:5s}] ({tag})  ", end="", flush=True)
                    try:
                        success = run_example(source, theme, out, scene=scene)
                        print(f"OK  {out.relative_to(REPO)}" if success else "FAIL  non-zero exit")
                        ok += success; failed += not success
                    except subprocess.TimeoutExpired:
                        print("FAIL  timeout"); failed += 1
                    except Exception as exc:
                        print(f"FAIL  {exc}"); failed += 1
            else:
                out = OUTPUT / f"{name}-{suffix}.png"
                print(f"  {name:28s} [{suffix:5s}] ({tag})  ", end="", flush=True)
                try:
                    success = run_example(source, theme, out)
                    print(f"OK  {out.relative_to(REPO)}" if success else "FAIL  non-zero exit")
                    ok += success; failed += not success
                except subprocess.TimeoutExpired:
                    print("FAIL  timeout"); failed += 1
                except Exception as exc:
                    print(f"FAIL  {exc}"); failed += 1

    print(f"\n{ok} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()