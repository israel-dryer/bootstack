"""Enhanced event system for bootstack.

This module patches the standard tkinter event system to enable passing custom
data with virtual events. This provides a more powerful and flexible event
handling mechanism than the default tkinter implementation.

Features:
    - Pass custom Python objects as data with virtual events
    - Automatic memory management with LRU cache to prevent leaks
    - Consistent Event objects for both regular and virtual events
    - All standard event attributes preserved (x, y, widget, etc.)
    - Backwards compatible with existing tkinter code

Examples:
    ```python
    import tkinter as tk
    import bootstack as bs

    root = bs.Window()

    def handler(event):
        print(f"Received: {event.data}")

    root.bind('<<CustomEvent>>', handler)
    root.event_generate('<<CustomEvent>>', data={'key': 'value', 'items': [1, 2, 3]})

    root.mainloop()
    ```

Note:
    This module automatically patches tkinter when imported. The patches are
    applied globally and affect all tkinter widgets in the application.
"""

import tkinter as tk
import uuid
import weakref
from collections import OrderedDict
from typing import Any, Callable, Optional, Union


# Global storage for event data with LRU cache behavior
_event_data_cache: OrderedDict[str, Any] = OrderedDict()
_MAX_CACHE_SIZE = 100  # Prevent unbounded growth

# Store original tkinter methods before patching
_original_event_generate: Callable = tk.Misc.event_generate
_original_bind: Callable = tk.Misc.bind
_original_unbind: Callable = tk.Misc.unbind


def _patched_event_generate(
    self: tk.Misc,
    sequence: str,
    data: Optional[Any] = None,
    **kw
) -> None:
    """Enhanced event_generate that supports custom data parameter.

    This patched version of tkinter's event_generate method allows passing
    arbitrary Python objects as event data. The data is stored in a cache
    with a unique identifier that is passed through the event system.

    Args:
        self: The widget instance (automatically provided)
        sequence: Virtual event name (e.g., '<<MyEvent>>')
        data: Optional custom data to attach to the event. Can be any Python object.
        **kw: Additional keyword arguments passed to the original event_generate

    Examples:
        ```python
        widget.event_generate('<<Save>>', data={'filename': 'doc.txt', 'author': 'John'})
        ```

    Note:
        The cache uses LRU eviction to prevent memory leaks. Old entries are
        automatically removed when the cache exceeds _MAX_CACHE_SIZE.
    """
    if data is not None:
        # Generate unique identifier for this data
        guid = str(uuid.uuid4())
        _event_data_cache[guid] = data

        # Limit cache size using LRU eviction
        if len(_event_data_cache) > _MAX_CACHE_SIZE:
            # Remove oldest entry (FIFO from OrderedDict)
            _event_data_cache.popitem(last=False)

        # Pass GUID through tkinter's event system
        kw['data'] = guid

    return _original_event_generate(self, sequence, **kw)


