# Contributing to bootstack

Thanks for helping improve bootstack! This guide covers development setup, the
pull-request workflow, and how to contribute translations.

bootstack is in pre-release — the public API may still change before 1.0.

## Getting started

1. Fork the repository and clone your fork.
2. Install bootstack in editable mode (Python 3.12+ and Tk/Tcl required):

   ```bash
   python -m pip install -e .
   ```

3. Create a feature branch off `main`:

   ```bash
   git checkout -b feat/my-change
   ```

4. Make your change, then open a pull request with the **base branch** set to
   `main`.

## Reporting bugs and requesting features

Open an issue with a clear title and a minimal, reproducible example. For bugs,
include your OS, Python version, and bootstack version.

## Code contributions

- Keep each pull request focused on one logical change.
- Match the style and conventions of the surrounding code.
- Run the relevant example or tests before opening the PR.
- Reference any issue your PR addresses (e.g. `Closes #123`).

## Translations (localization)

bootstack ships message catalogs for a set of languages, and native-speaker
review is the most valuable way to keep them high quality. The goal is that
every UI string follows proper local conventions, reads idiomatically, and
matches the terminology used in modern desktop applications.

### How to contribute a translation

1. Find the catalog for your language under:

   ```
   src/bootstack/assets/locales/<LOCALE>/LC_MESSAGES/bootstack.po
   ```

   where `<LOCALE>` is the locale code — for example `fr`, `de`, `zh_CN`,
   `pt_BR`, `ar`, or `he`.

2. Review and suggest corrections for:

   - Grammar and idiomatic usage
   - UI terminology accuracy
   - Consistent tone (formal / informal)
   - Industry-standard phrasing (e.g. typical OS dialog wording)
   - String length and truncation risk
   - Right-to-left layout needs (Arabic, Hebrew)

3. Edit the `.po` file on a feature branch off `main` and open a pull request
   (base branch `main`). Name the PR for the language, e.g.
   `i18n(fr): idiomatic fixes to dialog strings`.

If a string is missing or untranslated, leave the `msgstr` empty and note it in
your PR — a maintainer will handle compiling the catalog (`.po` → `.mo`).

## Documentation

Full documentation — guides, the widget catalog, and the API reference — lives
at [bootstack.org](https://bootstack.org).

---

Thank you for helping make bootstack better!
