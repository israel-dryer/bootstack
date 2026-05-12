---
title: SelectBox
---

# SelectBox

`SelectBox` is a selection control that lets users pick one value from a list using a field-like dropdown.

=== "Usage"

    ```python
    import bootstack as bs

    app = bs.App()

    sb = bs.SelectBox(
        app,
        label="Status",
        items=["New", "In Progress", "Blocked", "Done"],
        value="New",
    )
    sb.pack(fill="x", padx=20, pady=20)

    app.mainloop()
    ```

    <div class="app-window">
        <img src="../../assets/widgets-selectbox-quickstart.png" alt="SelectBox quickstart"/>
    </div>

    ## When to use

    Use `SelectBox` when:

    - users should pick one value from a known list
    - search or filtering improves usability
    - you want a field-like dropdown with consistent form patterns

    ### Consider a different control when...

    - you want a simpler, menu-based selector — use [OptionMenu](optionmenu.md)
    - you need single selection among visible options — use [RadioGroup](radiogroup.md)
    - you need direct access to the low-level combobox primitive — use [Combobox](../primitives/combobox.md)

    ## Common options

    | Option | Purpose |
    |---|---|
    | `items` | Sequence of string options shown in the popup. |
    | `value` | Initial selected value; should usually appear in `items`. |
    | `label` | Optional label rendered above the field. |
    | `message` | Optional helper or error message rendered below the field. |
    | `enable_search` | If `True`, typing filters the popup list. |
    | `allow_custom_values` | If `True`, the entry is editable and accepts off-list values. |
    | `show_dropdown_button` | Show the dropdown affordance (forced on with custom values). |
    | `dropdown_button_icon` | Icon name for the dropdown button. Defaults to `"chevron-down"`. |
    | `accent` | Accent token for the focus ring and active border. |
    | `density` | `"default"` or `"compact"`. |

    ## Value model

    | Concept | Where it lives |
    |---|---|
    | Text shown in the entry | `sb.entry_widget.get()` |
    | Committed value | `sb.value` |

    Selecting from the popup updates `value` and emits `<<Change>>`. The text in the entry mirrors the committed value for strict pickers; when `allow_custom_values=True` the displayed text can diverge until the user commits.

    ```python
    print("Current:", sb.value)
    sb.value = "In Progress"
    ```

    ## Items and values

    Update the list at runtime via `configure(items=...)`:

    ```python
    sb.configure(items=["Low", "Medium", "High"])
    ```

    Get or set the selection by index with `selected_index`:

    ```python
    sb.selected_index = 2       # select third item
    print(sb.selected_index)    # -1 if value not in items
    ```

    !!! note "`selected_index` edge cases"
        Setting to `None` clears the selection. Setting to an out-of-range integer raises `IndexError`.

    ## State

    `SelectBox` supports the standard Field state methods:

    ```python
    sb.disable()
    sb.enable()
    sb.readonly(True)
    ```

    `state="disabled"` and `state="readonly"` work as constructor kwargs too.

    ## Add-ons

    `SelectBox` inherits `insert_addon()` from Field. The internal dropdown button is added as an addon named `"dropdown"` at position `"after"`. You can insert additional prefix or suffix addons alongside it — give yours a different name to avoid colliding with the internal one.

    ```python
    sb = bs.SelectBox(app, label="Status", items=["New", "Done"])

    # Prefix icon
    sb.insert_addon(bs.Label, position="before", name="status-icon", icon="circle-fill")

    # Extra suffix action (appears further right than the internal dropdown)
    sb.insert_addon(
        bs.Button,
        position="after",
        name="refresh",
        icon="arrow-clockwise",
        icon_only=True,
        command=lambda: sb.configure(items=fetch_items()),
    )
    ```

    Accepted addon types are `bs.Button`, `bs.Label`, and `bs.CheckToggle`. Retrieve any addon by name via `sb.addons["name"]`. See [TextEntry add-ons](../inputs/textentry.md#add-ons) for the full surface.

    ## Search and filtering

    When `enable_search=True`:

    - typing filters the popup list
    - the first matching item is highlighted automatically
    - closing without explicit selection commits the first match (when `allow_custom_values=False`)

    ```python
    bs.SelectBox(
        app,
        label="Assignee",
        items=["Alice", "Bob", "Charlie", "Diana"],
        enable_search=True,
    )
    ```

    ## Custom values

    When `allow_custom_values=True`:

    - the entry becomes editable
    - the dropdown button is always shown
    - typed text is kept even if it doesn't match an item

    ```python
    bs.SelectBox(
        app,
        label="Tag",
        items=["Bug", "Feature", "Docs"],
        allow_custom_values=True,
    )
    ```

    ## Events

    ```python
    def on_changed(event):
        print("Changed:", event.data["value"])
        print("Previous:", event.data["prev_value"])

    bind_id = sb.on_changed(on_changed)
    sb.off_changed(bind_id)
    ```

    | Event | When it fires |
    |---|---|
    | `<<Change>>` | Selection changes (user or code). `event.data` carries `value`, `prev_value`, `text`. |

    ## Validation

    When `allow_custom_values=False`, values are constrained to `items`. Add explicit rules with the standard Field validation API:

    ```python
    sb.add_validation_rule("required", message="Please select a status")
    ```

    !!! link "See [Validation](../../guides/validation.md) for rules, triggers, and patterns."

    ## Keyboard navigation

    The popup opens on dropdown-button click. When the field is readonly (no search, no custom values), clicking the entry area also opens it.

    When the popup is open:

    | Key | Action |
    |---|---|
    | Arrow Up / Down | Navigate items |
    | Enter | Select highlighted item |
    | Tab | Select highlighted item (search mode) |
    | Escape | Close without selecting |

    Clicking outside also closes the popup.

    ## Reactivity

    Use `textsignal=` for reactive two-way binding to the displayed text:

    ```python
    status = bs.Signal("New")

    sb = bs.SelectBox(
        app,
        label="Status",
        items=["New", "In Progress", "Done"],
        textsignal=status,
    )

    status.subscribe(lambda v: print("status:", v))
    ```

    !!! link "See [Reactivity](../../guides/reactivity.md) for signal patterns."

    ## Localization

    The field label follows the global field localization rules.

    !!! link "See [Localization](../../guides/localization.md) for internationalization patterns."

    ## See also

    - [OptionMenu](optionmenu.md) — simple menu-based selection control
    - [Combobox](../primitives/combobox.md) — classic ttk dropdown with optional typing
    - [RadioGroup](radiogroup.md) — single selection among visible options
    - [Form](../forms/form.md) — declarative selection fields
    - [Validation guide](../../guides/validation.md)
    - [Reactivity guide](../../guides/reactivity.md)

=== "API"

    ::: bootstack.widgets.composites.selectbox.SelectBox
        options:
          inherited_members: true