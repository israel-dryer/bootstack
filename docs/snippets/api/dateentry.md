## API reference

### Parameters

| Name | Type | Default | Description |
|---|---|---|---|
| `master` | `Master` | `None` | Parent widget |
| `value` | `str | date | datetime` | `None` | Initial date value to display (single
mode) |
| `value_format` | `str` | `'longDate'` | Date format pattern to use for parsing and displaying
dates |
| `label` | `str` | `None` | Optional label text to display above the entry field |
| `message` | `str` | `None` | Optional message text to display below the entry field |
| `show_picker_button` | `bool` | `True` | If True, displays the calendar picker button
to the right of the entry |
| `picker_title` | `str` | `None` | Title text for the calendar picker dialog |
| `picker_first_weekday` | `int` | `6` | First day of the week to display in the
calendar picker |
| `selection_mode` | `str` | `'single'` | ``'single'`` (default) for a single date or
``'range'`` for a start/end date range. In range mode the entry
is readonly and the user selects dates exclusively via the picker |
| `start_date` | `date | datetime | str` | `None` | Initial range start date (range
mode only) |
| `end_date` | `date | datetime | str` | `None` | Initial range end date (range mode
only) |
| `min_date` | `date | datetime | str` | `None` | Lower bound for selectable dates |
| `max_date` | `date | datetime | str` | `None` | Upper bound for selectable dates |
| `disabled_dates` | `Iterable` | `None` | Specific dates to disable in the picker |

### Properties

| Name | Type | Description |
|---|---|---|
| `addons` | — | Get the dictionary of inserted addon widgets |
| `date_picker_button` | — | Get the calendar picker button widget |
| `entry_widget` | `TextEntryPart | NumberEntryPart | SpinnerEntryPart` | Get the underlying entry widget |
| `label_widget` | — | Get the label widget |
| `message_widget` | — | Get the message widget |
| `signal` | — | Signal linked to the entry text for reactive updates |
| `value` | — | Selected date (single mode) or ``(start, end)`` tuple (range mode) |
| `variable` | — | Tkinter Variable linked to the entry text |

### Methods

| Method | Description |
|---|---|
| `add_validation_rule(rule_type)` | Add a validation rule to the field |
| `disable()` | Disable the field, preventing user input |
| `enable()` | Enable the field, allowing user input |
| `get()` | Return the raw text from the underlying entry widget |
| `insert_addon(widget, position, name=None, pack_options=None)` | Insert a widget addon before or after the entry input |
| `off_changed(bind_id=None)` | Unsubscribe from ``<<Change>>`` |
| `off_enter(bind_id=None)` | Unsubscribe from ``<Return>`` |
| `off_input(bind_id=None)` | Unsubscribe from ``<<Input>>`` |
| `off_invalid(bind_id=None)` | Unsubscribe from ``<<Invalid>>`` |
| `off_valid(bind_id=None)` | Unsubscribe from ``<<Valid>>`` |
| `off_validated(bind_id=None)` | Unsubscribe from ``<<Validate>>`` |
| `on_changed(callback)` → `str` | Register a callback for ``<<Change>>`` events (fires on commit) |
| `on_enter(callback)` → `str` | Register a callback for ``<Return>`` key events |
| `on_input(callback)` → `str` | Register a callback for ``<<Input>>`` events (fires on each keystroke) |
| `on_invalid(callback)` | Register a callback for ``<<Invalid>>`` events (fires when validation fails) |
| `on_valid(callback)` | Register a callback for ``<<Valid>>`` events (fires when validation passes) |
| `on_validated(callback)` | Register a callback for ``<<Validate>>`` events (fires after any validation) |
| `readonly(value=None)` | Set or toggle the readonly state of the field |
