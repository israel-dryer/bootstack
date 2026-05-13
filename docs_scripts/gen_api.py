#!/usr/bin/env python3
"""
Generate static API reference markdown snippets for bootstack widget pages.

Run from the project root:
    python docs_scripts/gen_api.py

Outputs one file per widget to docs/snippets/api/<slug>.md.

Include in a widget page with:
    --8<-- "snippets/api/textentry.md"

Each snippet contains up to three ## sections (Parameters, Properties, Methods).
These are plain markdown headings and appear directly in the page TOC.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import griffe

# ── Output ────────────────────────────────────────────────────────────────────

OUT_DIR = Path("docs/snippets/api")

# ── Widget registry ───────────────────────────────────────────────────────────
#
# slug: {
#   "path":         fully-qualified class to generate __init__ parameters from
#   "include_from": additional classes whose members are included (base classes)
# }
#
# griffe does not automatically resolve inherited members across the MRO, so
# base classes whose methods/properties should appear in the output must be
# listed explicitly under "include_from".

_FIELD = "bootstack.widgets.composites.field.Field"

WIDGETS: dict[str, dict] = {
    "textentry": {
        "path": "bootstack.widgets.composites.textentry.TextEntry",
        "include_from": [_FIELD],
    },
    "passwordentry": {
        "path": "bootstack.widgets.composites.passwordentry.PasswordEntry",
        "include_from": [_FIELD],
    },
    "pathentry": {
        "path": "bootstack.widgets.composites.pathentry.PathEntry",
        "include_from": [_FIELD],
    },
    "numericentry": {
        "path": "bootstack.widgets.composites.numericentry.NumericEntry",
        "include_from": [_FIELD],
    },
    "spinnerentry": {
        "path": "bootstack.widgets.composites.spinnerentry.SpinnerEntry",
        "include_from": [_FIELD],
    },
    "dateentry": {
        "path": "bootstack.widgets.composites.dateentry.DateEntry",
        "include_from": [_FIELD],
    },
    "timeentry": {
        "path": "bootstack.widgets.composites.timeentry.TimeEntry",
        "include_from": [_FIELD],
    },
    "scrolledtext": {
        "path": "bootstack.widgets.composites.scrolledtext.ScrolledText",
        "include_from": [_FIELD],
    },
    "selectbox": {
        "path": "bootstack.widgets.composites.selectbox.SelectBox",
        "include_from": [_FIELD],
    },
}

# ── Member filter ─────────────────────────────────────────────────────────────

SKIP: frozenset[str] = frozenset({
    # EntryMixin text-cursor operations (not part of the public field contract)
    "bbox", "delete", "icursor", "index", "insert",
    "scan_mark", "scan_dragto",
    "selection_adjust", "selection_clear", "selection_from",
    "selection_to", "selection_range", "selection_present", "selection_all",
    # Low-level config forwarding (documented at the ttk level)
    "configure", "config", "cget",
    # Internal helpers exposed as instance attributes
    "validation",
    "add_validation_rules",  # batch setter; rarely needed directly
})

# ── Helpers ───────────────────────────────────────────────────────────────────

_STRIP_PREFIXES = (
    "bootstack.widgets.types.",
    "bootstack.core.signals.signal.",
    "bootstack.core.signals.",
    "bootstack.widgets.composites.field.",
    "typing_extensions.",
    "typing.",
)


def fmt_type(annotation: object) -> str:
    if annotation is None:
        return ""
    s = str(annotation)
    for prefix in _STRIP_PREFIXES:
        s = s.replace(prefix, "")
    return s.strip()


def fmt_default(default: object) -> str:
    """Render a parameter default as a table cell. Returns '—' for no default."""
    if default is None:
        return "—"
    s = str(default)
    return f"`{s}`" if s else "—"


def first_sentence(text: str) -> str:
    """Return the first sentence of a string, suitable for a table cell."""
    text = text.strip()
    # Stop at a period followed by whitespace or newline
    for sep in (".\n", ". "):
        idx = text.find(sep)
        if idx != -1:
            return text[:idx].strip()
    # Stop at a blank line (multi-paragraph docstrings)
    idx = text.find("\n\n")
    if idx != -1:
        return text[:idx].strip().rstrip(".")
    # Stop at a newline followed by a list marker
    for i, line in enumerate(text.splitlines()):
        if i > 0 and line.strip().startswith(("-", "*", "+")):
            return " ".join(text.splitlines()[:i]).strip().rstrip(".")
    return text.rstrip(".")




# ── Member collection ─────────────────────────────────────────────────────────

def load_class(module: griffe.Module, class_path: str) -> griffe.Class | None:
    parts = class_path.split(".")
    obj: griffe.Object = module
    try:
        for part in parts[1:]:   # skip "bootstack" — that is the loaded root
            obj = obj[part]
    except KeyError as exc:
        print(f"  not found: {class_path} ({exc})", file=sys.stderr)
        return None
    if not isinstance(obj, griffe.Class):
        print(f"  {class_path} resolved to {type(obj).__name__}, expected Class", file=sys.stderr)
        return None
    return obj


def collect_members(
    module: griffe.Module,
    class_path: str,
    include_from: list[str],
) -> dict[str, griffe.Object]:
    """
    Collect all public, documented members from a class and its explicitly
    listed base classes.

    griffe represents @property members as Attribute objects and regular
    methods as Function objects — both are collected here and routed to
    the appropriate section generator by type.

    Members are keyed by name; the class's own members take precedence over
    those from include_from (earlier entries in include_from win over later).
    """
    seen: dict[str, griffe.Object] = {}

    def pull(cls: griffe.Class) -> None:
        for name, member in cls.members.items():
            if name.startswith("_"):
                continue
            if name in SKIP:
                continue
            if not isinstance(member, (griffe.Function, griffe.Attribute)):
                continue
            if not member.docstring:
                continue
            if name not in seen:
                seen[name] = member

    cls = load_class(module, class_path)
    if cls:
        pull(cls)

    for base_path in include_from:
        base = load_class(module, base_path)
        if base:
            pull(base)

    return seen


# ── Section generators ────────────────────────────────────────────────────────

def gen_parameters(cls: griffe.Class) -> str:
    """### Parameters table — built from __init__ docstring Args sections."""
    init = cls.members.get("__init__")
    if not isinstance(init, griffe.Function) or not init.docstring:
        return ""

    # Collect defaults from the actual function signature; the docstring
    # Args section carries descriptions but not default values.
    sig_defaults: dict[str, str] = {}
    for p in init.parameters:
        if p.name == "self":
            continue
        sig_defaults[p.name] = fmt_default(p.default)

    rows: list[str] = []
    try:
        for section in init.docstring.parsed:
            if section.kind.value in ("parameters", "other_parameters"):
                for dp in section.value:
                    type_str = fmt_type(dp.annotation) if dp.annotation else ""
                    type_cell = f"`{type_str}`" if type_str else "—"
                    default = sig_defaults.get(dp.name, "—")
                    desc = first_sentence(dp.description) if dp.description else ""
                    rows.append(f"| `{dp.name}` | {type_cell} | {default} | {desc} |")
    except Exception as exc:
        print(f"    parameters parse error: {exc}", file=sys.stderr)

    if not rows:
        return ""

    return "\n".join([
        "### Parameters\n",
        "| Name | Type | Default | Description |",
        "|---|---|---|---|",
        *rows,
        "",
    ])


