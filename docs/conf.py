import importlib.metadata

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

project   = "bootstack"
author    = "Israel Dryer"
copyright = f"2026, {author}"

release = importlib.metadata.version("bootstack")
version = ".".join(release.split(".")[:2])

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_design",
    "sphinx_copybutton",
]

# ---------------------------------------------------------------------------
# Autodoc
# ---------------------------------------------------------------------------

autodoc_member_order        = "bysource"
autodoc_typehints           = "description"
autodoc_typehints_format    = "short"
autodoc_default_options     = {
    "members":          True,
    "undoc-members":    False,
    "show-inheritance": True,
}

autosummary_generate = True

# ---------------------------------------------------------------------------
# Napoleon (Google-style docstrings)
# ---------------------------------------------------------------------------

napoleon_google_docstring       = True
napoleon_numpy_docstring        = False
napoleon_include_init_with_doc  = False
napoleon_use_param              = False
napoleon_use_rtype              = False
napoleon_attr_annotations       = True

# ---------------------------------------------------------------------------
# Type hints
# ---------------------------------------------------------------------------

typehints_fully_qualified       = False
always_document_param_types     = False
typehints_document_rtype        = True

# ---------------------------------------------------------------------------
# Intersphinx
# ---------------------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# ---------------------------------------------------------------------------
# HTML / Shibuya theme
# ---------------------------------------------------------------------------

html_theme = "shibuya"

html_theme_options = {
    "github_url":  "https://github.com/israel-dryer/bootstack",
    "light_logo":  "_static/bootstack-logo-light.svg",
    "dark_logo":   "_static/bootstack-logo-dark.svg",
    "nav_links": [
        {
            "title": "Getting Started",
            "url": "getting-started/index",
            "children": [
                {"title": "Installation",     "url": "getting-started/installation",   "summary": "Install bootstack and its dependencies"},
                {"title": "Quick Start",      "url": "getting-started/quickstart",     "summary": "Build your first app in minutes"},
                {"title": "App Structures",   "url": "getting-started/app-structures", "summary": "Choose between App, AppShell, and Window"},
            ],
        },
        {
            "title": "Common Tasks",
            "url": "tasks/index",
            "children": [
                {"title": "Displaying Data",   "url": "tasks/displaying-data",   "summary": "Labels, badges, tables, trees, and gauges"},
                {"title": "Getting Input",     "url": "tasks/getting-input",     "summary": "Text fields, selects, sliders, and date pickers"},
                {"title": "Handling Actions",  "url": "tasks/handling-actions",  "summary": "Buttons, menus, and toolbars"},
                {"title": "Building Forms",    "url": "tasks/building-forms",    "summary": "Spec-driven forms with validation"},
                {"title": "Dialogs & Alerts",  "url": "tasks/dialogs",           "summary": "Modal dialogs, alerts, and quick prompts"},
                {"title": "Navigation & Pages","url": "tasks/navigation",        "summary": "Tabs, sidebars, and page stacks"},
                {"title": "Layout & Spacing",  "url": "tasks/layout",            "summary": "Stacks, grids, cards, and containers"},
            ],
        },
        {
            "title": "Going Deeper",
            "url": "deeper/index",
            "children": [
                {"title": "Signals",        "url": "deeper/signals",       "summary": "Reactive state and two-way binding"},
                {"title": "Events",         "url": "deeper/events",        "summary": "Binding, emitting, streams, and scheduling"},
                {"title": "Theming",        "url": "deeper/theming",       "summary": "Colors, variants, and custom themes"},
                {"title": "Typography",     "url": "deeper/typography",    "summary": "Font tokens and text styling"},
                {"title": "Icons",          "url": "deeper/icons",         "summary": "Built-in Bootstrap Icons catalog"},
                {"title": "Localization",   "url": "deeper/localization",  "summary": "Language catalogs and locale-aware formatting"},
                {"title": "Data Sources",   "url": "deeper/data-sources",  "summary": "SQLite, memory, and file backends"},
                {"title": "Validation",     "url": "deeper/validation",    "summary": "Field-level validators and error messages"},
                {"title": "Windowing",      "url": "deeper/windowing",     "summary": "Multi-window, modal, and custom chrome"},
                {"title": "Overlays",       "url": "deeper/overlays",      "summary": "Toast notifications and tooltips"},
            ],
        },
        {
            "title": "Production",
            "url": "production/index",
            "children": [
                {"title": "CLI & Tooling",  "url": "production/cli",          "summary": "Scaffold, run, and manage your project"},
                {"title": "Distribution",   "url": "production/distribution",  "summary": "Package with PyInstaller via bootstack build"},
                {"title": "Debugging",      "url": "production/debugging",     "summary": "Diagnose and fix common issues"},
                {"title": "App Settings",   "url": "production/app-settings",  "summary": "Configure themes, locale, and startup behavior"},
            ],
        },
        {
            "title": "API",
            "url": "api/index",
            "children": [
                {"title": "Actions",      "url": "api/actions",      "summary": "Button, ButtonGroup, MenuButton, ContextMenu"},
                {"title": "Inputs",       "url": "api/inputs",       "summary": "TextField, Slider, DateField, CodeEditor, and more"},
                {"title": "Selection",    "url": "api/selection",    "summary": "Checkbox, RadioGroup, ToggleGroup, Select, Calendar"},
                {"title": "Data Display", "url": "api/data-display", "summary": "Label, Badge, Tree, Table, ListView, Gauge"},
                {"title": "Layout",       "url": "api/layout",       "summary": "VStack, HStack, Grid, Card, Accordion, SplitView"},
                {"title": "Navigation",   "url": "api/navigation",   "summary": "AppShell, Tabs, SideNav, PageStack, Toolbar"},
                {"title": "Overlays",     "url": "api/overlays",     "summary": "Toast, Tooltip"},
                {"title": "Dialogs",      "url": "api/dialogs",      "summary": "All dialog types and module-level functions"},
                {"title": "Forms",        "url": "api/forms",        "summary": "Form, FormDialog, and Field"},
            ],
        },
    ],
}

html_static_path = ["_static"]
html_css_files   = ["custom.css"]
html_favicon     = "_static/favicon.ico"
html_title       = "bootstack"
html_short_title = "bootstack"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# Autodoc mock imports (unavailable on Linux CI runners)
# ---------------------------------------------------------------------------

autodoc_mock_imports = [
    "pywinstyles",
]