def _patched_bind(
    self: tk.Misc,
    sequence: Optional[str] = None,
    func: Optional[Callable] = None,
    add: Optional[Union[bool, str]] = None
) -> Optional[str]:
    """Enhanced bind that supports data attribute on all events.

    This patched version of tkinter's bind method ensures that:
    1. Virtual events (<<EventName>>) receive custom data if provided
    2. All event objects have a 'data' attribute (None for regular events)
    3. Virtual events get properly formatted Event objects with __str__

    Args:
        self: The widget instance (automatically provided)
        sequence: Event sequence (e.g., '<Button-1>', '<<MyEvent>>')
        func: Callback function to handle the event
        add: If True/'+', add binding without removing existing ones

    Returns:
        Tkinter function name string if binding was created, None otherwise

    Examples:
        ```python
        def handler(event):
            print(f"Event: {event}, Data: {event.data}")

        widget.bind('<<CustomEvent>>', handler)
        ```
    """
    if func is not None and sequence is not None:
        is_virtual = sequence and sequence.startswith('<<')

        if is_virtual:
            # Create wrapper for virtual events to handle data retrieval
            widget_ref = weakref.ref(self)  # Avoid circular references

            def wrapper(
                data_guid, serial, num, height, width, keycode, state, time,
                x, y, x_root, y_root, char, keysym, keysym_num, event_type,
                send_event, delta
            ):
                """Internal wrapper that constructs Event objects for virtual events.

                This function is called by tkinter's event system with all the
                standard event substitution values plus our custom data GUID.
                """

                class VirtualEvent:
                    """Event object for virtual events with enhanced functionality.

                    This class mimics tkinter's Event class but adds:
                    - Custom data attribute from event_generate
                    - Proper __str__ representation showing event details
                    - All standard tkinter event attributes
                    """

                    def __init__(self, widget: tk.Misc) -> None:
                        """Initialize event with standard tkinter attributes.

                        Args:
                            widget: The widget that received the event
                        """
                        self.serial = serial
                        self.num = num
                        self.height = height
                        self.width = width
                        self.keycode = keycode
                        self.state = state
                        self.time = time
                        self.x = x
                        self.y = y
                        self.x_root = x_root
                        self.y_root = y_root
                        self.char = char
                        self.keysym = keysym
                        self.keysym_num = keysym_num
                        self.type = event_type
                        self.send_event = send_event
                        self.delta = delta
                        self.widget = widget
                        self.data: Optional[Any] = None

                    def __str__(self) -> str:
                        """Return human-readable event representation.

                        Returns:
                            Formatted string like: <VirtualEvent type=MyEvent x=10 y=20 data={'key': 'value'}>
                        """
                        # Extract event name from sequence (remove << and >>)
                        event_name = sequence.strip('<').strip('>')
                        parts = [f"type={event_name}"]

                        # Add position if available
                        if self.x is not None and self.x != '??':
                            parts.append(f"x={self.x}")
                        if self.y is not None and self.y != '??':
                            parts.append(f"y={self.y}")

                        # Add data if present (truncate if too long)
                        if self.data is not None:
                            data_repr = repr(self.data)
                            max_length = 50
                            if len(data_repr) > max_length:
                                parts.append(f"data={data_repr[:max_length]}...")
                            else:
                                parts.append(f"data={data_repr}")

                        return f"<VirtualEvent {' '.join(parts)}>"

                    def __repr__(self) -> str:
                        """Return repr string (same as __str__)."""
                        return self.__str__()

                # Retrieve widget from weakref
                widget = widget_ref()
                if widget is None:
                    # Widget was destroyed, clean up cache entry if present
                    if data_guid and data_guid in _event_data_cache:
                        _event_data_cache.pop(data_guid)
                    return

                # Create event object
                event = VirtualEvent(widget)

                # Attach custom data (don't pop yet - multiple handlers may need it)
                if data_guid and data_guid in _event_data_cache:
                    event.data = _event_data_cache[data_guid]
                    # Schedule cleanup after all handlers have run
                    widget.after_idle(lambda: _event_data_cache.pop(data_guid, None))
                else:
                    # Data might have been evicted from cache already
                    event.data = None

                return func(event)

            # Register wrapper function with tkinter
            name = self._register(wrapper)

            # Build the binding script. Its exact shape is load-bearing, and
            # this must stay byte-for-byte what stock `Misc._bind` emits:
            #
            #   * Removing a single handler works by matching the line prefix
            #     `if {"[<funcid> ` — note the TRAILING SPACE, which means the
            #     substitution list below must never be empty. A script in any
            #     other shape is invisible to the matcher, so the handler
            #     survives while its command is deleted, leaving an orphan that
            #     aborts every handler after it. All handlers for an event share
            #     ONE concatenated script, so that took out every handler
            #     registered after the cancelled one (#392).
            #   * The `if {...} == "break"` test is what lets a handler return
            #     'break' to stop the remaining handlers for that event.
            #
            # (The trailing newline only separates this line from the next
            # handler's; Tk inserts its own separator when appending a `+`
            # script. It is kept to match stock exactly.)
            #
            # The substitution list carries %d (our data token) ahead of the
            # standard values; its order must match `wrapper`'s parameters.
            # Substitution codes: https://tcl.tk/man/tcl8.6/TkCmd/bind.htm
            subst = '%d %# %b %h %w %k %s %t %x %y %X %Y %A %K %N %T %E %D'
            cmd = '%sif {"[%s %s]" == "break"} break\n' % (
                '+' if add else '', name, subst
            )

            # Bind to widget
            self.tk.call('bind', self._w, sequence, cmd)

            return name
        else:
            # For regular events, wrap to add data=None attribute
            def regular_wrapper(event):
                """Wrapper for regular events to add consistent data attribute."""
                if not hasattr(event, 'data'):
                    event.data = None
                return func(event)

            return _original_bind(self, sequence, regular_wrapper, add)

    # No function or sequence provided, pass through to original
    return _original_bind(self, sequence, func, add)


