"""`import bootstack` must not depend on optional parts of the standard library.

`idlelib` is standard library, but not every Python build ships it — Debian and
Ubuntu package IDLE separately, the same way they package `python3-tk`
separately, so `import idlelib` fails on a stock system Python there. An import
of it at module scope anywhere reachable from `bootstack/__init__` therefore
takes down the entire framework rather than degrading one widget, which is what
shipped in 0.2.2 (#430).

Neither maintainer box can reproduce that: the python.org installers for
Windows and macOS bundle IDLE, so `import idlelib` always succeeds there. This
guards the invariant directly instead of relying on the platform to expose it.

Lives under `tests/widgets/public/` because `testpaths` is `tests/cli`,
`tests/widgets/public`, `tests/data` — a file outside those three is collected
by nothing at all. It is not a widget test.
"""
from __future__ import annotations

import subprocess
import sys

# Setting a name to None in `sys.modules` makes importing it raise, which stands
# in for a Python build that does not ship it. The import runs in a subprocess
# because `bootstack` is already imported long before any test runs.
_BLOCKED_IMPORT = (
    "import sys\n"
    "sys.modules['idlelib'] = None\n"
    "sys.modules['idlelib.redirector'] = None\n"
    "import bootstack\n"
)


def test_bootstack_imports_on_a_python_without_idlelib():
    """The framework imports with `idlelib` unavailable.

    Controlled rather than assumed: run against the code this replaced, the
    same subprocess exits 1 with `ModuleNotFoundError: import of
    idlelib.redirector halted; None in sys.modules`. So the check fails for the
    right reason and is not merely asserting that importing works.
    """
    result = subprocess.run(
        [sys.executable, "-c", _BLOCKED_IMPORT],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_the_blocking_trick_actually_blocks():
    """Control for the test above, which would pass vacuously if it did not.

    If `sys.modules[name] = None` stopped making imports fail — a detail of the
    import system, not of this project — the test above would report success
    while proving nothing at all.
    """
    result = subprocess.run(
        [sys.executable, "-c", _BLOCKED_IMPORT.replace(
            "import bootstack", "import idlelib.redirector"
        )],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "idlelib" in result.stderr
