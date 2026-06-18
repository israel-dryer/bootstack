"""Internal dialog implementations.

The Bootstrap-styled dialog building blocks behind the public dialog API. The
curated public surface — the `alert` / `confirm` / `ask_*` verbs and the
`Dialog` / `FormDialog` / `FontDialog` / `ColorChooserDialog` /
`FilterDialog` classes — lives in `bootstack.dialogs`; import from there, not
from this package.

Modules here:

- `message` (MessageBox/MessageDialog): info/warning/error/question prompts
- `query` (QueryBox/QueryDialog): collect input (string, number, date, item, …)
- `colorchooser`: color picker
- `datedialog`: calendar date picker
- `fontdialog`: font selection
- `filterdialog`: multi-select filter dialog with search
- `dialog`: the base `Dialog` / `DialogButton`
"""
from .colorchooser import (
    ColorChooser,
    ColorChooserDialog,
)
from .dialog import Dialog, DialogButton
from .filterdialog import FilterDialog
from .formdialog import FormDialog
from .message import MessageDialog, MessageBox
from .query import QueryDialog, QueryBox
from .datedialog import DateDialog
from .fontdialog import FontDialog

__all__ = [
    # Base / core dialogs
    "Dialog",
    "DialogButton",
    "FilterDialog",
    "FormDialog",
    "MessageDialog",
    "QueryDialog",
    "DateDialog",
    "FontDialog",
    # Facades
    "MessageBox",
    "QueryBox",
    # Color tools
    "ColorChooser",
    "ColorChooserDialog",
]
