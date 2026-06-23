"""One-command GUI test runner with per-process isolation.

GUI tests run against a single Tk root for the whole process — destroying a
root and creating a new one in-process crashes natively (ttk ``element_create``
access violation as image-element registrations accumulate across interpreters).
Most tests share one session root (see ``tests/conftest.py``). A handful
genuinely construct their own root (``App(undecorated=...)``, an App-config
factory, ``AppShell``/``Workbench``); those are marked ``@pytest.mark.isolated``
and must each run in a dedicated process.

This runner does both in one command:

1. Run the whole suite EXCEPT isolated tests, in one process (shared root).
2. Run each isolated test module in its own fresh process.

Exit code is non-zero if any leg fails. Extra args are forwarded to pytest, e.g.
``python tests/run_gui.py -q`` or ``python tests/run_gui.py -k slider``.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Modules that build their own Tk root once and run cleanly in a dedicated
# process (one root for the module).
ISOLATED = [
    "tests/widgets/public/test_undecorated_titlebar.py",
    "tests/widgets/public/test_appshell_reshape.py",
    "tests/widgets/public/test_workbench.py",
    "tests/widgets/public/test_sidebar_toggle.py",
    "tests/widgets/public/test_tabs_overflow.py",
    "tests/widgets/public/test_hot_reload_app.py",
    "tests/widgets/public/test_hot_reload_shell.py",
]

# Modules that construct a fresh root PER TEST (e.g. an App-config factory
# exercising constructor kwargs). Many sequential roots in one process hit a
# native Tcl-teardown failure, so each test runs in its own process.
PER_TEST_ISOLATED = [
    "tests/widgets/public/test_app_config.py",
]


def _run(args: list[str]) -> int:
    print(f"\n$ pytest {' '.join(args)}", flush=True)
    return subprocess.run([sys.executable, "-m", "pytest", *args], cwd=REPO).returncode


def _collect_test_ids(mod: str) -> list[str]:
    """Return the per-test node ids in a module via pytest --collect-only."""
    out = subprocess.run(
        [sys.executable, "-m", "pytest", mod, "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if "::" in ln and ln.strip().startswith(mod)]


# Shared-root suite, split into independent process groups. The widget/CLI
# tests and the data tests each share one root within their group, but the data
# tests' change-hub/after-queue assertions are sensitive to the app event-queue
# state left by hundreds of widget tests, so they run in their own process.
SHARED_GROUPS = [
    ["tests/widgets/public", "tests/cli"],
    ["tests/data"],
]


def main() -> int:
    extra = sys.argv[1:]
    failed = []

    # 1) Shared-root suite, each group in its own process (not isolated tests).
    for group in SHARED_GROUPS:
        if _run([*group, "-m", "not isolated", *extra]) != 0:
            failed.append("shared-root: " + " ".join(group))

    # 2) Each isolated module in its own process.
    for mod in ISOLATED:
        if _run([mod, *extra]) != 0:
            failed.append(mod)

    # 3) Per-test-isolated modules: each test in its own fresh process.
    for mod in PER_TEST_ISOLATED:
        ids = _collect_test_ids(mod)
        if not ids:
            ids = [mod]
        for tid in ids:
            if _run([tid, *extra]) != 0:
                failed.append(tid)

    print("\n" + "=" * 60)
    if failed:
        print("FAILED legs:")
        for f in failed:
            print(f"  - {f}")
        return 1
    print("All GUI test legs passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
