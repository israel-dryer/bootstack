#!/usr/bin/env python3
"""
Generate API reference pages for bootstack widgets.

Run from the project root:
    python docs_scripts/gen_api.py

Writes one complete reference page per widget to docs/reference/widgets/<slug>.md.

Page structure:
  - mkdocstrings ::: block  — class description + constructor parameters only
  - ## Properties / ## Methods / ## State / ## Events   (h2, in TOC)
  - ### `member(sig)` → type                            (h3 static markdown)

Static h3 headings for members are nested correctly under h2 section headers
in the page.toc by the markdown toc extension. mkdocstrings-injected headings
always register at a flat page.toc level, which is why ::: blocks for sections
were abandoned.

Re-run whenever source docstrings change.
"""

from __future__ import annotations

import sys
from pathlib import Path

import griffe

# ── Output ────────────────────────────────────────────────────────────────────

OUT_DIR = Path("docs/reference/widgets")

# ── Widget registry ───────────────────────────────────────────────────────────

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

SKIP: frozenset[str] = frozenset({
    "bbox", "delete", "icursor", "index", "insert",
    "scan_mark", "scan_dragto",
    "selection_adjust", "selection_clear", "selection_from",
    "selection_to", "selection_range", "selection_present", "selection_all",
    "configure", "config", "cget",
    "validation",
    "add_validation_rules",
})

STATE_NAMES: frozenset[str] = frozenset({
    "disable", "enable", "readonly", "show", "hide", "forget",
    "lift", "lower", "state",
})


def classify(name: str, member: griffe.Object) -> str | None:
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


# ── Formatting helpers ────────────────────────────────────────────────────────

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


def first_sentence(text: str) -> str:
    text = text.strip()
    for sep in (".\n", ". "):
        idx = text.find(sep)
        if idx != -1:
            return text[:idx].strip()
    idx = text.find("\n\n")
    if idx != -1:
        return text[:idx].strip().rstrip(".")
    for i, line in enumerate(text.splitlines()):
        if i > 0 and line.strip().startswith(("-", "*", "+")):
            return " ".join(text.splitlines()[:i]).strip().rstrip(".")
    return text.rstrip(".")


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
) -> dict[str, list[tuple[str, griffe.Object]]]:
    """Return (name, member) pairs grouped by section, in source order."""
    sections: dict[str, list[tuple[str, griffe.Object]]] = {
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
                sections[section].append((name, member))
                seen.add(name)

    cls = load_class(module, class_path)
    if cls:
        pull(cls)

    for base_path in include_from:
        base = load_class(module, base_path)
        if base:
            pull(base)

    return sections


# ── Static member markdown ────────────────────────────────────────────────────

def gen_member_md(name: str, member: griffe.Object) -> list[str]:
    """Generate static h3 markdown for a single member.

    Format:
      ### `name` — *property* · `Type`       (for attributes)
      ### `name(param, param)` → `ReturnType` (for functions)
      description sentence
    """
    lines: list[str] = []
    desc = first_sentence(member.docstring.value) if member.docstring else ""

    if isinstance(member, griffe.Attribute):
        type_str = fmt_type(member.annotation) if member.annotation else ""
        suffix = f" — *property*" + (f" · `{type_str}`" if type_str else "")
        lines.append(f"### `{name}`{suffix}")
        if desc:
            lines.append("")
            lines.append(desc)
        lines.append("")

    elif isinstance(member, griffe.Function):
        params: list[str] = []
        for p in member.parameters:
            if p.name in ("self", "cls"):
                continue
            if p.kind in (
                griffe.ParameterKind.var_positional,
                griffe.ParameterKind.var_keyword,
            ):
                continue
            params.append(f"{p.name}={p.default}" if p.default is not None else p.name)

        ret = ""
        if member.returns:
            ret_str = fmt_type(member.returns)
            if ret_str and ret_str not in ("None", "none"):
                ret = f" → `{ret_str}`"

        lines.append(f"### `{name}({', '.join(params)})`{ret}")
        if desc:
            lines.append("")
            lines.append(desc)
        lines.append("")

    return lines


# ── Page generator ────────────────────────────────────────────────────────────

def gen_page(slug: str, cfg: dict, module: griffe.Module) -> str | None:
    class_path = cfg["path"]
    include_from = cfg.get("include_from", [])
    class_name = class_path.split(".")[-1]

    if load_class(module, class_path) is None:
        return None

    sections = collect_sections(module, class_path, include_from)

    lines: list[str] = [
        "---",
        f"title: {class_name}",
        "---",
        "",
        # mkdocstrings renders the class description and constructor parameters.
        # members: false keeps it from rendering any member docs here.
        f"::: {class_path}",
        "    options:",
        "      show_root_heading: true",
        "      show_root_toc_entry: true",
        "      show_root_full_path: false",
        "      inherited_members: false",
        "      merge_init_into_class: true",
        "      members: false",
        "",
    ]

    section_labels = {
        "properties": "Properties",
        "methods": "Methods",
        "state": "State",
        "events": "Events",
    }

    for key, label in section_labels.items():
        members_in_section = sections[key]
        if not members_in_section:
            continue
        lines += [f"## {label}", ""]
        for name, member in members_in_section:
            lines += gen_member_md(name, member)

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