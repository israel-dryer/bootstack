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
    "light_logo":  "_static/bootstack-logo-light.png",
    "dark_logo":   "_static/bootstack-logo-dark.png",
    "nav_links": [
        {"title": "Gallery",  "url": "gallery"},
        {"title": "GitHub",   "url": "https://github.com/israel-dryer/bootstack"},
    ],
}

html_static_path = ["_static"]
html_title       = "bootstack"
html_short_title = "bootstack"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# Autodoc mock imports (for CI — packages unavailable on Linux build runners)
# ---------------------------------------------------------------------------

autodoc_mock_imports = [
    "pywinstyles",
]
