"""Derive the GitHub Release title and body for a tag from CHANGELOG.md.

The CHANGELOG uses ``## [<version>] — <descriptive title>`` section headings. The
GitHub Release should show ``<version> — <descriptive title>`` as its *title*
(no ``v`` prefix — GitHub already shows the ``v<version>`` tag alongside it, and
this matches the CHANGELOG's ``[<version>]`` format), and the section content
*without* that heading in its *body* (so the title isn't repeated and the
``[<version>]`` heading doesn't render as a self-link).

Usage::

    python release_notes.py <version> <body_out_path> <github_output_path>

Writes the body to ``<body_out_path>`` and ``title=<...>`` to the file named by
``<github_output_path>`` (i.e. ``$GITHUB_OUTPUT``). If the version has no
CHANGELOG section, the title falls back to ``v<version>`` and the body is empty
(the workflow then relies on GitHub's auto-generated notes).
"""
from __future__ import annotations

import re
import sys


def extract(version: str, changelog: str) -> tuple[str, str]:
    lines = changelog.splitlines()
    start = None
    heading = ""
    for i, line in enumerate(lines):
        if line.startswith(f"## [{version}]"):
            start, heading = i, line
            break

    if start is None:
        return version, ""

    # Descriptive suffix after "## [version]", dropping a leading dash separator
    # (em-dash, en-dash, or hyphen) and surrounding whitespace.
    m = re.match(r"^## \[" + re.escape(version) + r"\]\s*[—–-]*\s*(.*)$", heading)
    suffix = m.group(1).strip() if m else ""
    title = f"{version} — {suffix}" if suffix else version

    body_lines: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## ["):
            break
        body_lines.append(line)
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()

    return title, "\n".join(body_lines)


def main() -> None:
    version, body_path, gh_output = sys.argv[1], sys.argv[2], sys.argv[3]
    with open("CHANGELOG.md", encoding="utf-8") as f:
        title, body = extract(version, f.read())
    with open(body_path, "w", encoding="utf-8") as f:
        f.write(body + ("\n" if body else ""))
    with open(gh_output, "a", encoding="utf-8") as f:
        f.write(f"title={title}\n")


if __name__ == "__main__":
    main()