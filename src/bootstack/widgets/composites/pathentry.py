"""Path entry field widget with file/directory chooser dialog.

Provides an entry field with a button that opens a file or directory chooser
dialog for selecting paths.
"""

from tkinter import filedialog
from typing import Any

from typing_extensions import Unpack

from bootstack.widgets.primitives.button import Button
from bootstack.widgets.composites.field import Field, FieldOptions
from bootstack.widgets.mixins import configure_delegate
from bootstack.widgets.types import FileDialogType, Master


class PathEntry(Field):
    """A path entry field widget with file/directory chooser dialog button.

    PathEntry extends the Field widget to provide a specialized input for file
    and directory paths. It includes a button that opens a native file/directory
    chooser dialog, and displays the selected path(s) in the entry field. The
    widget supports various dialog types including single file selection, multiple
    file selection, directory selection, and save file dialogs.
    """

    def __init__(
            self,
            master: Master = None,
            *,
            value: str | None = None,
            dialog: FileDialogType = "openfilename",
            dialog_options: dict[str, Any] | None = None,
            button_text: str = "Browse",
            label: str = None,
            message: str = None,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial path value to display in the entry field. Default is None
                (empty field). This is updated when a path is selected from the dialog.
            dialog: Type of file dialog to open. Default is "openfilename".
                Options:

                - 'openfilename': Single file selection (returns path string)
                - 'openfile': Single file selection (returns file object)
                - 'directory': Directory selection
                - 'openfilenames': Multiple file selection (returns paths)
                - 'openfiles': Multiple file selection (returns file objects)
                - 'saveasfile': Save file dialog (returns file object)
                - 'saveasfilename': Save file dialog (returns path string)

            dialog_options: Dictionary of options to pass to the file dialog.
                Common options: title, initialdir, initialfile, filetypes,
                defaultextension, multiple.
            button_text: Text to display on the browse button. Default is "Browse".
                Can be changed at runtime via `configure(button_text=...)`.
            label: Label text to display above the entry field (from FieldOptions).
            message: Message text to display below the field.

        Other Parameters:
            required: If True, field cannot be empty.
            accent: Accent token for the focus ring and active border.
            allow_blank: Allow empty input.
            cursor: Cursor style when hovering.
            font: Font for text display.
            foreground: Text color.
            initial_focus: If True, widget receives focus on creation.
            justify: Text alignment.
            show_message: If True, displays message area.
            padding: Padding around entry widget.
            takefocus: If True, widget accepts Tab focus.
            textvariable: Tkinter Variable to link with text.
            textsignal: Signal object for reactive updates.
            width: Width in characters.
        """
        self._dialog = dialog
        self._dialog_options = dialog_options
        self._dialog_result = None
        self._button_text = button_text
        self._prev_value: str | None = value

        super().__init__(master=master, label=label, message=message, value=value, **kwargs)

        self.insert_addon(
            Button,
            position="before",
            name="dialog-button",
            text=self._button_text,
            command=self._show_file_chooser
        )

    @property
    def dialog_button(self) -> Button | None:
        """Get the dialog button widget."""
        return self.addons.get('dialog-button')

    @property
    def dialog_result(self) -> str | tuple[str, ...] | None:
        """Get the raw result from the last file dialog operation.

        Returns a single path string for single-file dialogs, a tuple of
        paths for multi-file dialogs, or ``None`` if no selection was made.
        """
        return self._dialog_result

    # ------ Configuration Delegates ------

    @configure_delegate('dialog')
    def _delegate_dialog(self, value: FileDialogType = None):
        if value is None:
            return self._dialog
        else:
            self._dialog = value
        return None

    @configure_delegate('button_text')
    def _delegate_button_text(self, value: str = None):
        if value is None:
            return self._button_text
        else:
            self._button_text = value
            if self.dialog_button:
                self.dialog_button['text'] = value
        return None

    @configure_delegate('dialog_options')
    def _delegate_dialog_options(self, value: dict[str, Any] = None):
        if value is None:
            return self._dialog_options
        else:
            self._dialog_options = value
        return None

    def _show_file_chooser(self):
        """Open the file/directory chooser dialog and update the entry."""
        method_name = f"ask{self._dialog}"
        dialog_func = getattr(filedialog, method_name, None)

        if dialog_func is None:
            raise ValueError(f"Invalid dialog type `{self._dialog}`")

        result = dialog_func(**(self._dialog_options or {}))
        self._dialog_result = result

        # Format display text for multiple selections
        if isinstance(result, (tuple, list)):
            display_text = ", ".join(str(p) for p in result)
        else:
            display_text = result

        # Only update if a selection was made (result is truthy)
        if result:
            prev_value = self._prev_value
            self._prev_value = display_text

            # Set the value through the field's standard mechanism
            self.value = display_text

            # Emit <<Change>> on PathEntry (the composite) with full event data
            self.event_generate(
                '<<Change>>',
                data={
                    'value': display_text,
                    'prev_value': prev_value,
                    'text': display_text,
                    'dialog_result': self._dialog_result,
                },
                when="tail"
            )

