"""Control for the #441 test barrier - is the dialog BODY on screen yet?

`test_dialog_enter_key.py` drives a real dialog and presses Enter inside its
body. It waits for the modal grab AND every footer button to be mapped, which
is the barrier `test_dialog_press_contract.py` established. That barrier is not
enough for a test that touches the BODY: the footer and the content are mapped
by separate geometry passes, so the body widget can still be unmapped when
every footer button is up.

The consequences are silent and look exactly like the bug under test. An
unmapped widget cannot take focus, and Tk reports nothing when `focus_set()`
fails on one - `TkSetFocusWin` walks the ancestry and returns. So the key press
goes to whatever DOES hold focus, which is the toplevel, the toplevel's binding
fires the default button, and the dialog closes. A test asserting "the dialog
did not close" then fails, having produced the failure itself. It failed about
2 runs in 5.

⚠ RE-RUNNING A FIXED TEST DOES NOT PROVE THE FIX. That is the lesson from
`probe_437_focus_flake.py`, which this mirrors: the control has to CREATE the
condition rather than wait for it. Arm 1 leaves idle geometry work outstanding
when the dialog goes up - packed-but-not-yet-updated widgets - and counts how
often each barrier's "ready" claim is wrong about the body.

Expected: the footer-only barrier reports ready while the body is unmapped a
good fraction of the time; the footer+body barrier never does.

Run:  py -3.13 development/probe_441_body_barrier.py
"""

from __future__ import annotations

import sys

import bootstack as bs
from bootstack.dialogs._impl.dialog import Dialog, DialogButton

ROUNDS = 12


def _descend(widget, klass):
    if widget.winfo_class() == klass:
        return widget
    for child in widget.winfo_children():
        found = _descend(child, klass)
        if found is not None:
            return found
    return None


def _run(root, *, wait_for_body: bool, rounds: int = ROUNDS) -> dict:
    """Open `rounds` dialogs; count how often the body is unmapped when ready."""
    stats = {"unmapped_at_ready": 0, "focus_missed": 0, "rounds": 0}

    for _ in range(rounds):
        holder: dict = {}

        def build():
            holder["body"] = bs.TextArea(height=3)
            # Leave idle geometry work outstanding, the way a real dialog body
            # does while it is still being laid out. Without this the process
            # is too quiet to reproduce anything.
            for _i in range(6):
                bs.Label("filler")

        dialog = Dialog(
            title="barrier",
            content_builder=build,
            buttons=[DialogButton(text="OK", role="primary", result="ok",
                                  default=True)],
            parent=root,
        )

        def leaf():
            body = holder.get("body")
            if body is None:
                return None
            return _descend(body._internal, "Text")

        def footer_up() -> bool:
            footer = getattr(dialog, "_footer", None)
            if footer is None or not footer.winfo_exists():
                return False
            kids = footer.winfo_children()
            return bool(kids) and all(k.winfo_ismapped() for k in kids)

        def ready() -> bool:
            top = dialog._toplevel
            if top is None or not top.winfo_exists():
                return False
            if top.grab_current() is not top or not footer_up():
                return False
            if wait_for_body:
                node = leaf()
                return node is not None and node.winfo_ismapped()
            return True

        def poll(attempt=0):
            if not ready():
                if attempt < 200:
                    root.after(20, lambda: poll(attempt + 1))
                return
            top = dialog._toplevel
            try:
                node = leaf()
                stats["rounds"] += 1
                if node is None or not node.winfo_ismapped():
                    stats["unmapped_at_ready"] += 1
                    # A focus request on an unmapped widget is discarded
                    # silently; record that it is, since that is the half that
                    # actually breaks the test.
                    if node is not None:
                        node.focus_set()
                        if str(top.tk.call("focus") or "") != str(node):
                            stats["focus_missed"] += 1
                else:
                    node.focus_set()
                    if str(top.tk.call("focus") or "") != str(node):
                        stats["focus_missed"] += 1
            finally:
                if top is not None and top.winfo_exists():
                    top.destroy()

        root.after(10, poll)
        dialog.show()

    return stats


if __name__ == "__main__":
    app = bs.App(title="probe_441_barrier")
    root = app._tk_root
    root.geometry("420x320+120+120")
    root.deiconify()
    root.update()

    old = _run(root, wait_for_body=False)
    new = _run(root, wait_for_body=True)

    print("MEASURED - was the dialog body actually on screen when the")
    print("           barrier said the dialog was ready?\n")
    for label, s in (("footer only (the old barrier)", old),
                     ("footer + body (the fix)", new)):
        print(f"  {label}")
        print(f"      dialogs driven            {s['rounds']}")
        print(f"      body UNMAPPED at ready    {s['unmapped_at_ready']}")
        print(f"      focus_set() silently lost {s['focus_missed']}")
        print()

    print("=" * 66)
    failures = []
    if new["unmapped_at_ready"] or new["focus_missed"]:
        failures.append(
            f"the new barrier still let {new['unmapped_at_ready']} unmapped "
            f"bodies through ({new['focus_missed']} lost focus)"
        )
    if not old["unmapped_at_ready"]:
        failures.append(
            "the OLD barrier never reproduced the condition in this run, so "
            "this probe did not demonstrate anything - raise ROUNDS or add "
            "more outstanding geometry work before trusting the new column"
        )

    if failures:
        print(f"INCONCLUSIVE / FAIL ({len(failures)})")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("PASS - the old barrier reproduces the unmapped body and the new one")
    print("       never does, so the fix addresses the mechanism, not the odds.")