def gen_properties(members: dict[str, griffe.Object]) -> str:
    """### Properties table — griffe exposes @property members as Attribute objects."""
    rows: list[str] = []
    for name, member in sorted(members.items()):
        if not isinstance(member, griffe.Attribute):
            continue
        type_str = fmt_type(member.annotation) if member.annotation else ""
        type_cell = f"`{type_str}`" if type_str else "—"
        desc = first_sentence(member.docstring.value)
        rows.append(f"| `{name}` | {type_cell} | {desc} |")

    if not rows:
        return ""

    return "\n".join([
        "### Properties\n",
        "| Name | Type | Description |",
        "|---|---|---|",
        *rows,
        "",
    ])


def gen_methods(members: dict[str, griffe.Object]) -> str:
    """### Methods table."""
    rows: list[str] = []
    for name, member in sorted(members.items()):
        if not isinstance(member, griffe.Function):
            continue

        # Build a compact param list, skipping self/cls/*args/**kwargs
        params: list[str] = []
        for p in member.parameters:
            if p.name in ("self", "cls"):
                continue
            if p.kind in (
                griffe.ParameterKind.var_positional,
                griffe.ParameterKind.var_keyword,
            ):
                continue
            if p.default is not None:
                params.append(f"{p.name}={p.default}")
            else:
                params.append(p.name)

        sig = f"`{name}({', '.join(params)})`"
        desc = first_sentence(member.docstring.value)

        ret = ""
        if member.returns:
            ret_str = fmt_type(member.returns)
            if ret_str and ret_str not in ("None", "none"):
                ret = f" → `{ret_str}`"

        rows.append(f"| {sig}{ret} | {desc} |")

    if not rows:
        return ""

    return "\n".join([
        "### Methods\n",
        "| Method | Description |",
        "|---|---|",
        *rows,
        "",
    ])


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading bootstack...")
    try:
        module = griffe.load("bootstack", docstring_parser="google", resolve_aliases=True)
    except Exception as exc:
        print(f"griffe load failed: {exc}", file=sys.stderr)
        sys.exit(1)

    for slug, cfg in WIDGETS.items():
        print(f"  {slug:<20}", end=" ", flush=True)

        class_path = cfg["path"]
        include_from = cfg.get("include_from", [])

        cls = load_class(module, class_path)
        if cls is None:
            print("skipped")
            continue

        members = collect_members(module, class_path, include_from)

        body = "\n".join(s for s in [
            gen_parameters(cls),
            gen_properties(members),
            gen_methods(members),
        ] if s)
        content = f"## API reference\n\n{body}" if body else ""

        if not content.strip():
            print("empty output")
            continue

        out = OUT_DIR / f"{slug}.md"
        out.write_text(content, encoding="utf-8")
        lines = content.count("\n")
        print(f"-> {out}  ({lines} lines)")

    print("Done.")


if __name__ == "__main__":
    main()