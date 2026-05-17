# Internationalization (i18n)

bootstack uses a unified message catalog that bridges Python gettext (compiled
with Babel) and Tcl/Tk msgcat. Catalogs are distributed with the package under
`bootstack/assets/locales`.

Highlights
- Use `_ = MessageCatalog.translate` in code to mark strings.
- The framework auto-initializes the catalog and auto-discovers shipped catalogs.
- Switch language at runtime with `MessageCatalog.locale('de')`.
- A virtual event `<<LocaleChanged>>` is emitted on language changes so UIs can refresh.
- Runtime overrides (`set`, `set_many`) let you add translations not yet in catalogs.

Directory structure
- `src/bootstack/assets/locales/<lang>/LC_MESSAGES/bootstack.po`
- `src/bootstack/assets/locales/<lang>/LC_MESSAGES/bootstack.mo`

Marking strings for translation
- In modules that render UI:
  - `from bootstack.i18n import MessageCatalog`
  - `_ = MessageCatalog.translate`
  - Example: `bs.Label(root, text=_('Cancel'))`
- Formatting:
  - `_("File: %s", name)` uses Python `%` formatting.
  - Legacy Tcl printf like `%1$s` are supported via a formatting fallback.

Language switching
- Change language at runtime:
  - `MessageCatalog.locale('fr')`
  - Bind a refresh: `root.bind('<<LocaleChanged>>', lambda e: refresh())`

Runtime overrides (non-compiled messages)
- Add translations for a locale during runtime:
  - Single: `MessageCatalog.set('fr', 'Hello', 'Bonjour')`
  - Many: `MessageCatalog.set_many('de', 'Open','Oeffnen', 'Cancel','Abbrechen')`
  - Emit refresh if you're already in that locale: `root.event_generate('<<LocaleChanged>>')`

Developer workflow (Babel)
- Config lives at project root: `babel.cfg` (extracts from `src/**/*.py` and `_()`/gettext keywords).
- Use the helper to manage catalogs (defaults to `src/bootstack/assets/locales` and domain `bootstack`):
  - Extract template: `python tools/make_i18n.py extract`
  - Init locales: `python tools/make_i18n.py init -l de fr`
  - Update catalogs: `python tools/make_i18n.py update`
  - Compile catalogs: `python tools/make_i18n.py compile`
- The compiled `.mo` files are shipped in the wheel from `assets/locales`.

Import path
- Public API is available at the top-level namespace:
  - `import bootstack as bs; bs.MessageCatalog, bs.L, bs.LV, bs.IntlFormatter`
  - `from bootstack.i18n import MessageCatalog, L, LV, IntlFormatter`

Contribution notes
- Prefer base locales (`de`, `fr`, `nl`) unless region-specific differences are
  required (for example `pt_BR`).
- Avoid embedding mnemonics `&` in messages; MessageCatalog strips them when rendering.
- Keep message ids consistent (case and punctuation) to avoid duplicates.

Minimum keys to translate for a new language (baseline UI):
- OK, Ok, Retry, Delete, Next, Prev, Previous
- Yes, No, Open, Close, Add, Remove, Submit, Cancel
- Family, Weight, Slant, Effects, Preview, Size
- Should be of data type, Invalid data type
- Number cannot be greater than, Number cannot be less than, Out of range
- The quick brown fox jumps over the lazy dog.
- Font Selector, Color Chooser, Advanced, Themed, Standard
- Current, New, Hue, Sat, Lum, Hex, Red, Green, Blue
- color dropper, Search, Page, of
- Reset table, Columns, Move, Align
- Hide column, Delete column, Show All
- Move to left, Move to right, Move to first, Move to last
- Align left, Align center, Align right
- Sort, Filter, Export, Delete selected rows
- Sort Ascending, Sort Descending, Clear filters
- Filter by cell's value, Hide select rows, Show only select rows
- Export all records, Export current page, Export current selection, Export records in filter
- Move up, Move down, Move to top, Move to bottom
- Mo, Tu, We, Th, Fr, Sa, Su
