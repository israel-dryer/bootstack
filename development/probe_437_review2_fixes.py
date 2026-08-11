"""Controls for the round-2 review findings on #437/#438.

Three questions the fixes rest on, measured rather than assumed. All arms are
pure Tk plus bootstack's own dialog classes, so this runs on every box (the
#430 rule: a probe must be runnable everywhere it is meant to inform).

    py -3.12 development/probe_437_review2_fixes.py

Arm 1 (F6) - does Tk release a grab when the grabbing window is destroyed?
    The range-confirm path in `datedialog.py` hands the close to `Dialog`,
    which destroys without calling `grab_release()`, while `_confirm` still
    calls it. If Tk does not release on destroy, that difference is a bug on
    X11, where a stuck keyboard grab freezes input to a dead window.

Arm 2 (F4) - is `query.py`'s `<Return>` binding on the composite frame
    reachable? The review says focus lands on the inner entry widget and Tk
    does not bubble child -> parent, so the handler can never fire. Deleting
    live code would be a regression; deleting dead code is not.

Arm 3 (F4, cross-platform) - does the keypad Enter key activate a dialog's
    default button? `KP_Enter` is a distinct keysym from `Return` on Windows,
    X11 and Aqua alike, so a binding on `<Return>` alone does not cover it.
"""
from __future__ import annotations

import tkinter

import bootstack as bs


def arm_1_grab_release_on_destroy(root: tkinter.Misc) -> None:
    print("arm 1: does destroying a grabbing window release the grab?")
    top = tkinter.Toplevel(root)
    top.geometry("120x60+100+100")
    top.deiconify()
    root.update()
    try:
        top.grab_set()
    except tkinter.TclError as exc:
        print("  SKIP: grab_set failed on this display: %s" % exc)
        top.destroy()
        return
    held = top.grab_current()
    print("  grab held by the toplevel before destroy = %s" % (held is top))
    top.destroy()
    root.update()
    after = root.grab_current()
    print("  grab_current() after destroy            = %r" % (after,))
    print("  -> Tk releases on destroy               = %s" % (after in (None, "")))


def arm_2_query_return_binding(root: tkinter.Misc) -> None:
    print("arm 2: can query.py's <Return> binding on the composite frame fire?")
    from bootstack.dialogs._impl.query import QueryDialog

    dialog = QueryDialog("Name:", master=root)
    dialog._dialog._create_toplevel(modal=False)
    dialog._dialog._build_content()
    root.update_idletasks()

    entry = dialog._entry_widget
    inner = getattr(entry, "entry_widget", None)
    print("  the composite exposes .entry_widget      = %s" % (inner is not None))
    if inner is None:
        print("  SKIP: no inner entry, so the frame itself would take focus")
        dialog._dialog.toplevel.destroy()
        return

    tags = [str(t) for t in inner.bindtags()]
    frame_path = str(entry)
    print("  focus target                             = %s" % inner.winfo_class())
    print("  its bindtags                             = %s" % tags)
    print("  the composite's own path is in them      = %s" % (frame_path in tags))
    print("  -> the frame's <Return> binding is dead  = %s" % (frame_path not in tags))
    dialog._dialog.toplevel.destroy()


def arm_3_keypad_enter(root: tkinter.Misc) -> None:
    print("arm 3: does the keypad Enter key press a dialog's default button?")
    from bootstack.dialogs import Dialog, DialogButton

    presses: list[str] = []

    def record(dlg):
        presses.append("ok")
        # Refuse the press so the dialog stays open and both keys can be tried
        # against one window. Doubles as a check that the #437 veto holds.
        return False

    dialog = Dialog(
        title="probe",
        content_builder=lambda: bs.Label("body"),
        buttons=[DialogButton(text="OK", role="primary", default=True,
                              command=record)],
        parent=root,
    )
    dialog._create_toplevel(modal=False)
    dialog._build_content()
    dialog._build_footer()
    top = dialog.toplevel
    top.geometry("200x120+120+120")
    top.deiconify()
    root.update()

    bound = [str(s) for s in top.bind()]
    print("  sequences bound on the toplevel          = %s" % bound)
    for seq in ("<Return>", "<KP_Enter>"):
        before = len(presses)
        try:
            top.event_generate(seq, when="now")
        except tkinter.TclError as exc:
            print("  %-12s could not be synthesized: %s" % (seq, exc))
            continue
        root.update()
        print("  %-12s pressed the default button = %s" % (seq, len(presses) > before))
    top.destroy()


if __name__ == "__main__":
    app = bs.App(title="probe 437 review 2")
    root = app._tk_root
    root.geometry("300x120+40+40")
    root.update()

    arm_1_grab_release_on_destroy(root)
    print()
    arm_2_query_return_binding(root)
    print()
    arm_3_keypad_enter(root)

    root.destroy()
