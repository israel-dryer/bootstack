"""Path entry field widget with file/directory chooser dialog."""

from tkinter import filedialog
from typing import Any, Literal

from typing_extensions import Unpack

from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.composites.field import Field, FieldOptions
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master

PathMode = Literal['open', 'open_multiple', 'save', 'directory']

_MODE_TO_DIALOG = {
    'open':          filedialog.askopenfilename,
    'open_multiple': filedialog.askopenfilenames,
    'save':          filedialog.asksaveasfilename,
    'directory':     filedialog.askdirectory,
}


class PathEntry(Field):
    """A path entry field with a browse button that opens a native dialog."""

    def __init__(
            self,
            master: Master = None,
            *,
            value: str | None = None,
            mode: PathMode = 'open',
            dialog_title: str | None = None,
            start_dir: str | None = None,
            file_filters: list[tuple[str, str]] | None = None,
            default_extension: str | None = None,
            default_filename: str | None = None,
            label: str = None,
            message: str = None,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial path value. Updated when the user picks a path.
            mode: Dialog type — `'open'` (default), `'open_multiple'`,
                `'save'`, or `'directory'`.
            dialog_title: Title shown in the native picker window.
            start_dir: Directory the dialog opens in.
            file_filters: File type filters, e.g. `[('Images', '*.png *.jpg')]`.
                Not used for `'directory'` mode.
            default_extension: Extension appended automatically if the user
                omits it. `'save'` mode only.
            default_filename: Suggested filename pre-filled in the dialog.
                `'save'` mode only.
            label: Label displayed above the field.
            message: Hint text displayed below the field.
        """
        self._mode = mode
        self._dialog_title = dialog_title
        self._start_dir = start_dir
        self._file_filters = file_filters
        self._default_extension = default_extension
        self._default_filename = default_filename
        self._dialog_result = None
        self._prev_value: str | None = value

        super().__init__(master=master, label=label, message=message, value=value, **kwargs)

        self.insert_addon(
            Button,
            position="after",
            name="dialog-button",
            icon="folder",
            icon_only=True,
            command=self._show_file_chooser
        )

    @property
    def dialog_button(self) -> Button:
        """The browse button widget."""
        return self.addons.get('dialog-button')

    @property
    def dialog_result(self) -> str | tuple[str, ...] | None:
        """Raw result from the most recent dialog (string or tuple of strings)."""
        return self._dialog_result

    def _build_dialog_kwargs(self) -> dict[str, Any]:
        """Assemble the kwargs dict for the native dialog call."""
        opts: dict[str, Any] = {}
        if self._dialog_title is not None:
            opts['title'] = self._dialog_title
        if self._start_dir is not None:
            opts['initialdir'] = self._start_dir
        if self._file_filters is not None:
            opts['filetypes'] = self._file_filters
        if self._default_extension is not None:
            opts['defaultextension'] = self._default_extension
        if self._default_filename is not None:
            opts['initialfile'] = self._default_filename
        return opts

    # ------ Configuration delegates ------

    @configure_delegate('mode')
    def _delegate_mode(self, value: PathMode = None):
        """Get or set the dialog mode."""
        if value is None:
            return self._mode
        self._mode = value

    @configure_delegate('dialog_title')
    def _delegate_dialog_title(self, value: str = None):
        if value is None:
            return self._dialog_title
        self._dialog_title = value

    @configure_delegate('start_dir')
    def _delegate_start_dir(self, value: str = None):
        if value is None:
            return self._start_dir
        self._start_dir = value

    @configure_delegate('file_filters')
    def _delegate_file_filters(self, value: list = None):
        if value is None:
            return self._file_filters
        self._file_filters = value

    @configure_delegate('default_extension')
    def _delegate_default_extension(self, value: str = None):
        if value is None:
            return self._default_extension
        self._default_extension = value

    @configure_delegate('default_filename')
    def _delegate_default_filename(self, value: str = None):
        if value is None:
            return self._default_filename
        self._default_filename = value

    def _show_file_chooser(self):
        """Open the native dialog and update the entry with the selected path."""
        dialog_func = _MODE_TO_DIALOG.get(self._mode)
        if dialog_func is None:
            raise ValueError(f"Invalid mode {self._mode!r}")

        result = dialog_func(**self._build_dialog_kwargs())
        self._dialog_result = result

        if isinstance(result, (tuple, list)):
            display_text = ", ".join(str(p) for p in result)
        else:
            display_text = result

        if result:
            prev_value = self._prev_value
            self._prev_value = display_text
            self.value = display_text
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