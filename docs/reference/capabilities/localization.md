# Localization

This capability documents one focused aspect of the **widget interface** (Tk/Tcl-style behavior + bootstack extensions).

> **Note**: You typically won’t use `bootstack._core.capabilities.localization` directly. This page describes the behavior that widgets expose.

::: bootstack._core.capabilities.localization
    options:
      show_root_heading: false
      show_source: false
      inherited_members: false
      members:
        - resolve_text
        - resolve_variable_text
        - apply_spec
        - get_current_locale
        - create_formatted_signal
