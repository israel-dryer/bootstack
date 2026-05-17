"""
Localization integration for bootstack.

Exports MessageCatalog, which bridges Tcl msgcat lookups with compiled
gettext (.mo) catalogs built via Babel.
"""
from .msgcat import MessageCatalog
from .intl_format import IntlFormatter
from .specs import L, LV

__all__ = [
    "MessageCatalog",
    "IntlFormatter",
    "L",
    "LV",
]
