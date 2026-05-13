#!/usr/bin/env python3
"""
Generate API reference pages for bootstack widgets.

Run from the project root:
    python docs_scripts/gen_api.py

Writes one complete reference page per widget to docs/reference/widgets/<slug>.md.
Each page has h2 section headings (Properties / Methods / State / Events) that
appear in the MkDocs Material right-side TOC.

Re-run whenever source docstrings change.
"""

from __future__ import annotations

import sys
from pathlib import Path

import griffe

# ── Output ────────────────────────────────────────────────────────────────────

OUT_DIR = Path("docs/reference/widgets")

# ── Widget registry ───────────────────────────────────────────────────────────
#
# slug → {
#   "path":         fully-qualified class path
#   "include_from": additional classes to pull inherited members from
# }

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

# ── Member classification ─────────────────────────────────────────────────────

# Members to exclude entirely from the reference page.
SKIP: frozenset[str] = frozenset({
    "bbox", "delete", "icursor", "index", "insert",
    "scan_mark", "scan_dragto",
    "selection_adjust", "selection_clear", "selection_from",
    "selection_to", "selection_range", "selection_present", "selection_all",
    "configure", "config", "cget",
    "validation",
    "add_validation_rules",
})

# Methods that belong in the State section.
STATE_NAMES: frozenset[str] = frozenset({
    "disable", "enable", "readonly", "show", "hide", "forget",
    "lift", "lower", "state",
})


def classify(name: str, member: griffe.Object) -> str | None:
    """Return the section name for a member, or None to skip it."""
    if name.startswith("_") or name in SKIP:
        return None
    if not member.docstring:
        return None
    if isinstance(member, griffe.Attribute):
        return "properties"
    if isinstance(member, griffe.Function):
        if name.startswith(("on_", "off_")):
            return "events"
        if name in STATE_NAMES:
            return "state"
        return "methods"
    return None


# ── Griffe helpers ────────────────────────────────────────────────────────────

def load_class(module: griffe.Module, class_path: str) -> griffe.Class | None:
    parts = class_path.split(".")
    obj: griffe.Object = module
    try:
        for part in parts[1:]:
            obj = obj[part]
    except KeyError as exc:
        print(f"  not found: {class_path} ({exc})", file=sys.stderr)
        return None
    if not isinstance(obj, griffe.Class):
        print(f"  {class_path} is {type(obj).__name__}, expected Class", file=sys.stderr)
        return None
    return obj


def collect_sections(
    module: griffe.Module,
    class_path: str,
    include_from: list[str],
) -> dict[str, list[str]]:
    """Return member names grouped by section, preserving source order."""
    sections: dict[str, list[str]] = {
        "properties": [],
        "methods": [],
        "state": [],
        "events": [],
    }
    seen: set[str] = set()

    def pull(cls: griffe.Class) -> None:
        for name, member in cls.members.items():
            if name in seen:
                continue
            section = classify(name, member)
            if section:
                sections[section].append(name)
                seen.add(name)

    cls = load_class(module, class_path)
    if cls:
        pull(cls)

    for base_path in include_from:
        base = load_class(module, base_path)
        if base:
            pull(base)

    return sections


# ── Page generator ────────────────────────────────────────────────────────────

def mkdocs_block(
    class_path: str,
    *,
    show_root_heading: bool = False,
    inherited_members: bool = True,
    members: list[str] | bool = True,
    merge_init: bool = False,
) -> list[str]:
    """Render a mkdocstrings ::: block as a list of lines."""
    lines = [f"::: {class_path}", "    options:"]

    lines.append(f"      show_root_heading: {'true' if show_root_heading else 'false'}")
    lines.append(f"      show_root_toc_entry: {'true' if show_root_heading else 'false'}")
    lines.append("      show_root_full_path: false")
    lines.append(f"      inherited_members: {'true' if inherited_members else 'false'}")

    if merge_init:
        lines.append("      merge_init_into_class: true")

    if members is False:
        lines.append("      members: false")
    elif isinstance(members, list):
        lines.append("      members:")
        for m in members:
            lines.append(f"        - {m}")

    return lines


def gen_page(slug: str, cfg: dict, module: griffe.Module) -> str | None:
    class_path = cfg["path"]
    include_from = cfg.get("include_from", [])
    class_name = class_path.split(".")[-1]

    cls = load_class(module, class_path)
    if cls is None:
        return None

    sections = collect_sections(module, class_path, include_from)

    lines: list[str] = [
        "---",
        f"title: {class_name}",
        "---",
        "",
    ]

    # Class description block — docstring + merged __init__ signature, no members
    lines += mkdocs_block(
        class_path,
        show_root_heading=True,
        inherited_members=False,
        members=False,
        merge_init=True,
    )
    lines.append("")

    section_labels = {
        "properties": "Properties",
        "methods": "Methods",
        "state": "State",
        "events": "Events",
    }

    for key, label in section_labels.items():
        names = sections[key]
        if not names:
            continue
        lines += [f"## {label}", ""]
        lines += mkdocs_block(
            class_path,
            show_root_heading=False,
            inherited_members=True,
            members=names,
        )
        lines.append("")

    return "\n".join(lines)


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
        content = gen_page(slug, cfg, module)
        if content is None:
            print("skipped")
            continue
        out = OUT_DIR / f"{slug}.md"
        out.write_text(content, encoding="utf-8")
        print(f"-> {out}")

    print("Done.")


if __name__ == "__main__":
    main()