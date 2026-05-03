# Changelog

## 2.0.0a1 — bootstack rebrand

**Breaking changes:**

- Package renamed from `ttkbootstrap` to `bootstack`. Update all imports:
  ```python
  # Before
  import ttkbootstrap as ttk

  # After
  import bootstack as bs
  ```
- The `bootstyle` widget parameter has been removed. Use `accent` and `variant` instead:
  ```python
  # Before
  ttk.Button(root, text="OK", bootstyle="primary-outline")

  # After
  bs.Button(root, text="OK", accent="primary", variant="outline")
  ```
- Deprecated widget aliases removed (`Checkbutton`, `Radiobutton`, `Labelframe`, `Panedwindow`, `Treeview`, `Tableview`, `DatePicker`, `NavigationView*`). Use the PascalCase names (`CheckButton`, `RadioButton`, etc.).
- CLI entry point renamed from `ttkb` to `bootstack`.
- `Bootstyle` removed from public API. Use `Style` for theme management.
