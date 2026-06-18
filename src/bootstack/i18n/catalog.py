"""Public helpers for extending the runtime translation catalog.

Widget text is localized automatically: in the default `localize_mode="auto"`,
a plain string such as `bs.Label("Save")` is translated through the catalog
when a translation is registered for the current locale, and left as-is
otherwise. These functions register your own strings so that auto-localization
(and the explicit :func:`~bootstack.i18n.L` spec) can resolve them.

Call them any time — including at startup, *before* you build the app. The
registrations persist and apply when widgets resolve their text.
"""

from __future__ import annotations

import sys
from os import PathLike
from pathlib import Path
from typing import Mapping, Optional, Union

from .msgcat import MessageCatalog

__all__ = ["add_translation", "add_translations", "load_po", "load_translations"]


def _resolve_asset(path: Union[str, PathLike[str]]) -> Path:
    """Resolve a project asset path in both a dev run and a packaged build.

    A relative path is tried under the PyInstaller bundle (`sys._MEIPASS`)
    first, then relative to the working directory (the dev case).
    """
    p = Path(path)
    if p.is_absolute():
        return p
    base = getattr(sys, "_MEIPASS", None)
    if base:
        bundled = Path(base) / p
        if bundled.exists():
            return bundled
    return p


def add_translation(locale: str, source: str, translated: str) -> None:
    """Register a single translation for a locale.

    Args:
        locale: Target locale code (e.g. `'es'`, `'fr'`, `'pt_BR'`).
        source: The source string (the message id), e.g. `'Save'`.
        translated: The localized string, e.g. `'Guardar'`.
    """
    MessageCatalog.set(locale, source, translated)


def add_translations(locale: str, translations: Mapping[str, str]) -> int:
    """Register multiple translations for a locale.

    Args:
        locale: Target locale code (e.g. `'es'`).
        translations: A mapping of source string to localized string, e.g.
            `{"Save": "Guardar", "Cancel": "Cancelar"}`.

    Returns:
        The number of translations registered.
    """
    pairs: list[str] = []
    for source, translated in translations.items():
        pairs.extend((source, translated))
    if not pairs:
        return 0
    return MessageCatalog.set_many(locale, *pairs)


def load_po(path: Union[str, PathLike[str]], locale: Optional[str] = None) -> int:
    """Load translations from a gettext `.po` source file into the catalog.

    The `.po` is read directly with Babel — no `msgfmt` compilation and no `.mo`
    files. The path is resolved in both a development run and a PyInstaller build
    (bundle the `.po` with your app, e.g. under `assets/`, which the default
    build config already includes).

    Args:
        path: Path to a `.po` file, relative to the project or absolute.
        locale: Target locale code. If omitted, it is read from the `.po` file's
            `Language:` header.

    Returns:
        The number of translations loaded.
    """
    from babel.messages.pofile import read_po

    resolved = _resolve_asset(path)
    with open(resolved, encoding="utf-8") as handle:
        catalog = read_po(handle)

    loc = locale or (str(catalog.locale) if catalog.locale else None)
    if not loc:
        raise ValueError(
            f"load_po: no locale given and {path} has no 'Language:' header."
        )

    translations = {
        str(message.id): message.string
        for message in catalog
        if message.id and message.string
    }
    return add_translations(loc, translations)


def load_translations(directory: Union[str, PathLike[str]]) -> int:
    """Load translation catalogs from a directory of `.msg` files.

    Each file is named for its locale (e.g. `es.msg`) and holds the locale's
    translations. This is the bulk alternative to :func:`add_translations` for
    projects that keep translations in files.

    Args:
        directory: Path to a directory containing `.msg` catalog files.

    Returns:
        The number of catalog files loaded.
    """
    return MessageCatalog.load(directory)
