"""How wide is the 'click does not focus the table' behavior?

Three configurations, each arm starting from focus parked on a TextField:
  plain          — data row vs group header
  checkbox mode  — data row (this path also returns 'break')
"""
import subprocess
import bootstack as bs

BRANCH = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True, text=True).stdout.strip()

ROWS = [{"id": i, "name": n, "role": r} for i, n, r in
        [(1, "Ada", "eng"), (2, "Bob", "eng"), (3, "Cy", "ops")]]
out = []

with bs.App(title="focus scope", size=(760, 620)) as app:
    field = bs.TextField(placeholder="focus parks here")
    plain = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["id", "name", "role"], grow=1)
    checks = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["id", "name", "role"],
                          selection_mode="multi", show_selection_controls=True, grow=1)

root = app._tk_root


def park():
    field._internal.focus_set()
    root.update()
    assert root.focus_get() is not None, "PRECONDITION FAILED: nothing holds focus"


def click(table, iid):
    tree = table._internal._tree
    box = tree.bbox(iid)
    assert box, "PRECONDITION FAILED: no bbox"
    x, y = box[0] + 40, box[1] + box[3] // 2
    tree.event_generate("<Button-1>", x=x, y=y)
    tree.event_generate("<ButtonRelease-1>", x=x, y=y)
    root.update()
    return root.focus_get() is tree


def run():
    root.update(); root.update_idletasks()
    root.deiconify(); root.focus_force(); root.update()

    # plain table, grouped
    impl = plain._internal
    impl.set_grouping("role")
    root.update()
    header = list(impl._group_parents.values())[0]
    leaf = impl._tree.get_children(header)[0]

    park(); out.append(("plain: data row", click(plain, leaf)))
    park(); out.append(("plain: group header", click(plain, header)))

    # checkbox mode, ungrouped — the toggle-select path also returns 'break'
    c_leaf = checks._internal._tree.get_children("")[0]
    park(); out.append(("checkbox mode: data row", click(checks, c_leaf)))

    app.tk.after(50, app.close)


app.tk.after(400, run)
app.run()

print(f"\n=== ref: {BRANCH} ===")
for label, focused in out:
    print(f"{label:28s} table takes keyboard focus: {'yes' if focused else 'NO'}")
