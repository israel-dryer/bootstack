"""Probe for the #417 review — is `context_menus` reachable on the PUBLIC DataTable?

The prior session concluded that the identical gated-binding shape behind
`on_row_right_click` (bound only when `context_menus != "none"`) is unreachable
from public API, so nothing was filed. But `docs/widgets/datatable.rst:566`
documents `context_menus` as a `bs.DataTable` argument, and it is absent from
`src/bootstack/widgets/datatable.py`. Only one of those can be right.

Measures, in order:
  1. does `bs.DataTable(context_menus=...)` construct at all, or raise?
  2. if it constructs, did the value REACH the impl (`_context_menus`) or get
     swallowed into layout kwargs and silently dropped?
  3. with `context_menus="none"`, is a right-click binding present on the tree?

Control: the same three readings for the default table, which must show
`_context_menus == 'all'` and a live right-click binding — otherwise a "no
binding" result would just mean the probe is looking in the wrong place.

Run: py -3.13 development/probe_417_context_menus_reachable.py
"""

import bootstack as bs

COLUMNS = [{"text": "Name", "key": "name", "width": 140}]
ROWS = [{"name": "Ada"}, {"name": "Alan"}]


def _right_click_bindings(tree):
    """Sequences on the tree that a right-click would match (Win/Linux Button-3)."""
    return [b for b in tree.bind() if "Button-3" in b or "Button-2" in b]


def run(label, **table_kwargs):
    constructed, err = True, None
    try:
        with bs.App(title=f"#417 ctx {label}", size=(520, 260), padding=8) as app:
            table = bs.DataTable(columns=COLUMNS, rows=ROWS, **table_kwargs)
    except Exception as exc:
        constructed, err = False, f"{type(exc).__name__}: {exc}"
        print(f"  {label}\n    constructed .............. False ({err})", flush=True)
        return None

    impl = table._internal
    root = app.tk
    root.deiconify()
    root.update()

    reached = getattr(impl, "_context_menus", "<missing>")
    binds = _right_click_bindings(impl._tree)

    print(f"  {label}", flush=True)
    print(f"    constructed .............. {constructed}", flush=True)
    print(f"    impl._context_menus ...... {reached!r}", flush=True)
    print(f"    right-click bindings ..... {binds}", flush=True)

    root.destroy()
    return reached, binds


print(f"bootstack {bs.__version__}\n", flush=True)
print("CONTROL — default table (must be 'all' with a live binding):", flush=True)
ctl = run("default")
print(flush=True)
print("CASE — the documented spelling, context_menus='none':", flush=True)
case = run("context_menus='none'", context_menus="none")

print("\n" + "=" * 62, flush=True)
if ctl and case:
    print(f"control has a right-click binding ............. {bool(ctl[1])}", flush=True)
    print(f"the kwarg REACHED the impl .................... {case[0] == 'none'}", flush=True)
    print(f"...and it silenced the right-click binding .... {not case[1]}", flush=True)
    if case[0] == ctl[0]:
        print("the kwarg was SILENTLY SWALLOWED (impl unchanged)", flush=True)
