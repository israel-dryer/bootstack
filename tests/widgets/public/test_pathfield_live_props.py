"""PathField dialog-config options are live properties (#232).

`mode`, `dialog_title`, `start_dir`, `file_filters`, `default_extension`, and
`default_filename` are construction kwargs that can also be read and reassigned
at runtime — so a field can switch from, say, "open" to "save", or update its
start directory based on a prior selection, without being recreated. They route
through the internal PathEntry's configure-delegates.
"""
import pytest

import bootstack as bs


def test_dialog_props_read_construction_values(app):
    pf = bs.PathField(
        mode="save",
        dialog_title="Save as",
        start_dir="/tmp",
        file_filters=[("CSV", "*.csv")],
        default_extension=".csv",
        default_filename="out.csv",
    )
    app._tk_root.update_idletasks()
    assert pf.mode == "save"
    assert pf.dialog_title == "Save as"
    assert pf.start_dir == "/tmp"
    assert pf.file_filters == [("CSV", "*.csv")]
    assert pf.default_extension == ".csv"
    assert pf.default_filename == "out.csv"


def test_dialog_props_are_live(app):
    pf = bs.PathField(mode="open")
    app._tk_root.update_idletasks()
    assert pf.mode == "open"

    pf.mode = "directory"
    pf.start_dir = "/home/user"
    pf.file_filters = [("Images", "*.png *.jpg")]
    pf.dialog_title = "Choose a folder"
    pf.default_extension = ".png"
    pf.default_filename = "image.png"
    app._tk_root.update_idletasks()

    assert pf.mode == "directory"
    assert pf.start_dir == "/home/user"
    assert pf.file_filters == [("Images", "*.png *.jpg")]
    assert pf.dialog_title == "Choose a folder"
    assert pf.default_extension == ".png"
    assert pf.default_filename == "image.png"


def test_unset_dialog_props_default_to_none(app):
    pf = bs.PathField()
    app._tk_root.update_idletasks()
    assert pf.dialog_title is None
    assert pf.start_dir is None
    assert pf.file_filters is None
