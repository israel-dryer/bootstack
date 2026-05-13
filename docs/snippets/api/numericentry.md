## API reference

### Parameters

| Name | Type | Default | Description |
|---|---|---|---|
| `master` | `Master` | `None` | Parent widget |
| `value` | `int | float` | `0` | Initial numeric value to display |
| `label` | `str` | `None` | Optional label text to display above the entry field |
| `message` | `str` | `None` | Optional message text to display below the entry field |
| `show_spin_buttons` | `bool` | `True` | If True, displays increment/decrement buttons
(plus and minus icons) to the right of the entry |
| `minvalue` | `int | float` | `None` | Minimum allowed value (inclusive) |
| `maxvalue` | `int | float` | `None` | Maximum allowed value (inclusive) |
| `increment` | `int | float` | `1` | Step size for increment/decrement operations |

### Properties

| Name | Type | Description |
|---|---|---|
| `addons` | — | Get the dictionary of inserted addon widgets |
| `decrement_widget` | — | Get the decrement spin button widget |
| `entry_widget` | `TextEntryPart | NumberEntryPart | SpinnerEntryPart` | Get the underlying entry widget |
| `increment_widget` | — | Get the increment spin button widget |
| `label_widget` | — | Get the label widget |
| `message_widget` | — | Get the message widget |
| `signal` | — | Signal linked to the entry text for reactive updates |
| `value` | — | Get or set the parsed value via the underlying entry widget |
| `variable` | — | Tkinter Variable linked to the entry text |

### Methods

| Method | Description |
|---|---|
| `add_validation_rule(rule_type)` | Add a validation rule to the field |
| `decrement()` | Decrement the numeric value by one step |
| `get()` | Return the raw text from the underlying entry widget |
| `increment()` | Increment the numeric value by one step |
| `insert_addon(widget, position, name=None, pack_options=None)` | Insert a widget addon before or after the entry input |

### State

| Method | Description |
|---|---|
| `disable()` | Disable the field, preventing user input |
| `enable()` | Enable the field, allowing user input |
| `readonly(value=None)` | Set or toggle the readonly state of the field |

### Events

| Method | Description |
|---|---|
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
