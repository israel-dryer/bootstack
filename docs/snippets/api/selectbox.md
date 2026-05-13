## API reference

### Parameters

| Name | Type | Default | Description |
|---|---|---|---|
| `master` | `Master` | `None` | Parent widget |
| `value` | `str` | `None` | Initial selected value; should typically be present in `items` |
| `items` | `list` | `None` | Sequence of string options to present in the popup list |
| `label` | `str` | `None` | Optional label text shown above the field |
| `message` | `str` | `None` | Optional helper/error message shown below the field |
| `allow_custom_values` | `bool` | `False` | If True, the entry is editable so users can type
arbitrary values in addition to choosing from the list |
| `show_dropdown_button` | `bool` | `True` | If True (default), the dropdown button is shown |
| `dropdown_button_icon` | `str` | `None` | The icon to display on the dropdown button |
| `enable_search` | `bool` | `False` | If True, allows typing in the entry to filter the popup list |

### Properties

| Name | Type | Description |
|---|---|---|
| `addons` | — | Get the dictionary of inserted addon widgets |
| `entry_widget` | `TextEntryPart | NumberEntryPart | SpinnerEntryPart` | Get the underlying entry widget |
| `label_widget` | — | Get the label widget |
| `message_widget` | — | Get the message widget |
| `selected_index` | — | Get or set the selected index |
| `signal` | — | Signal linked to the entry text for reactive updates |
| `value` | — | Get or set the selected value |
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
