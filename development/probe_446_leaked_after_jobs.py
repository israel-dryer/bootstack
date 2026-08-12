"""Which of the dialog tests leave an `after` timer queued on the shared root.

Flake A of #446 kills a LATER test: `bad window path name` on `deiconify()`
inside `show()`, i.e. a dialog's own toplevel destroyed between construction and
positioning. Nothing in the failing test touches that window, which points at
the mechanism `CLAUDE.md` records from #397 -- a timer queued by an earlier test
firing during a later one, where the callback destroys whatever it finds.

At 1 in 12, hunting the failure is useless: a clean run is the expected outcome.
So this does not look for the crash at all. It measures the PRECONDITION -- a
timer outliving the test that scheduled it -- which is deterministic, and names
the leaker instead of leaving it to be guessed from reading.

Run:  py -3.12 development/probe_446_leaked_after_jobs.py

Output is ASCII only (this box's console is cp1252).
"""
from __future__ import annotations

import sys
import tkinter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

FILES = [
    "tests/widgets/public/test_dialog_enter_key.py",
    "tests/widgets/public/test_dialog_nested_modality.py",
    "tests/widgets/public/test_dialog_initial_focus.py",
    "tests/widgets/public/test_layout_migration_error.py",
    "tests/widgets/public/test_dialog_press_contract.py",
]


def _pending(root) -> set[str]:
    """The ids of every `after` job currently queued on this interpreter."""
    if root is None:
        return set()
    try:
        return set(root.tk.splitlist(root.tk.call("after", "info")))
    except tkinter.TclError:
        return set()


def _describe(root, job: str) -> str:
    """The script a queued job will run, so the leaker is identifiable."""
    try:
        info = root.tk.splitlist(root.tk.call("after", "info", job))
    except tkinter.TclError:
        return "<already fired or cancelled>"
    # ('<script>', 'timer'|'idle')
    script = str(info[0]) if info else "?"
    return script.replace("\n", " ")[:110]


class LeakWatch:
    """Snapshots queued jobs around every test and reports what survived."""

    def __init__(self) -> None:
        self.leaks: list[tuple[str, list[str]]] = []
        self._before: set[str] = set()

    @staticmethod
    def _root():
        # The shared root is the session app's; tkinter records it here.
        return getattr(tkinter, "_default_root", None)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        root = self._root()
        self._before = _pending(root)
        yield
        root = self._root()
        after = _pending(root)
        new = sorted(after - self._before)
        if new:
            self.leaks.append((item.nodeid, [f"{j}  {_describe(root, j)}" for j in new]))


def main() -> int:
    watch = LeakWatch()
    args = [*FILES, "-q", "-p", "no:cacheprovider", "--no-header"]
    print("Running the five dialog files in ONE process, watching `after info`.")
    print("A job present after a test that was absent before it OUTLIVED that test.\n")
    code = pytest.main(args, plugins=[watch])

    print("\n" + "=" * 72)
    print("LEAKED TIMERS (queued during a test, still queued after it)")
    print("=" * 72)
    if not watch.leaks:
        print("\nNone. Every test cancelled what it scheduled.")
        print("Flake A's precondition is NOT a leaked timer -- look elsewhere.")
    else:
        for nodeid, jobs in watch.leaks:
            print(f"\n{nodeid}")
            for job in jobs:
                print(f"    {job}")
        print(f"\n{len(watch.leaks)} test(s) leaked a timer onto the shared root.")
        print("Any of these can fire during a LATER test. A callback that")
        print("destroys a window it LOOKS UP rather than one it was handed is")
        print("the shape that produces flake A's 'bad window path name'.")
    return 0 if code == 0 else int(code)


if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    raise SystemExit(main())
