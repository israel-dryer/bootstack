"""A page builder in its own file, marked for per-page hot reload.

Edit anything in `build_dashboard` and save — because it's `@reloadable`, only
this region rebuilds in the running app (the entry file's body is not re-run).

Rule the marker imposes (good practice anyway): a page file is a pure VIEW
builder over shared state. Durable state (signals, datasources) lives in the
entry module and is passed in — not declared here, since editing this file
re-runs its top level.
"""
import bootstack as bs
from bootstack.dev import reloadable


@reloadable
def build_dashboard(clicks):
    bs.Label("Dashboard", font="heading-lg")
    bs.Label("Edit hot_reload_page.py and save — only this card rebuilds.")
    bs.Label(textsignal=clicks.map(lambda n: f"Shared clicks: {n}"))
