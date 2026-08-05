"""Probe: record the PHYSICAL pixel size every icon renders at, segmented by the
widget that triggered it, at a given Tk scaling. Compare baseline vs high-DPI to
see which paths scale with DPI (crisp) and which stay literal (soft — issue #267).

Usage:
    py -3.12 development/probe_icon_sizes.py 1.334   # baseline (ui_scale 1.0)
    py -3.12 development/probe_icon_sizes.py 2.0      # 150% (ui_scale ~1.5)
"""
import sys
import bootstack as bs
from bootstack._core.images import _ImageService

current = {"label": "?"}
records: list[tuple[str, str, int]] = []
_orig = _ImageService.get_icon.__func__


def _spy(cls, name, size, color):
    records.append((current["label"], name, size))
    return _orig(cls, name, size, color)


_ImageService.get_icon = classmethod(_spy)

scaling = float(sys.argv[1]) if len(sys.argv) > 1 else 1.334

with bs.App(title="probe", scaling=scaling) as app:
    from bootstack._runtime.utility import _ScalingState
    current["label"] = "button-text"
    bs.Button("Btn", icon="house")
    current["label"] = "button-icononly"
    bs.Button(icon="gear")
    current["label"] = "textfield"
    bs.TextField(label="Field", value="x")
    current["label"] = "select"
    bs.Select(options=["a", "b"])
    current["label"] = "spinner"
    bs.SpinnerField(label="Spin")
    current["label"] = "menubutton"
    mb = bs.MenuButton("Menu")
    mb.add_item("One")
    current["label"] = "checkbox"
    bs.Checkbox("Check")

current["label"] = "public-get_icon"
from bootstack.images import get_icon as _pub_get_icon
_ = _pub_get_icon("star", size=24)._materialize()

print(f"\n=== scaling={scaling}  ui_scale={_ScalingState.get_ui_scale():.3f} ===")
agg: dict[tuple[str, str], set] = {}
for label, name, size in records:
    agg.setdefault((label, name), set()).add(size)
for (label, name) in sorted(agg):
    print(f"  {label:18} {name:20} -> {sorted(agg[(label, name)])}")
# --- rail / Workbench probe (the issue's headline) ---
current["label"] = "rail"
try:
    with bs.Workbench(title="wb", scaling=scaling) as wb:
        with wb.add_workspace("home", icon="house", text="Home"):
            bs.Label("hi")
    rail_sizes = sorted({s for (l, n, s) in records if l == "rail"})
    print(f"  rail icon sizes -> {rail_sizes}")
except Exception as e:
    print(f"  rail probe failed: {e}")
