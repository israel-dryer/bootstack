"""Widget package for bootstack.

Public widgets are lazily importable from this package — e.g.
`from bootstack.widgets import Button` — mirroring the canonical
`import bootstack as bs; bs.Button` access. Resolution is lazy (PEP 562)
so importing the package does not eagerly pull in every widget module.
"""
from typing import Any

# Public widget-area name -> defining submodule (relative to this package).
# Single source of truth for the runtime namespace below.
_EXPORTS: dict[str, str] = {
    # Application & windows
    "App": "app", "AppShell": "appshell", "Window": "window",
    # Layout
    "Row": "stacks", "Column": "stacks", "Spacer": "stacks",
    "Grid": "grid", "Card": "card",
    "GroupBox": "groupbox", "Divider": "divider", "ScrollView": "scrollview",
    "SplitView": "splitview", "SplitPane": "splitview",
    "Accordion": "expander", "AccordionSection": "expander",
    # Actions
    "Button": "button", "ButtonGroup": "buttongroup", "MenuButton": "menubutton",
    "Toolbar": "toolbar", "StatusBar": "statusbar",
    "ContextMenu": "contextmenu", "ContextMenuItem": "contextmenu",
    # Inputs
    "TextField": "textfield", "PasswordField": "passwordfield",
    "NumberField": "numberfield", "PathField": "pathfield",
    "SpinnerField": "spinnerfield", "TextArea": "textarea", "CodeEditor": "codeeditor",
    "DateField": "datefield", "TimeField": "timefield",
    "Slider": "slider", "RangeSlider": "slider",
    "EditFilter": "_impl.composites.textarea.filter",
    # Selection
    "Checkbox": "boolean_controls", "Switch": "boolean_controls",
    "ToggleButton": "boolean_controls", "ToggleGroup": "togglegroup",
    "Radio": "radio_variants", "RadioToggleButton": "radio_variants",
    "RadioGroup": "radiogroup", "Select": "select", "SelectButton": "selectbutton",
    "Calendar": "calendar",
    # Data display
    "Label": "label", "Badge": "label", "Picture": "picture", "Gallery": "gallery",
    "Carousel": "carousel", "Avatar": "avatar", "ProgressBar": "progressbar",
    "Gauge": "gauge", "ListView": "listview", "DataTable": "datatable", "Tree": "tree",
    "Chart": "chart",
    # Navigation
    "PageStack": "pagestack", "StackPage": "pagestack",
    "Tabs": "tabs", "TabPage": "tabs",
    # Overlays
    "Tooltip": "tooltip", "Toast": "toast", "toast": "toast",
    # Forms
    "Form": "form", "FormItem": "form", "FieldItem": "form", "GroupItem": "form",
    "TabsItem": "form", "TabItem": "form",
    # Extension base classes (for building custom public widgets)
    "PublicWidgetBase": "_core.base", "PublicContainer": "_core.container",
    # Dialogs
    "alert": "dialogs", "confirm": "dialogs", "ask_string": "dialogs",
    "ask_integer": "dialogs", "ask_float": "dialogs", "ask_date": "dialogs",
    "ask_date_range": "dialogs", "ask_item": "dialogs", "ask_color": "dialogs",
    "ask_font": "dialogs", "ask_filter": "dialogs", "FormDialog": "dialogs",
    "Dialog": "dialogs", "DialogButton": "dialogs", "ColorChooserDialog": "dialogs",
    "ColorChoice": "dialogs", "FontDialog": "dialogs", "FontChoice": "dialogs",
    "FilterDialog": "dialogs",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str) -> Any:
    """Lazily import and cache a public widget by name (PEP 562)."""
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    obj = getattr(importlib.import_module(f"bootstack.widgets.{module}"), name)
    globals()[name] = obj  # cache so subsequent lookups skip __getattr__
    return obj


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))