def _patched_unbind(
    self: tk.Misc,
    sequence: str,
    funcid: Optional[str] = None
) -> None:
    """Enhanced unbind that cannot disturb the other handlers for an event.

    Stock tkinter removes one handler in two steps: rewrite the binding script
    without that handler's line, then delete the Tcl command behind it. The
    rewrite is correct, but the deletion is immediate — and all handlers for an
    event share ONE script, so if the removal happens *while that script is
    running* (a handler cancelling another handler's subscription), execution
    later reaches the deleted command and the whole script aborts. Every handler
    after the cancelled one is skipped for that dispatch, and the error surfaces
    nowhere Python can see it.

    This version neutralizes the command in place instead, then deletes it once
    the current dispatch has finished. An already-running script then evaluates
    a harmless no-op where the cancelled handler used to be and carries on to
    the handlers after it.

    Args:
        self: The widget instance (automatically provided)
        sequence: Event sequence the handler was bound to
        funcid: Identifier returned by `bind`. When omitted, every handler for
            the sequence is removed and the original implementation is used.
    """
    if funcid is None:
        # Removing everything replaces the whole script, so there is no
        # surviving line that could reference a deleted command.
        return _original_unbind(self, sequence)

    what = ('bind', self._w, sequence)
    try:
        script = self.tk.call(what)
        lines = str(script).split('\n')
        # Must match what `_patched_bind` emits (and stock `Misc._bind`).
        prefix = 'if {"[%s ' % funcid
        keep = [line for line in lines if not line.startswith(prefix)]
        if len(keep) == len(lines):
            # This funcid is not bound to this widget and sequence, so it is
            # not ours to delete — the live binding may be somewhere else, and
            # deleting its command would orphan it. Leave everything alone.
            return
        remaining = '\n'.join(keep)
        self.tk.call(*what, remaining if remaining.strip() else '')
        # Replace the command rather than deleting it, so an in-flight copy of
        # the concatenated script has something harmless to call.
        self.tk.createcommand(funcid, lambda *args: '')
    except tk.TclError:
        return

    def _delete_command() -> None:
        try:
            self.deletecommand(funcid)
        except (tk.TclError, AttributeError):
            # Already swept, most likely because the widget was destroyed
            # before the interpreter went idle. `AttributeError` is that same
            # case seen from the other side: destroy() clears the widget's
            # command bookkeeping, which `deletecommand` then cannot update.
            pass

    try:
        # Deliberately scheduled on the root, not on `self`. Deferred work owned
        # by a widget is torn down with it, and destroying a widget between the
        # cancellation and the next idle point would leave the pending callback
        # referring to a command that destroy() had already deleted — a silent
        # error of exactly the kind this function exists to avoid. The root
        # outlives every widget, and when the root itself goes the pending
        # callback goes with it, which is equally fine: there is nothing left to
        # clean up.
        self._root().after_idle(_delete_command)
    except (tk.TclError, AttributeError):
        # No event loop left to defer onto; nothing can be mid-dispatch either.
        _delete_command()


