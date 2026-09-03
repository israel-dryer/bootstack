"""Probe #507 -- does an undecorated shell get a Windows taskbar button?

Windows decides taskbar membership when a window FIRST BECOMES VISIBLE. Tk gives
an override-redirect window WS_EX_TOOLWINDOW, and a window mapped as a toolwindow
gets no button -- clearing the flag afterwards does not create one. So the only
measurement that means anything is the extended style at the first map; the style
read after startup is identical in all arms and tells you nothing.

Arms:
    app            bs.App(undecorated=True) -- the reference that always worked
    shell          bs.AppShell(undecorated=True) through its own run()
                   -- reflects WHATEVER YOUR TREE DOES
    shell-shipped  the same AppShell with deiconify() before mainloop() staged
                   BY HAND -- the pre-fix ordering, reproduced whether or not
                   appshell.py:707 is still there
    shell-fixed    the same AppShell with no early deiconify, staged by hand

⚠ THE TWO STAGED ARMS DO NOT READ THE SOURCE, AND THAT IS THE POINT. Once the
fix lands, an arm that merely calls run() passes, so a probe built only from
`shell` stops discriminating and reads as "cannot reproduce". `shell-shipped`
keeps the defect available for comparison; `shell` is the verification.

Usage:
    py -3.13 development/probe_507_undecorated_taskbar.py <arm> [decorated]

Pass `decorated` to run the arm with undecorated=False, which is the control
showing the defect is specific to the borderless path.

Windows only. Every other platform skips with a message rather than failing.
"""

import sys
import tkinter

ARMS = ("app", "shell", "shell-shipped", "shell-fixed")

if sys.platform != "win32":
    print("SKIP: WS_EX_TOOLWINDOW and the taskbar are Windows concepts.")
    print("      This probe measures nothing on %s." % sys.platform)
    raise SystemExit(0)

from ctypes import windll  # noqa: E402

import bootstack as bs  # noqa: E402

user32 = windll.user32
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

# Filled by the deiconify hook the first time the window actually becomes
# visible. Stays empty if the window never mapped -- see the guard in report().
first_map = {}


def toplevel_hwnd(widget):
    """The wrapper HWND Windows manages, not Tk's child window."""
    child = widget.winfo_id()
    return user32.GetParent(child) or child


def install_first_map_hook():
    """Record the extended style at the instant the window first becomes visible."""
    original = tkinter.Wm.deiconify

    def deiconify(self, *args, **kwargs):
        try:
            hwnd = toplevel_hwnd(self)
            was_visible = bool(user32.IsWindowVisible(hwnd))
        except Exception:
            return original(self, *args, **kwargs)
        result = original(self, *args, **kwargs)
        if not was_visible and user32.IsWindowVisible(hwnd) and not first_map:
            first_map["hwnd"] = hwnd
            first_map["exstyle"] = user32.GetWindowLongW(hwnd, GWL_EXSTYLE) & 0xFFFFFFFF
        return result

    tkinter.Wm.deiconify = deiconify


def report(arm, undecorated, root):
    if not first_map:
        # A window that never mapped yields no measurement. Saying so is the
        # point: a silent "no button" here would read as a reproduction.
        print("INCONCLUSIVE: the window never became visible -- nothing was measured.")
        root.destroy()
        return
    hwnd = first_map["hwnd"]
    at_map = first_map["exstyle"]
    now = user32.GetWindowLongW(hwnd, GWL_EXSTYLE) & 0xFFFFFFFF
    tool_at_map = bool(at_map & WS_EX_TOOLWINDOW)

    print("arm            : %s (undecorated=%s)" % (arm, undecorated))
    print("hwnd           : %s" % hex(hwnd))
    print("ex AT FIRST MAP: 0x%08X  TOOLWINDOW=%-5s APPWINDOW=%s"
          % (at_map, tool_at_map, bool(at_map & WS_EX_APPWINDOW)))
    print("ex NOW         : 0x%08X  TOOLWINDOW=%-5s APPWINDOW=%s"
          % (now, bool(now & WS_EX_TOOLWINDOW), bool(now & WS_EX_APPWINDOW)))
    print("TASKBAR BUTTON : %s" % ("NO -- mapped as a toolwindow" if tool_at_map else "yes"))
    if tool_at_map and not (now & WS_EX_TOOLWINDOW):
        print()
        print("READING: the flag was cleared AFTER the window was already visible.")
        print("         Windows does not re-read the style on a mapped window, so")
        print("         the late correction buys nothing. Compare 'ex NOW' across")
        print("         arms and it is identical -- that is why only the first-map")
        print("         value discriminates.")
    sys.stdout.flush()
    root.destroy()


def build_app(undecorated):
    with bs.App(title="Probe 507", undecorated=undecorated) as app:
        bs.Label("Hello World!")
        bs.Button("Click Me")
    return app, app.tk


def build_shell(undecorated):
    with bs.AppShell(title="Probe 507", undecorated=undecorated) as shell:
        with shell.add_toolbar(show_window_controls=True) as titlebar:
            titlebar.add_label("Probe 507", icon="stack", font="caption")
            titlebar.add_spacer()
            titlebar.add_theme_toggle()
        with shell.page_nav() as nav:
            with nav.add_page("home", text="Home", icon="house", padding=24, gap=12):
                bs.Label("Hello World!")
                bs.Button("Click Me")
    return shell, shell.tk


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else ""
    if arm not in ARMS:
        print("usage: probe_507_undecorated_taskbar.py {%s} [decorated]" % "|".join(ARMS))
        raise SystemExit(2)
    undecorated = "decorated" not in sys.argv[2:]

    install_first_map_hook()
    builder = build_app if arm == "app" else build_shell
    handle, root = builder(undecorated)
    root.after(900, lambda: report(arm, undecorated, root))

    if arm in ("app", "shell"):
        # The real entry point -- this arm says what THIS TREE does.
        handle.run()
        return
    # Both staged arms replicate run()'s body, so they keep their meaning no
    # matter what the source says. The deiconify is the only difference: it maps
    # the window while it is still a toolwindow, which is the whole defect.
    handle._ensure_default_titlebar()
    if arm == "shell-shipped":
        handle._internal.deiconify()
    handle._internal.mainloop()


main()
