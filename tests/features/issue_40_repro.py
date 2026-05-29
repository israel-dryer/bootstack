"""Reproduction for issue #40 — two bugs with AppShell window controls.

Bug 1: resizable=(False, False) + show_window_controls=True
  → clicking Maximize still zooms the window (should be a no-op / button disabled)

Bug 2: undecorated=True + show_window_controls=True
  → clicking Minimize raises TclError:
    cannot iconify ".": override-redirect flag is set
"""
from bootstack import AppShell, VStack, Label, Button, Separator


def repro_bug1():
    """resizable=False window — maximize button should be disabled/no-op."""
    with AppShell(
        title="Bug 1 — resizable=False (click Maximize)",
        size=(700, 400),
        resizable=(False, False),
        show_window_controls=True,
    ) as shell:
        with shell.add_page("home", text="Home", icon="house"):
            with VStack(padding=24, gap=8):
                Label("resizable=(False, False)", font="heading-md")
                Label("Click the maximize button — it should do nothing.")
    shell.run()


def repro_bug2():
    """undecorated=True — minimize button crashes with TclError."""
    with AppShell(
        title="Bug 2 — undecorated (click Minimize)",
        size=(700, 400),
        undecorated=True,
    ) as shell:
        with shell.add_page("home", text="Home", icon="house"):
            with VStack(padding=24, gap=8):
                Label("undecorated=True", font="heading-md")
                Label("Click the minimize (dash) button — it should crash.")
    shell.run()


if __name__ == "__main__":
    import sys
    bug = sys.argv[1] if len(sys.argv) > 1 else "1"
    if bug == "2":
        repro_bug2()
    else:
        repro_bug1()