def cleanup_event_cache() -> None:
    """Manually clear the entire event data cache.

    This function removes all cached event data. It's useful for:
    - Forcing memory cleanup in long-running applications
    - Resetting state during testing
    - Manual intervention when cache grows unexpectedly

    Note:
        Normally cache cleanup is automatic via LRU eviction. Manual cleanup
        should rarely be needed in production code.

    Examples:
        ```python
        from bootstack.events import cleanup_event_cache

        # After processing many events
        cleanup_event_cache()
        ```
    """
    _event_data_cache.clear()


def enable_periodic_cache_cleanup(
    root: tk.Misc,
    interval: int = 60000,
    threshold: int = 10
) -> None:
    """Enable automatic periodic cleanup of the event cache.

    This function sets up a recurring timer that checks the cache size
    and performs cleanup when it exceeds a threshold. This helps prevent
    cache growth in long-running applications that generate many events.

    Args:
        root: Root window or any widget (needed for .after() scheduling)
        interval: Cleanup check interval in milliseconds (default: 60000 = 1 minute)
        threshold: Only clean if cache has more than this many entries (default: 10)

    Examples:
        ```python
        import bootstack as bs
        from bootstack.events import enable_periodic_cache_cleanup

        root = bs.Window()
        enable_periodic_cache_cleanup(root, interval=30000)  # Check every 30 seconds
        root.mainloop()
        ```

    Note:
        This is optional. The LRU cache already prevents unbounded growth.
        Periodic cleanup is only needed for applications that generate
        thousands of events and want more aggressive memory management.
    """
    def cleanup_task():
        """Internal task that performs conditional cache cleanup."""
        if len(_event_data_cache) > threshold:
            # Remove half of the oldest entries
            to_remove = list(_event_data_cache.keys())[:len(_event_data_cache) // 2]
            for key in to_remove:
                _event_data_cache.pop(key, None)

        # Schedule next cleanup
        root.after(interval, cleanup_task)

    # Start the cleanup cycle
    cleanup_task()


def get_cache_size() -> int:
    """Get the current number of entries in the event data cache.

    This is primarily useful for debugging and monitoring cache behavior.

    Returns:
        Number of cached event data objects

    Examples:
        ```python
        from bootstack.events import get_cache_size

        print(f"Current cache size: {get_cache_size()}")
        ```
    """
    return len(_event_data_cache)


def install_enhanced_events() -> None:
    """Install the enhanced event system by patching tkinter methods.

    This function applies monkey patches to tkinter's Misc class, replacing
    event_generate and bind with enhanced versions that support passing custom
    data through virtual events, and unbind with a version that cannot disturb
    the other handlers for an event while one is being removed.

    The patches are applied globally and affect all tkinter widgets
    in the application. This function is called automatically when
    bootstack is imported.

    Note:
        You should not need to call this manually unless you've explicitly
        uninstalled the patches and need to reinstall them.

    Examples:
        ```python
        from bootstack.events import install_enhanced_events

        # Reinstall if needed
        install_enhanced_events()
        ```
    """
    tk.Misc.event_generate = _patched_event_generate
    tk.Misc.bind = _patched_bind
    tk.Misc.unbind = _patched_unbind


def uninstall_enhanced_events() -> None:
    """Restore original tkinter event methods.

    This function removes the patches and restores tkinter to its
    original behavior. Useful for testing or if conflicts arise.

    Warning:
        After calling this, event_generate will no longer accept
        the 'data' parameter, and existing bindings may not work
        as expected.

    Examples:
        ```python
        from bootstack.events import uninstall_enhanced_events

        # Restore original tkinter behavior
        uninstall_enhanced_events()
        ```
    """
    tk.Misc.event_generate = _original_event_generate
    tk.Misc.bind = _original_bind
    tk.Misc.unbind = _original_unbind
    cleanup_event_cache()


__all__ = [
    'cleanup_event_cache',
    'enable_periodic_cache_cleanup',
    'get_cache_size',
    'install_enhanced_events',
    'uninstall_enhanced_events',
]