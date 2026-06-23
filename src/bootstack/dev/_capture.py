"""Capture a ``with bs.App()`` block's body from source for hot reload.

PROVISIONAL — part of the carved-out ``bootstack.dev`` surface.

The body of a ``with`` block runs in the caller's frame and is never handed to
the context manager, so a flag alone cannot re-run it. In dev mode the App
captures *where* its body lives (file + the ``as`` target name) and, on each
reload, re-reads the file and re-extracts the matching block's statements — so a
save is picked up. Matching is by the ``as`` target name, which is stable across
edits that shift line numbers.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from types import FrameType
from typing import Any


@dataclass
class BodyCapture:
    """Where a reloadable ``with`` block lives, plus its compiled body cache."""

    filename: str
    """Absolute path of the source file holding the ``with`` block."""
    target_names: tuple[str, ...]
    """The ``as <name>`` targets of the block (e.g. ``("app",)``)."""
    module_globals: dict
    """The module namespace the body executes in (frame globals)."""
    with_lineno: int
    """Line of the ``with`` statement at capture time (a matching hint only)."""

    @property
    def is_capturable(self) -> bool:
        """Whether this capture can drive an in-process reload."""
        return bool(self.filename) and bool(self.target_names)


def capture_from_frame(frame: FrameType) -> BodyCapture | None:
    """Capture the enclosing ``with`` block from a caller frame.

    Returns None when the block is not reloadable in-process — notably when it
    is authored inside a function (frame locals differ from globals), so the
    body's names cannot be safely re-bound by re-exec.
    """
    # A module-level `with` runs with locals IS globals. Inside a function the
    # two differ; re-execing the body into globals would mis-scope its names.
    if frame.f_locals is not frame.f_globals:
        return None

    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    try:
        source = _read(filename)
    except OSError:
        return None

    node = _find_with_node(source, lineno)
    if node is None:
        return None
    targets = _with_target_names(node)
    if not targets:
        return None

    return BodyCapture(
        filename=filename,
        target_names=targets,
        module_globals=frame.f_globals,
        with_lineno=node.lineno,
    )


def find_current_body(capture: BodyCapture) -> list[ast.stmt]:
    """Re-read the source and return the matching block's current statements.

    Raises ``SyntaxError`` if the file no longer parses (the caller renders a
    banner and keeps the process alive), or ``RuntimeError`` if the block can no
    longer be located.
    """
    source = _read(capture.filename)
    tree = ast.parse(source, capture.filename)  # SyntaxError propagates
    node = _match_with_node(tree, capture)
    if node is None:
        raise RuntimeError(
            "hot reload: could not locate the `with` block to reload "
            f"(looking for `as {', '.join(capture.target_names)}` in "
            f"{capture.filename})"
        )
    return list(node.body)


def compile_body(filename: str, body: list[ast.stmt]) -> Any:
    """Compile a block body (list of statements) into an executable code object."""
    module = ast.Module(body=list(body), type_ignores=[])
    ast.fix_missing_locations(module)
    return compile(module, filename, "exec")


# --- internals ---------------------------------------------------------------


def _read(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()


def _find_with_node(source: str, lineno: int) -> ast.With | None:
    """Find the top-level ``with`` node at (or nearest to) a line."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    candidates = [n for n in tree.body if isinstance(n, ast.With)]
    if not candidates:
        return None
    for node in candidates:
        if node.lineno == lineno:
            return node
    return min(candidates, key=lambda n: abs(n.lineno - lineno))


def _match_with_node(tree: ast.Module, capture: BodyCapture) -> ast.With | None:
    """Locate the block to reload, preferring a target-name match."""
    candidates = [n for n in tree.body if isinstance(n, ast.With)]
    if not candidates:
        return None
    want = set(capture.target_names)
    by_name = [n for n in candidates if want & set(_with_target_names(n))]
    if by_name:
        # Prefer the one nearest the original line if several share the name.
        return min(by_name, key=lambda n: abs(n.lineno - capture.with_lineno))
    return min(candidates, key=lambda n: abs(n.lineno - capture.with_lineno))


def _with_target_names(node: ast.With) -> tuple[str, ...]:
    names = []
    for item in node.items:
        var = item.optional_vars
        if isinstance(var, ast.Name):
            names.append(var.id)
    return tuple(names)