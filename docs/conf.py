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
# Only emit parameter type hints for params that have an explicit docstring
# entry. Dataclasses documented with attribute docstrings then render each field
# once (in the members list), instead of also getting a redundant, description-
# less "Parameters" block synthesized from the generated __init__ signature.
autodoc_typehints_description_target = "documented"
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
napoleon_use_param              = True
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
# Nitpicky cross-reference suppression
# ---------------------------------------------------------------------------
# `-n` flags every unresolved xref. Suppress targets that are intentionally
# outside the cross-referenced public API so the nitpicky build stays focused
# on real broken links: stdlib typing constructs, the deliberately-hidden
# Tkinter layer, private framework internals (``_core``/``_impl`` and any
# leading-underscore name), and bare ``TypeVar``s used in generics.
nitpick_ignore_regex = [
    (r"py:.*", r"typing\..*"),
    (r"py:.*", r"tkinter\..*"),
    (r"py:.*", r"tk\..*"),
    (r"py:.*", r".*\._core\..*"),
    (r"py:.*", r".*\._impl\..*"),
    (r"py:.*", r"(?:.*\.)?_[A-Za-z]\w*$"),  # private leading-underscore names
    (r"py:.*", r".*\.T$"),                   # bare TypeVars (generic Signal/Stream)
]

# ---------------------------------------------------------------------------
# HTML / Shibuya theme
# ---------------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/israel-dryer/bootstack",
    "logo": {
        "image_light": "_static/bootstack-logo-light.svg",
        "image_dark":  "_static/bootstack-logo-dark.svg",
    },
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links", "theme-switcher"],
    "secondary_sidebar_items": ["page-toc"],
    "navigation_with_keys": True,
    "show_nav_level": 2,
}

html_static_path = ["_static"]
templates_path   = ["_templates"]
html_css_files   = ["custom.css"]
html_favicon     = "_static/favicon.ico"
html_title       = "bootstack"
html_short_title = "bootstack"

# Hide source exposure — the framework abstracts its internals, so we don't
# surface the reST page source ("View page source") or per-page source copies.
# (`viewcode` is also intentionally omitted from extensions, so there are no
# `[source]` links into the private `_impl`/`_runtime` modules either.)
html_show_sourcelink = False
html_copy_source     = False

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# Autodoc mock imports (unavailable on Linux CI runners)
# ---------------------------------------------------------------------------

autodoc_mock_imports = [
    "pywinstyles",
]
