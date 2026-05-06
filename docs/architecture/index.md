# Architecture

The **Architecture** section explains how bootstack is structured at a foundational level — the Tk/ttk runtime model, the enhancements bootstack makes to it, and the system-level behaviors that underpin every widget and application.

If you're trying to build an interface, start with [Guides](../guides/index.md). Architecture pages explain *why* things behave the way they do.

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

Many concepts described here originate in Tk itself: the event loop, geometry managers, widget lifecycles, and windowing behavior. External resources such as Python's `tkinter` documentation and the TkDocs tutorial cover *how Tk works*. This section explains **how bootstack expects you to work with Tk** — and where bootstack extends or replaces the defaults.

---

## Topics

- **[Tk vs ttk](tk-vs-ttk.md)** — what each layer provides and when bootstack uses which
- **[Event Loop](event-loop.md)** — how the Tk event loop works and what bootstack adds
- **[Events & Bindings](events-and-bindings.md)** — event delivery, binding scopes, virtual events
- **[Geometry & Layout](geometry-and-layout.md)** — pack, grid, and place at the Tk level
- **[Widget Lifecycle](widget-lifecycle.md)** — creation, configuration, and destruction
- **[Styling Internals](ttk-styles-elements.md)** — ttk styles, elements, and how bootstack themes map to them
- **[Images & DPI](images-and-dpi.md)** — image handling, DPI awareness, and scaling
- **[Windows](windows.md)** — top-level windows and modality

Together, these topics define the foundation on which all bootstack applications are built.