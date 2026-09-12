"""Docstring drift census for #474 — run before and after each area's pass.

Two views:

* PUBLIC  — what the API docs render: everything `__all__` exports from
  `bootstack` and its public submodules, plus each exported class's public
  members (inherited included). Imports the package.
* INTERNAL — every other docstring under `src/bootstack`, found by AST, grouped
  by area so a pass can be scoped to one.

A flag is a regex signal, not a verdict: it means look, not cut. Output is ASCII.

    py -3.12 development/probe_474_docstring_census.py            # both views
    py -3.12 development/probe_474_docstring_census.py --list _runtime
"""
from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import pathlib
import re
import sys
from collections import Counter, defaultdict

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "bootstack"
sys.path.insert(0, str(REPO / "src"))

PUBLIC_MODULES = [
    "bootstack", "bootstack.data", "bootstack.style", "bootstack.i18n",
    "bootstack.validation", "bootstack.events", "bootstack.streams",
    "bootstack.scheduling", "bootstack.shortcuts", "bootstack.store",
    "bootstack.errors", "bootstack.types", "bootstack.dialogs",
    "bootstack.signals", "bootstack.images",
]

SIGNALS = {
    "issue_ref": re.compile(r"(?<![\w/`])#\d{3}\b"),
    "history": re.compile(r"\b(used to|previously|no longer|pre-fix|regression|round \d|reviewer|maintainer)\b", re.I),
    "measured": re.compile(r"\bmeasured\b", re.I),
    "warning": re.compile("⚠"),
    "shouting": re.compile(r"\b[A-Z]{3,}(?:\s+[A-Z]{2,}){2,}\b"),
    "dev_path": re.compile(r"development/|docs/_dev|CLAUDE\.md"),
}
PUBLIC_EXTRA = {
    "tk_terms": re.compile(r"\b(tkinter|ttk|Tcl|Tk\b|tk\.[A-Za-z]+|textvariable|event_generate|winfo_\w+|cget|after_idle|bindtags?|StringVar|IntVar|BooleanVar)\b"),
    "internal_names": re.compile(r"`_[a-z]\w*`|\b_internal\b|_impl\b"),
}


LONG = 25  # lines; a long docstring is a signal on its own


def flags(doc: str, extra: bool) -> list[str]:
    rules = {**SIGNALS, **(PUBLIC_EXTRA if extra else {})}
    found = [k for k, rx in rules.items() if rx.search(doc)]
    if not extra and doc.count("\n") + 1 >= LONG:
        found.append("long")
    return found


def public_view() -> set[str]:
    """Print the public census; return the source files it covered."""
    seen: set[int] = set()
    stats: Counter = Counter()
    hits: defaultdict = defaultdict(list)
    for modname in PUBLIC_MODULES:
        try:
            mod = importlib.import_module(modname)
        except Exception as exc:  # a missing optional dependency
            print(f"  SKIP {modname}: {exc}")
            continue
        for name in getattr(mod, "__all__", []):
            obj = getattr(mod, name, None)
            if obj is None:
                continue
            targets = [(f"{modname}.{name}", obj)]
            if inspect.isclass(obj):
                for mname, member in inspect.getmembers(obj):
                    if mname.startswith("_") and mname != "__init__":
                        continue
                    if isinstance(member, property) or (
                        inspect.isfunction(member)
                        and (member.__module__ or "").startswith("bootstack")
                    ):
                        targets.append((f"{modname}.{name}.{mname}", member))
            for qual, target in targets:
                doc = inspect.getdoc(target)
                if not doc or id(target) in seen:
                    continue
                seen.add(id(target))
                stats["docstrings"] += 1
                for k in flags(doc, extra=True):
                    stats[k] += 1
                    hits[k].append(qual)
    print(f"PUBLIC  docstrings={stats['docstrings']}")
    for k in [*SIGNALS, *PUBLIC_EXTRA]:
        if stats[k]:
            print(f"  {k:15} {stats[k]:4}  " + ", ".join(hits[k][:6]) + (" ..." if len(hits[k]) > 6 else ""))
    return set()


def area_of(rel: pathlib.PurePath) -> str:
    parts = rel.parts
    if parts[0] == "widgets" and len(parts) > 2 and parts[1].startswith("_"):
        if parts[1] == "_impl" and len(parts) > 3:
            return f"widgets/_impl/{parts[2]}"
        return f"widgets/{parts[1]}"
    return parts[0] if len(parts) > 1 else "(top)"


def internal_view(list_area: str | None) -> None:
    per_area: defaultdict = defaultdict(Counter)
    listing: list[str] = []
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(SRC)
        private_module = any(p.startswith("_") and p != "__init__.py" for p in rel.parts)
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))

        def visit(node, owner_private):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    dunder = child.name.startswith("__") and child.name.endswith("__")
                    private = owner_private or (child.name.startswith("_") and not dunder)
                    doc = ast.get_docstring(child, clean=True)
                    if doc and private:
                        yield child.name, child.lineno, doc
                    yield from visit(child, private)

        found = list(visit(tree, private_module))
        module_doc = ast.get_docstring(tree, clean=True)
        if module_doc and private_module:
            found.insert(0, ("<module>", 1, module_doc))
        area = area_of(rel)
        for name, line, doc in found:
            c = per_area[area]
            c["docstrings"] += 1
            c["lines"] += doc.count("\n") + 1
            f = flags(doc, extra=False)
            if f:
                c["flagged"] += 1
                if list_area and area.startswith(list_area):
                    listing.append(f"  {rel.as_posix()}:{line} {name}  [{','.join(f)}]")
    total = Counter()
    for c in per_area.values():
        total.update(c)
    print(f"\nINTERNAL docstrings={total['docstrings']} lines={total['lines']} flagged={total['flagged']}")
    for area, c in sorted(per_area.items(), key=lambda kv: -kv[1]["flagged"]):
        if c["flagged"]:
            print(f"  {area:34} flagged {c['flagged']:4} of {c['docstrings']:4}  ({c['lines']} lines)")
    if list_area:
        print(f"\nFLAGGED in {list_area} ({len(listing)}):")
        print("\n".join(listing))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", metavar="AREA", help="list flagged internal docstrings in an area prefix")
    args = parser.parse_args()
    public_view()
    internal_view(args.list)


if __name__ == "__main__":
    main()
