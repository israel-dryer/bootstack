---
title: SpinnerEntry
---

::: bootstack.widgets.composites.spinnerentry.SpinnerEntry
    options:
      show_root_heading: true
      show_root_toc_entry: true
      show_root_full_path: false
      inherited_members: false
      merge_init_into_class: true
      members: false

## Properties

### `values` — *property* · `List[str]`

Get the list of valid values (text mode only)

### `value` — *property*

Get or set the parsed value via the underlying entry widget

### `entry_widget` — *property* · `TextEntryPart | NumberEntryPart | SpinnerEntryPart`

Get the underlying entry widget

### `label_widget` — *property*

Get the label widget

### `message_widget` — *property*

Get the message widget

### `addons` — *property*

Get the dictionary of inserted addon widgets

### `variable` — *property*

Tkinter Variable linked to the entry text

### `signal` — *property*

Signal linked to the entry text for reactive updates

## Methods

### `get()`

Return the raw text from the underlying entry widget

### `add_validation_rule(rule_type)`

Add a validation rule to the field

### `insert_addon(widget, position, name=None, pack_options=None)`

Insert a widget addon before or after the entry input

## State

### `disable()`

Disable the field, preventing user input

### `enable()`

Enable the field, allowing user input

### `readonly(value=None)`

Set or toggle the readonly state of the field

## Events

### `on_input(callback)` → `str`

Register a callback for ``<<Input>>`` events (fires on each keystroke)

### `off_input(bind_id=None)`

Unsubscribe from ``<<Input>>``

### `on_changed(callback)` → `str`

Register a callback for ``<<Change>>`` events (fires on commit)

### `off_changed(bind_id=None)`

Unsubscribe from ``<<Change>>``

### `on_enter(callback)` → `str`

Register a callback for ``<Return>`` key events

### `off_enter(bind_id=None)`

Unsubscribe from ``<Return>``

### `on_valid(callback)`

Register a callback for ``<<Valid>>`` events (fires when validation passes)

### `off_valid(bind_id=None)`

Unsubscribe from ``<<Valid>>``

### `on_invalid(callback)`

Register a callback for ``<<Invalid>>`` events (fires when validation fails)

### `off_invalid(bind_id=None)`

Unsubscribe from ``<<Invalid>>``

### `on_validated(callback)`

Register a callback for ``<<Validate>>`` events (fires after any validation)

### `off_validated(bind_id=None)`

Unsubscribe from ``<<Validate>>``
