"""Localization for bootstack.

Public API: ``L`` (lazy translated text) and ``LV`` (lazy locale-formatted
value), used wherever a widget takes text. ``MessageCatalog`` (the gettext /
Tcl-msgcat bridge) and ``IntlFormatter`` (the Babel value formatter) are the
internal engines behind them — importable for internal use but not part of the
public API.
"""
from .msgcat import MessageCatalog
from .intl_format import IntlFormatter
from .specs import L, LV
from .catalog import add_translation, add_translations, load_translations

# Public surface: L / LV and the catalog-extension helpers. MessageCatalog and
# IntlFormatter stay importable (internal engines) but are excluded from __all__.
__all__ = [
    "L",
    "LV",
    "add_translation",
    "add_translations",
    "load_translations",
]
