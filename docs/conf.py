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
    "sphinx_design",
    "sphinx_copybutton",
]

# ---------------------------------------------------------------------------
# Autodoc
# ---------------------------------------------------------------------------

autodoc_member_order        = "groupwise"
# Group members by kind, leading with state (attributes/properties) before
# behavior (methods) — the pandas/NumPy convention. Sphinx 9.1's default
# (non-legacy) autodoc ranks groupwise members by each item's
# `_groupwise_order_key`, where property (60) sorts after method (50), so methods
# would lead. Override those keys so state-bearing members sort first; class
# methods keep priority within the method group (they act as alt constructors).
from sphinx.ext.autodoc import _property_types as _autodoc_pt  # noqa: E402


def _state_first_order_key(self) -> int:
    obj_type = self.obj_type
    if obj_type in ("attribute", "property"):
        return 20
    if obj_type == "data":
        return 10
    if obj_type == "method":
        if getattr(self, "is_classmethod", False):
            return 48
        if getattr(self, "is_staticmethod", False):
            return 49
        return 50
    if obj_type == "exception":
        return 5
    if obj_type == "class":
        return 30
    if obj_type == "type":
        return 70
    return 55  # function / decorator / anything else


for _pt_cls in (
    _autodoc_pt._ClassDefProperties,
    _autodoc_pt._FunctionDefProperties,
    _autodoc_pt._AssignStatementProperties,
    _autodoc_pt._TypeStatementProperties,
):
    _pt_cls._groupwise_order_key = property(_state_first_order_key)

autodoc_typehints           = "description"
autodoc_typehints_format    = "short"
# Only emit parameter type hints for params that have an explicit docstring
# entry. Dataclasses documented with attribute docstrings then render each field
# once (in the members list), instead of also getting a redundant, description-
# less "Parameters" block synthesized from the generated __init__ signature.
autodoc_typehints_description_target = "documented"
# Render type references with their short (unqualified) name while keeping the
# link — so resolved aliases show `IconPosition`, not `bootstack.types.IconPosition`.
python_use_unqualified_type_names = True
autodoc_default_options     = {
    "members":          True,
    "undoc-members":    False,
    "show-inheritance": True,
}

autosummary_generate = True

# Disambiguate stub filenames that differ only by case — they collide on
# case-insensitive filesystems (Windows/macOS). The message surfaces pair a
# class with a same-name verb: `Snackbar`/`snackbar` and the `toast` verb.
autosummary_filename_map = {
    "bootstack.toast": "bootstack.toast-verb",
    "bootstack.snackbar": "bootstack.snackbar-verb",
}

# Single backticks in docstrings render as inline code (the project convention)
# and, unlike the default interpreted-text role, are colon-safe (e.g. `h:mm`).
default_role = "code"

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
# Type hints / aliases
# ---------------------------------------------------------------------------
# Typehints render via CORE autodoc (NOT `sphinx_autodoc_typehints`): core
# autodoc honors `autodoc_type_aliases` and emits each alias as a cross-reference
# to its `.. py:type::` target, where `sphinx_autodoc_typehints` printed it as
# inert text. PEP 604 unions (`A | B`) render natively from the source form.
#
# Exported public type aliases therefore render as their NAME (not the expanded
# `Literal[...]`/union), linked to the API-reference page that documents them —
# where the allowed values live. This keeps widget signatures concise and the
# token vocabulary discoverable/importable.
#
# CONTRACT: every name here MUST have a `.. py:type::` target on a public page,
# or the nitpicky (`-n`) build fails on the dangling xref — which keeps this map
# and the alias docs in sync. Only EXPORTED aliases (in a public `__all__`) are
# listed; non-exported internal aliases (e.g. `AccordionVariant`, `Region`)
# deliberately keep expanding inline, since they are not part of the importable
# public vocabulary.
autodoc_type_aliases = {
    # Map each alias to its FULLY-QUALIFIED name so autodoc emits a cross-ref to
    # the `.. py:type::` target; `autodoc_typehints_format = "short"` then renders
    # just the short name as the link text.
    **{n: f"bootstack.types.{n}" for n in (
        "AccentToken", "VariantToken", "SurfaceToken", "WindowStyle",
        "WidgetDensity", "WidgetState", "Anchor", "Side", "Fill", "Sticky",
        "LayoutKind", "AutoFlow", "Padding", "Orient", "Justify", "Direction",
        "Relief", "CompoundMode", "BorderMode", "EditorType",
        "AccordionVariant", "Region", "ButtonVariant", "IconPosition",
        "SelectionMode", "ExportScope", "ExportFormat",
    )},
    **{n: f"bootstack.events.{n}" for n in (
        "ChangeReason", "ChangeMethod", "ChangeKind",
    )},
    "RuleType": "bootstack.validation.RuleType",
    "ThemeMode": "bootstack.style.ThemeMode",
    "SeverityToken": "bootstack.dialogs.SeverityToken",
    **{n: f"bootstack.data.{n}" for n in ("Record", "Primitive")},
}

# Sphinx 9.1: `autodoc_type_aliases` substitutes each alias with a
# `TypeAliasForwardRef(fqn)` object. Sphinx only unwraps it to a clean reference
# when it is the WHOLE annotation; nested inside a union (`X | None`) it instead
# leaks its repr (`TypeAliasForwardRef('bootstack.types.X')`) into the rendered
# type. Give each instance a `__module__`/`__qualname__` derived from its name so
# the stringify/restify machinery renders it as an ordinary class reference —
# which links to the alias's `.. py:type::` target — wherever it appears.
from sphinx.util.inspect import TypeAliasForwardRef as _TypeAliasForwardRef
if not getattr(_TypeAliasForwardRef, "_bs_patched", False):
    _bs_orig_taref_init = _TypeAliasForwardRef.__init__

    def _bs_taref_init(self, name):
        _bs_orig_taref_init(self, name)
        module, _, qualname = name.rpartition(".")
        self.__module__ = module or "builtins"
        self.__qualname__ = qualname or name

    _TypeAliasForwardRef.__init__ = _bs_taref_init
    _TypeAliasForwardRef._bs_patched = True

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
    "announcement": (
        "bootstack is in <strong>pre-release</strong> — the API may still "
        "change before 1.0. Install with <code>pip install --pre bootstack</code>."
    ),
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
    "show_nav_level": 1,
}

html_static_path = ["_static"]
# Files copied verbatim to the site root. CNAME pins the bootstack.org custom
# domain on GitHub Pages — without it, each deploy drops the custom domain.
html_extra_path  = ["CNAME"]
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

exclude_patterns = ["_build", "_dev", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------------------
# Autodoc mock imports (unavailable on Linux CI runners)
# ---------------------------------------------------------------------------

autodoc_mock_imports = [
    "pywinstyles",
]
