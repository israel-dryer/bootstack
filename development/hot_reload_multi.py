"""Multi-file hot reload with @reloadable.

Run it live:   bootstack dev development/hot_reload_multi.py

- Edit THIS file (the entry) and save  -> the whole body reloads.
- Edit hot_reload_page.py and save      -> ONLY the dashboard card rebuilds
  (per-page reload), and the running app's other widgets are untouched.

Note the import style: `import hot_reload_page as page` (import the MODULE),
not `from hot_reload_page import build_dashboard`. Importing the module is
reload-safe — attribute lookup always finds the freshly-reloaded builder; a
`from ... import name` would pin the stale function.
"""
import bootstack as bs

import hot_reload_page as page

clicks = bs.Signal(0)  # module-level shared state -> survives reloads, passed to the page

with bs.App(title="Multi-file Hot Reload", padding=24, gap=12) as app:
    bs.Label("Entry file owns the app + shared state.", font="heading-md")

    with bs.Card(padding=16, gap=8):
        page.build_dashboard(clicks)

    bs.Button("Click", accent="primary", on_click=lambda: clicks.set(clicks() + 1))

app.run()
