"""Public helpers for extending the runtime translation catalog.

Widget text is localized automatically: in the default ``localize_mode="auto"``,
a plain string such as ``bs.Label("Save")`` is translated through the catalog
when a translation is registered for the current locale, and left as-is
otherwise. These functions register your own strings so that auto-localization
(and the explicit :func:`~bootstack.i18n.L` spec) can resolve them.

They require a running application — call them inside a ``with bs.App():`` block.
"""

from __future__ import annotations

from os import PathLike
from typing import Mapping, Union

from .msgcat import MessageCatalog

__all__ = ["add_translation", "add_translations", "load_translations"]


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
