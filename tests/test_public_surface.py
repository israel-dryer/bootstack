"""Guards for the curated top-level ``bootstack`` namespace.

The top level holds what you *compose a UI* with (widgets, App/Window, Signal,
dialog verbs, theme verbs). Everything you reference *by type to configure
behavior* lives in a submodule. These tests lock that contract in:

* the exact top-level set can't drift silently (update EXPECTED deliberately),
* every moved primitive is importable from its submodule AND absent from the
  top level.

Headless — only imports.
"""
from __future__ import annotations

import importlib

import pytest

import bootstack as bs

# The curated top-level surface. Keep in sync with src/bootstack/__init__.py
# __all__ — a change here must be a deliberate API decision.
EXPECTED_TOPLEVEL = {
    "__version__",
    # reactive state
    "Signal",
    # theme switching
    "set_theme", "toggle_theme",
    # dialog verbs
    "alert", "confirm", "ask_string", "ask_integer", "ask_float", "ask_date",
    "ask_date_range", "ask_item", "ask_color", "ask_font", "ask_filter",
    "ask_save_file", "ask_open_file", "ask_open_files", "ask_directory",
    # application & windows
    "App", "AppShell", "Window",
    # layout
    "HStack", "VStack", "Grid", "Card", "GroupBox", "Separator", "ScrollView",
    "SplitView", "SplitPane", "Accordion", "AccordionSection",
    # actions
    "Button", "ButtonGroup", "MenuButton", "CommandBar", "StatusBar",
    "ContextMenu", "ContextMenuItem",
    # inputs
    "TextField", "PasswordField", "NumberField", "PathField", "SpinnerField",
    "TextArea", "CodeEditor", "DateField", "TimeField", "Slider", "RangeSlider",
    # selection
    "Checkbox", "Switch", "ToggleButton", "ToggleGroup", "Radio",
    "RadioToggleButton", "RadioGroup", "Select", "SelectButton", "Calendar",
    # data display
    "Label", "Badge", "ProgressBar", "Gauge", "ListView", "DataTable",
    "Tree", "TreeNode",
    # media
    "Picture", "Gallery", "Carousel", "Avatar",
    # navigation
    "PageStack", "StackPage", "Tabs", "TabPage",
    # overlays
    "Tooltip", "toast", "Notification", "Snackbar", "snackbar",
    # forms
    "Form", "FormItem", "FieldItem", "GroupItem", "TabsItem", "TabItem",
}

# Primitives that must live in a submodule and NOT at the top level.
MOVED = {
    "bootstack.data": [
        "BaseDataSource", "MemoryDataSource", "SqliteDataSource", "FileDataSource",
        "FileSourceConfig", "DataSourceProtocol", "Record", "Primitive",
        "col", "any_of", "all_of",
    ],
    "bootstack.i18n": ["L", "LV"],
    "bootstack.validation": ["ValidationRule", "ValidationResult", "RuleType"],
    "bootstack.events": ["Event", "Subscription"],
    "bootstack.streams": ["Stream", "Handle"],
    "bootstack.scheduling": ["Schedule", "Job"],
    "bootstack.shortcuts": ["Shortcuts", "Shortcut", "get_shortcuts"],
    "bootstack.store": ["Store"],
    "bootstack.images": ["Image", "get_icon", "AppIcon", "list_icons"],
    "bootstack.errors": [
        "BootstackError", "UnknownEventError", "ParentResolutionError",
        "DuplicateIdError", "SerializationError", "NavigationError",
        "ThemeError", "StyleBuilderError",
    ],
    "bootstack.style": [
        "Theme", "get_theme", "get_theme_color", "get_themes",
        "get_font_families", "set_font_family", "update_font_token",
    ],
    "bootstack.types": [
        "AccentToken", "VariantToken", "SurfaceToken", "WidgetDensity",
        "BaseWidgetKwargs", "StyledKwargs", "Anchor", "Fill", "Side", "Sticky",
        "Padding", "WindowStyle", "LayoutKind", "AutoFlow",
        "ColumnSpec", "EditorType", "FormOptions", "Option", "OptionDict",
        "Icon", "IconSpec",
    ],
    # EditFilter demoted from top-level (Tk-coupled CodeEditor extension hook);
    # stays importable here for power users. See project_editfilter_public_api.
    "bootstack.widgets": ["PublicWidgetBase", "PublicContainer", "EditFilter"],
    "bootstack.dialogs": [
        "FormDialog", "Dialog", "DialogButton", "ColorChooserDialog",
        "ColorChoice", "FontDialog", "FontChoice", "FilterDialog",
    ],
}

_MOVED_FLAT = [(mod, name) for mod, names in MOVED.items() for name in names]


def test_toplevel_all_matches_expected():
    """The top-level __all__ must match the curated set exactly (no drift)."""
    assert set(bs.__all__) == EXPECTED_TOPLEVEL


def test_toplevel_all_resolves():
    """Every name in __all__ is actually present (no stale entries)."""
    missing = [n for n in bs.__all__ if not hasattr(bs, n)]
    assert missing == []


def test_no_duplicate_exports():
    assert len(bs.__all__) == len(set(bs.__all__))


@pytest.mark.parametrize("module, name", _MOVED_FLAT)
def test_moved_symbol_importable_from_submodule(module, name):
    mod = importlib.import_module(module)
    assert hasattr(mod, name), f"{module}.{name} should be importable"


@pytest.mark.parametrize("module, name", _MOVED_FLAT)
def test_moved_symbol_absent_from_toplevel(module, name):
    assert name not in bs.__all__, f"{name} should no longer be top-level"
    assert not hasattr(bs, name), f"bs.{name} should be gone (moved to {module})"


def test_demoted_helpers_not_public():
    """Image and get_current_app are demoted to internal."""
    for name in ("Image", "get_current_app", "IntlFormatter", "MessageCatalog"):
        assert name not in bs.__all__
        assert not hasattr(bs, name)


def test_internal_style_accessors_not_public():
    """The Tk-leaking engine accessors stay out of the public style surface."""
    import bootstack.style as style
    for name in ("get_style", "get_style_builder", "get_theme_provider"):
        assert name not in style.__all__, f"{name} should not be public in bootstack.style"
