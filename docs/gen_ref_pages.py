"""Generate API reference pages for bootstack widgets."""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

REF_DIR = Path("reference")
WIDGETS_DIR = REF_DIR / "widgets"

# Map widget names to their full module paths for mkdocstrings
# This avoids issues with lazy loading in bootstack.__init__
WIDGET_MODULES = {
    # Primitives
    "Badge": "bootstack.widgets.primitives.badge.Badge",
    "Button": "bootstack.widgets.primitives.button.Button",
    "CheckButton": "bootstack.widgets.primitives.checkbutton.CheckButton",
    "CheckToggle": "bootstack.widgets.primitives.checktoggle.CheckToggle",
    "Combobox": "bootstack.widgets.primitives.combobox.Combobox",
    "Entry": "bootstack.widgets.primitives.entry.Entry",
    "Frame": "bootstack.widgets.primitives.frame.Frame",
    "Label": "bootstack.widgets.primitives.label.Label",
    "LabelFrame": "bootstack.widgets.primitives.labelframe.LabelFrame",
    "MenuButton": "bootstack.widgets.primitives.menubutton.MenuButton",
    "Notebook": "bootstack.widgets.primitives.notebook.Notebook",
    "OptionMenu": "bootstack.widgets.primitives.optionmenu.OptionMenu",
    "PanedWindow": "bootstack.widgets.primitives.panedwindow.PanedWindow",
    "Progressbar": "bootstack.widgets.primitives.progressbar.Progressbar",
    "RadioButton": "bootstack.widgets.primitives.radiobutton.RadioButton",
    "RadioToggle": "bootstack.widgets.primitives.radiotoggle.RadioToggle",
    "Scale": "bootstack.widgets.primitives.scale.Scale",
    "Scrollbar": "bootstack.widgets.primitives.scrollbar.Scrollbar",
    "Separator": "bootstack.widgets.primitives.separator.Separator",
    "SizeGrip": "bootstack.widgets.primitives.sizegrip.SizeGrip",
    "Spinbox": "bootstack.widgets.primitives.spinbox.Spinbox",
    "TreeView": "bootstack.widgets.primitives.treeview.TreeView",
    # Composites
    "ButtonGroup": "bootstack.widgets.composites.buttongroup.ButtonGroup",
    "Calendar": "bootstack.widgets.composites.calendar.Calendar",
    "ContextMenu": "bootstack.widgets.composites.contextmenu.ContextMenu",
    "DateEntry": "bootstack.widgets.composites.dateentry.DateEntry",
    "DropdownButton": "bootstack.widgets.composites.dropdownbutton.DropdownButton",
    "Field": "bootstack.widgets.composites.field.Field",
    "FloodGauge": "bootstack.widgets.composites.floodgauge.FloodGauge",
    "Form": "bootstack.widgets.composites.form.Form",
    "LabeledScale": "bootstack.widgets.composites.labeledscale.LabeledScale",
    "ListItem": "bootstack.widgets.composites.list.listitem.ListItem",
    "ListView": "bootstack.widgets.composites.list.listview.ListView",
    "Meter": "bootstack.widgets.composites.meter.Meter",
    "NumericEntry": "bootstack.widgets.composites.numericentry.NumericEntry",
    "PageStack": "bootstack.widgets.composites.pagestack.PageStack",
    "PasswordEntry": "bootstack.widgets.composites.passwordentry.PasswordEntry",
    "PathEntry": "bootstack.widgets.composites.pathentry.PathEntry",
    "RadioGroup": "bootstack.widgets.composites.radiogroup.RadioGroup",
    "ScrolledText": "bootstack.widgets.composites.scrolledtext.ScrolledText",
    "ScrollView": "bootstack.widgets.composites.scrollview.ScrollView",
    "SelectBox": "bootstack.widgets.composites.selectbox.SelectBox",
    "SpinnerEntry": "bootstack.widgets.composites.spinnerentry.SpinnerEntry",
    "TableView": "bootstack.widgets.composites.tableview.TableView",
    "TextEntry": "bootstack.widgets.composites.textentry.TextEntry",
    "TimeEntry": "bootstack.widgets.composites.timeentry.TimeEntry",
    "Toast": "bootstack.widgets.composites.toast.Toast",
    "ToggleGroup": "bootstack.widgets.composites.togglegroup.ToggleGroup",
    "ToolTip": "bootstack.widgets.composites.tooltip.ToolTip",
    # Dialogs
    "Dialog": "bootstack.dialogs.dialog.Dialog",
    "MessageDialog": "bootstack.dialogs.message.MessageDialog",
    "MessageBox": "bootstack.dialogs.message.MessageBox",
    "QueryDialog": "bootstack.dialogs.query.QueryDialog",
    "QueryBox": "bootstack.dialogs.query.QueryBox",
    "ColorChooser": "bootstack.dialogs.colorchooser.ColorChooser",
    "ColorChooserDialog": "bootstack.dialogs.colorchooser.ColorChooserDialog",
    "ColorDropperDialog": "bootstack.dialogs.colordropper.ColorDropperDialog",
    "DateDialog": "bootstack.dialogs.datedialog.DateDialog",
    "FontDialog": "bootstack.dialogs.fontdialog.FontDialog",
    "FilterDialog": "bootstack.dialogs.filterdialog.FilterDialog",
    "FormDialog": "bootstack.dialogs.formdialog.FormDialog",
    # Core
    "App": "bootstack.runtime.app.App",
    "Toplevel": "bootstack.runtime.toplevel.Toplevel",
    "Style": "bootstack.style.style.Style",
}


def write_ref_page(path: Path, identifier: str, title: str | None = None):
    """Write a reference page for a single symbol."""
    with mkdocs_gen_files.open(path, "w") as f:
        if title:
            f.write(f"# {title}\n\n")
        f.write(f"::: {identifier}\n")


# Generate individual widget pages
items = sorted(WIDGET_MODULES.keys())
print(f"Generating API docs for {len(items)} symbols: {items}")

for name in items:
    identifier = WIDGET_MODULES[name]
    write_ref_page(WIDGETS_DIR / f"{name}.md", identifier, title=name)

# Generate widgets index page
with mkdocs_gen_files.open(WIDGETS_DIR / "index.md", "w") as f:
    f.write("# API Reference - Widgets\n\n")
    f.write("Auto-generated API reference for bootstack widgets.\n\n")

    # Group by category
    f.write("## Primitives\n\n")
    for name in sorted(n for n in items if "primitives" in WIDGET_MODULES[n]):
        f.write(f"- [{name}]({name}.md)\n")

    f.write("\n## Composites\n\n")
    for name in sorted(n for n in items if "composites" in WIDGET_MODULES[n]):
        f.write(f"- [{name}]({name}.md)\n")

    f.write("\n## Dialogs\n\n")
    for name in sorted(n for n in items if "dialogs" in WIDGET_MODULES[n]):
        f.write(f"- [{name}]({name}.md)\n")

    f.write("\n## Core\n\n")
    for name in sorted(n for n in items if "runtime" in WIDGET_MODULES[n] or "style.style" in WIDGET_MODULES[n]):
        f.write(f"- [{name}]({name}.md)\n")