# Platform

The **Platform** section explains how Tk and ttk work underneath bootstack — the runtime model, event system, styling architecture, and system-level behaviors that apply to every widget you use.

If you're trying to build an interface, start with [Guides](../guides/index.md). Platform pages explain *why* things behave the way they do.

If you're new to Tk or ttk, these pages will help you build a mental model. If you already know Tk, this section explains what bootstack standardizes, extends, or intentionally constrains.

---

## How to use this section

Start here if you want to understand:

- how the event loop and event delivery work
- how widgets are created, updated, and destroyed
- how layout and geometry behave at runtime
- how ttk styles and elements are composed
- how images, fonts, and DPI are handled

For day-to-day workflow concerns — the CLI, project layout, packaging, debugging, performance — see [Tooling](../tooling/cli.md) and the relevant Guides.

For exact APIs, see the [API Reference](../reference/index.md).

---

## Relationship to Tk and ttk

Many concepts described here originate in Tk itself: the event loop, geometry managers, widget lifecycles, and windowing behavior. External resources such as Python's `tkinter` documentation and the TkDocs tutorial cover *how Tk works*. The Platform section explains **how bootstack expects you to work with Tk**.

---

## Platform topics

- **Fundamentals** — Tk vs ttk, the event loop, events and bindings, widget lifecycle, geometry and layout
- **Styling internals** — ttk styles and elements
- **Windows** — top-level windows and modality
- **Images & DPI** — image handling, DPI awareness, scaling

Together, these topics define the foundation on which all bootstack applications are built.
