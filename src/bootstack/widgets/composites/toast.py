
from bootstack._runtime.toplevel import Toplevel
from typing import Any, Callable, Sequence

from typing_extensions import TypedDict, Unpack

from bootstack._runtime.window_utilities import WindowPositioning


class IconSpec(TypedDict, total=False):
    """Icon configuration for toast."""
    name: str
    size: int | None
    color: str | None


class ToastConfig(TypedDict, total=False):
    """Configuration options for Toast widget."""
    title: str | None
    icon: str | IconSpec | None
    message: str | None
    memo: str | None
    duration: int | None
    buttons: Sequence[dict[str, Any]] | None
    show_close_button: bool
    accent: str | None
    position: str | None
    alert: bool
    on_dismissed: Callable[[Any], Any] | None


class Toast:
    """A notification toast widget that displays temporary messages.

    Toast notifications appear in a small window, typically in the corner of the screen,
    and can display a title, message, icon, buttons, and optional metadata. They can be
    configured to auto-dismiss after a duration or remain visible until manually closed.
    """

    def __init__(
            self,
            *,
            title: str | None = None,
            icon: str | IconSpec | None = None,
            message: str | None = None,
            memo: str | None = None,
            duration: int | None = None,
            buttons: Sequence[dict[str, Any]] | None = None,
            show_close_button: bool = True,
            accent: str | None = None,
            position: str | None = None,
            alert: bool = False,
            on_dismissed: Callable[[Any], Any] | None = None,
    ) -> None:
        """Initialize a Toast notification.

        Args:
            title: Title text. Displayed with a larger font when no message is
                provided; otherwise appears as the header with message below.
            icon: Icon name string or `IconSpec` dict with `name`, `size`, and
                `color` keys.
            message: Main message text. Displayed in header when no title; shown
                below the title separator when both are provided.
            memo: Small metadata text in the header (e.g., "5 mins ago"). Muted styling.
            duration: Auto-dismiss delay in milliseconds. If None, stays until closed.
            buttons: Sequence of button option dicts. Each dict accepts any bootstack
                Button kwargs. Button press triggers `on_dismissed` before closing.
            show_close_button: Whether to show the close (×) button. Default True.
            accent: Accent token for the container (e.g., 'primary', 'danger'). If
                None, uses the default background.
            position: Tkinter geometry string (e.g., '-25-75'). If None, uses
                platform defaults (bottom-right on Windows/macOS, top-right on X11).
            alert: If True, plays a system bell when shown.
            on_dismissed: Callback invoked on dismiss. Receives the button options
                dict when dismissed via a button, or None otherwise.
        """
        self._config_keys = {'title', 'icon', 'message', 'memo', 'duration', 'buttons', 'show_close_button',
                             'accent', 'position', 'alert', 'on_dismissed'}

        # initialized configuration
        self._title = title
        self._icon = icon
        self._message = message
        self._memo = memo
        self._duration = duration
        self._buttons = buttons
        self._show_close_button = show_close_button
        self._accent = accent
        self._position = position
        self._alert = alert
        self._on_dismissed = on_dismissed

        # top level widget
        self._toplevel: Toplevel | None = None

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a configuration option using dictionary syntax."""
        self.configure(**{key: value})

    def __getitem__(self, key: str) -> Any:
        """Get a configuration option using dictionary syntax."""
        return self.cget(key)

    def _handle_on_dismissed(self, data: Any = None) -> None:
        """Invoke the on_dismissed callback if configured."""
        if self._on_dismissed:
            self._on_dismissed(data)

    def configure(
            self,
            option: str | None = None,
            **kwargs: Unpack[ToastConfig]
    ) -> tuple[str, str, str, None, Any] | None:
        """Configure toast options.

        Args:
            option: If provided, returns the configuration for this option.
            **kwargs: Configuration options to set.

        Returns:
            Configuration tuple if option provided, otherwise None.
        """
        if option is not None:
            if option in self._config_keys:
                attr = f"_{option}"
                value = getattr(self, attr)
                # returns in the expected tkinter.configure format
                return option, option, option.capitalize(), None, value
            else:
                raise AttributeError(f"'{option}' is not a valid option")

        if kwargs:
            for key, value in kwargs.items():
                if key in self._config_keys:
                    attr = f"_{key}"
                    setattr(self, attr, value)
                else:
                    raise AttributeError(f"'{key}' is not a valid option")
        return None

    def cget(self, option: str) -> Any:
        """Get the value of a configuration option.

        Args:
            option: The configuration option name.

        Returns:
            The value of the configuration option.
        """
        if option in self._config_keys:
            attr = f"_{option}"
            return getattr(self, attr)
        else:
            raise AttributeError(f"'{option}' is not a valid option")

    def show(self, merge: bool = True, **options: Unpack[ToastConfig]) -> None:
        """Display the toast.

        If options are provided, they are merged with the existing toast configuration. If you do not want this
        behavior, set the merge flag to False, or create a new toast instance.

        Args:
            merge: If True, merge options with existing configuration. If False, clear existing options first.
            **options: Configuration options to set before showing.
        """
        if not merge:
            self._clear_options()

        self.configure(**options)
        self._build_toast()
        if self._toplevel:
            self._toplevel.deiconify()

    def _clear_options(self) -> None:
        """Clear all configuration options to their default values."""
        self._title = None
        self._icon = None
        self._message = None
        self._memo = None
        self._duration = None
        self._buttons = None
        self._show_close_button = True
        self._accent = None
        self._position = None
        self._alert = False
        self._on_dismissed = None

    def hide(self) -> None:
        """Hide the toast and trigger the on_dismissed callback."""
        if self._toplevel:
            self._toplevel.destroy()
        self._handle_on_dismissed(None)

    def destroy(self) -> None:
        """Destroy the toast widget and cleanup resources."""
        if hasattr(self, '_toplevel') and self._toplevel:
            self._toplevel.destroy()
        self._toplevel = None

    def _build_toast(self) -> None:
        import bootstack as bs
        # ----- Configuration Options -------

        has_title = self._title is not None
        has_title_and_message = has_title and self._message is not None
        resolved_title_font = "label" if has_title else "body"
        muted_foreground = "background[muted]" if self._accent is None else f"{self._accent}[muted]"

        # ------ Toplevel setup ------

        # bootstack.Toplevel applies MacWindowStyle 'help none' on Aqua
        # via windowtype='tooltip', so toasts render chromeless on Mac
        # (overrideredirect alone is silently skipped on Aqua per the
        # project's BaseWindow guard). Win/Linux keep the overrideredirect
        # path. Topmost + alpha are passed as kwargs so the Toplevel sets
        # them at the right moment in its setup pipeline.
        top = Toplevel(
            overrideredirect=True,
            topmost=True,
            alpha=0.97,
            windowtype='tooltip',
        )
        top.minsize(400, 30)

        # ------ Toast Layout ------

        container = bs.Frame(top, padding=4, accent=self._accent)
        container.pack(fill='both', expand=True)

        header = bs.Frame(container, padding=(8, 0, 0, 0))
        header.pack(side='top', fill='x')

        # icon
        if self._icon:
            bs.Label(header, icon=self._icon).pack(side='left', padx=(0, 8))

        # title
        bs.Label(
            header,
            text=self._title if has_title else self._message,
            font=resolved_title_font,
            wraplength=380,
            justify='left',
        ).pack(side='left', fill='x')

        # close
        if self._show_close_button:
            bs.Button(
                header,
                icon="x",
                accent=muted_foreground,
                variant="ghost",
                style_options={"icon_only": True},
                command=self.hide
            ).pack(side='right')

        # memo
        if self._memo:
            bs.Label(
                header,
                text=self._memo,
                font="caption",
                accent=muted_foreground,
            ).pack(side='right', pady=8, padx=(0, 0 if self._show_close_button else 12))

        # message
        if has_title_and_message:
            bs.Separator(container).pack(side='top', fill='x')
            bs.Label(
                container,
                text=self._message,
                wraplength=400,
                justify='left'
            ).pack(side='top', fill='x', pady=8, padx=8)

        # buttons
        if self._buttons:
            def execute_command(options: dict[str, Any], fn: Callable[[], None] | None = None) -> Callable[[], None]:
                def inner() -> None:
                    if fn:
                        fn()
                    self._handle_on_dismissed(options)
                    top.destroy()

                return inner

            bs.Separator(container).pack(side='top', fill='x', pady=4)
            button_frame = bs.Frame(container)
            button_frame.pack(side='top', fill='x')

            for i, button_options in enumerate(self._buttons):
                func = button_options.get('command', None)
                button_opts = {k: v for k, v in button_options.items() if k != 'command'}
                bs.Button(
                    button_frame,
                    **button_opts,
                    command=execute_command(button_options, func)
                ).grid(column=i, row=0, sticky="ew")

        # ------ Positioning -------

        # Deiconify off-screen first so the geometry manager runs a full
        # layout pass on a mapped window. winfo_height() returns 1 on a
        # withdrawn window, causing the toast to be placed with ~0 height
        # and therefore positioned flush against the screen edge.
        top.deiconify()
        top.geometry(
            f"+{top.winfo_screenwidth() * 2}+{top.winfo_screenheight() * 2}"
        )
        top.update_idletasks()

        # Apply positioning using WindowPositioning utilities
        if self._position:
            # Support legacy geometry strings (e.g., "-25-75")
            if self._position.startswith(('+', '-')):
                # Legacy geometry string - use directly
                top.geometry(self._position)
            else:
                # New positioning - assume it's a corner specification
                # (future enhancement: could support more complex positioning)
                top.geometry(self._position)
        else:
            # Default positioning based on platform
            winsys = top.tk.call('tk', 'windowingsystem')
            if winsys in ['win32', 'aqua']:
                # Bottom-right corner
                WindowPositioning.position_anchored(
                    window=top,
                    anchor_to="screen",
                    parent=None,
                    anchor_point="se",
                    window_point="se",
                    offset=(-25, -75),
                    auto_flip=False,
                    ensure_visible=True
                )
            else:
                # Top-right corner for X11
                WindowPositioning.position_anchored(
                    window=top,
                    anchor_to="screen",
                    parent=None,
                    anchor_point="ne",
                    window_point="ne",
                    offset=(-25, 25),
                    auto_flip=False,
                    ensure_visible=True
                )

        # ------ Other setup -------

        if self._duration:
            top.after(self._duration, self.hide)

        if self._alert:
            top.bell()

        self._toplevel = top

