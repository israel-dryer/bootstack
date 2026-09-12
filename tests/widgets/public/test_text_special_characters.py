"""Widget text containing `&`, braces or a backslash displays exactly as written."""
import pytest

import bootstack as bs
from bootstack.data import MemoryDataSource
from bootstack.i18n import add_translations


pytestmark = pytest.mark.gui


def _unset(app, name):
    """Remove a Tcl global so a later `info exists` proves nothing set it."""
    app._tk_root.tk.call("unset", "-nocomplain", name)
    assert not int(app._tk_root.tk.call("info", "exists", name))


def _is_set(app, name):
    return bool(int(app._tk_root.tk.call("info", "exists", name)))


def test_braces_and_backslash_render(app):
    texts = ["Test } Brace", "a}b{c", "end\\"]
    assert [bs.Label(t)._internal.cget("text") for t in texts] == texts


def test_text_is_not_run_as_a_script(app):
    _unset(app, "::bs515_plain")
    text = "x } [set ::bs515_plain 1]"
    shown = bs.Label(text)._internal.cget("text")
    assert not _is_set(app, "::bs515_plain")
    assert shown == text


def test_ampersands_render(app):
    texts = ["Test & Ampersand", "Tom && Jerry"]
    assert [bs.Label(t)._internal.cget("text") for t in texts] == texts


def test_registered_translation_with_braces(app):
    # A locale nothing else registers or ships, so the process-wide catalog entry cannot leak.
    add_translations("eo", {"Open } 515": "Malfermi } 515"})
    app.locale = "eo"
    assert bs.Label("Open } 515")._internal.cget("text") == "Malfermi } 515"


def test_formatted_translation_shows_outside_data_verbatim(app):
    # A registered translation used with a format argument: the DataTable status bar
    # formats the end user's search text into it.
    add_translations("eo", {"table.filter_status": "Filtrilo: %s"})
    app.locale = "eo"
    _unset(app, "::bs515_search")
    source = MemoryDataSource()
    source.load([{"id": 1, "name": "Ada"}])
    table = bs.DataTable(data_source=source, columns=["name"], searchable=True)
    search = "x} [set ::bs515_search 1] {"
    table.set_search(search)
    app._tk_root.update_idletasks()
    assert not _is_set(app, "::bs515_search")
    assert table._internal._filter_label.cget("text") == f"Filtrilo: '{search}' in any column"