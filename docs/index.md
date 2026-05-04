---
title: Home
---

# bootstack

**bootstack** is a batteries-included desktop application framework for Python, built on Tk. It grew out of [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) — which brought Bootstrap-style theming to ttk widgets — and bundles the layers you'd expect from a modern framework around it: app scaffolding, layout containers, semantic styling, reactive signals, forms and validation, i18n, a data layer, and a CLI for scaffolding and packaging.

The aim is to take you from `pip install` to a working, themed application without wiring those pieces together yourself or dropping down to raw Tk geometry calls.

---

## What bootstack provides

- a structured application root (`App`, `AppShell`)
- container-first layout (`PackFrame`, `GridFrame`, `ScrollView`)
- a design system with semantic colors, variants, and typography
- optional reactivity via signals
- forms and validation, localization, icons, and theming as first-class concerns
- a CLI for scaffolding new projects and packaging applications

These pieces are designed to work together. You can adopt them incrementally, but most of the leverage comes from following the framework's conventions for layout, styling, and state.

---

## How the documentation is organized

The documentation is structured by intent, not by inheritance or module layout.

### Getting Started

Create your first bootstack application and learn the core mental model.

→ [Start here if you're new](getting-started/index.md)

### Guides

Workflow-oriented documentation that shows how to build real applications:
layout patterns, reactivity, styling, localization, and structure.

### Widgets

Practical documentation for each widget: when to use it, how it behaves, and how it fits into the framework.

### Design System

Semantic colors, variants, typography, icons, and theming.

### Platform

How Tk and ttk work under the hood — behavior, constraints, and mechanics rather than usage patterns.

### Capabilities

Reference pages for framework features such as signals, localization, layout properties, and state handling — what each capability is and how it's defined.

### Tooling

The CLI, project structure, and packaging — everything you need to scaffold, run, and distribute a bootstack application.

### API Reference

Auto-generated reference for classes, methods, and functions.

### Showcase

Example applications and a gallery of what's been built with bootstack.

---

## Where to start

If you're new to bootstack:

1. Begin with **Getting Started**
2. Read the **Guides** relevant to your task
3. Refer to **Widgets** for specifics
4. Reach for **Capabilities** and **Platform** when you need deeper understanding
5. See **Tooling** when you're ready to ship

If you're coming from Tkinter, the layout, styling, and state conventions are where bootstack diverges most — those are worth reading before reaching for the API reference.
