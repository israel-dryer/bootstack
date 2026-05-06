---
title: Installation
---

# Installation

bootstack is a **framework** for building Tkinter applications with a modern design system and convenience APIs
(reactive state, icons, layout containers, localization, and more).

It runs anywhere Tk runs — Windows, macOS, and Linux — and installs like any other Python package.

---

## Requirements

- **Python 3.12 or newer**

- **Tk / Tcl**

  Tkinter ships with most Python distributions, but some minimal Linux installs omit Tk.

!!! tip "On Linux, install Tk if Tkinter is missing"
    - Debian/Ubuntu: `sudo apt-get install python3-tk`
    - Fedora: `sudo dnf install python3-tkinter`
    - Arch: `sudo pacman -S tk`

---

## Install with pip

bootstack is currently in **active alpha**, so pip won't install it by default — you need the `--pre` flag to opt in to pre-release versions:

```bash
python -m pip install --pre bootstack
```

If you’re upgrading:

```bash
python -m pip install --upgrade --pre bootstack
```

!!! note "Pinning to a specific alpha"
    Once stable releases ship, the `--pre` flag will no longer be required. To stay on the alpha line in the meantime, you can pin a specific version, e.g. `pip install bootstack==0.1.0a2`.

---

## Verify your installation

Create a quick smoke test:

```python
import bootstack as bs

app = bs.App()
bs.Label(app, text="Hello bootstack").pack(padx=20, pady=20)
app.mainloop()
```

If a window appears, you’re ready.

!!! link "Next: follow the [Quick Start](quick-start.md) to build your first small app."

---

## Included image support (Pillow)

bootstack includes Pillow as a dependency to support modern image workflows, including
theme-aware icons, DPI scaling, caching, and recoloring.

No additional installation is required.

!!! link "See [Icons & Imagery](../guides/icons.md) for details on image handling and icon behavior."

---

## Optional: Command-line tooling

bootstack includes an optional CLI that can scaffold projects, add views or dialogs, and help with
building and distribution.

You do **not** need the CLI to use bootstack, but it can simplify larger projects.

!!! link "See [Tooling → CLI](../tooling/cli.md) for available commands."

---

## Troubleshooting

### `_tkinter` / Tk not found

If you see errors like:

- `ModuleNotFoundError: No module named '_tkinter'`
- `TclError: ...`

then Tk is not installed or not visible to your Python interpreter.

Common fixes:

- **Windows**: reinstall Python using the official installer and ensure Tcl/Tk is selected.
- **macOS**: use the official Python installer from python.org or a distribution that bundles Tk support.
- **Linux**: install the Tk package for your distro (see the Linux tip above).

### Virtual environments

If Tk works in system Python but not in a venv, ensure:

- the venv was created from an interpreter that has Tk support.

---

## Next steps

- [Quick Start](quick-start.md) — build a minimal app
- [Guides](../guides/index.md) — recommended patterns and workflows
- [Widgets](../widgets/index.md) — available UI components
- [Capabilities](../guides/index.md) — framework features like signals and localization
- [Tooling](../tooling/cli.md) — CLI, project structure, and packaging
- [Architecture](../architecture/index.md) — Tk/ttk foundations (optional)
