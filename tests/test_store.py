"""Tests for the public bs.Store preferences store.

Store is plain file I/O (no App required), so these are headless and write to
pytest's tmp_path.
"""
from __future__ import annotations

import json

import pytest

import bootstack as bs
from bootstack.errors import SerializationError


def _store(tmp_path, **kw):
    return bs.Store(path=tmp_path / "settings.json", **kw)


def test_set_get_roundtrip_and_persists(tmp_path):
    s = _store(tmp_path)
    s.set("theme", "dark")
    assert s.get("theme") == "dark"
    # A fresh store over the same file sees the persisted value.
    assert _store(tmp_path).get("theme") == "dark"


def test_get_default_for_missing_key(tmp_path):
    s = _store(tmp_path)
    assert s.get("missing") is None
    assert s.get("missing", "fallback") == "fallback"


def test_mapping_protocol(tmp_path):
    s = _store(tmp_path)
    s["a"] = 1
    assert s["a"] == 1
    assert "a" in s
    assert len(s) == 1
    assert list(s) == ["a"]
    del s["a"]
    assert "a" not in s
    with pytest.raises(KeyError):
        _ = s["a"]
    with pytest.raises(KeyError):
        del s["a"]


def test_delete_is_noop_when_missing(tmp_path):
    s = _store(tmp_path)
    s.delete("nope")  # must not raise
    s["x"] = 1
    s.delete("x")
    assert "x" not in s


def test_update_setdefault_clear(tmp_path):
    s = _store(tmp_path)
    s.update({"a": 1, "b": 2})
    assert s.as_dict() == {"a": 1, "b": 2}
    assert s.setdefault("a", 99) == 1      # existing untouched
    assert s.setdefault("c", 3) == 3       # inserted
    assert sorted(s.keys()) == ["a", "b", "c"]
    s.clear()
    assert len(s) == 0
    assert _store(tmp_path).as_dict() == {}  # cleared state persisted


def test_update_accepts_kwargs(tmp_path):
    s = _store(tmp_path)
    s.update(theme="dark", locale="de_DE")
    assert s.as_dict() == {"theme": "dark", "locale": "de_DE"}
    # mapping and kwargs together; kwargs win on conflict
    s.update({"theme": "light", "extra": 1}, theme="ocean")
    assert s.get("theme") == "ocean"
    assert s.get("extra") == 1
    # persisted
    assert _store(tmp_path).get("theme") == "ocean"


def test_keys_values_items_are_snapshots(tmp_path):
    s = _store(tmp_path)
    s.update({"a": 1, "b": 2})
    assert sorted(s.keys()) == ["a", "b"]
    assert sorted(s.values()) == [1, 2]
    assert dict(s.items()) == {"a": 1, "b": 2}


def test_json_values_supported(tmp_path):
    s = _store(tmp_path)
    s.set("nested", {"list": [1, 2, 3], "flag": True, "n": None})
    assert _store(tmp_path).get("nested") == {"list": [1, 2, 3], "flag": True, "n": None}


def test_non_json_value_raises(tmp_path):
    s = _store(tmp_path)
    with pytest.raises(SerializationError):
        s.set("bad", object())
    # Nothing was stored or written.
    assert "bad" not in s
    assert _store(tmp_path).as_dict() == {}


def test_non_string_key_raises(tmp_path):
    s = _store(tmp_path)
    with pytest.raises(TypeError):
        s.set(5, "v")  # type: ignore[arg-type]


def test_missing_file_starts_empty(tmp_path):
    s = bs.Store(path=tmp_path / "does_not_exist.json")
    assert s.as_dict() == {}


def test_corrupt_file_starts_empty(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text("{not valid json", encoding="utf-8")
    s = bs.Store(path=p)
    assert s.as_dict() == {}


def test_autosave_false_defers_until_save(tmp_path):
    p = tmp_path / "settings.json"
    s = bs.Store(path=p, autosave=False)
    s.set("theme", "dark")
    assert not p.exists()                 # nothing written yet
    assert bs.Store(path=p).as_dict() == {}
    s.save()
    assert bs.Store(path=p).get("theme") == "dark"


def test_reload_picks_up_external_change(tmp_path):
    p = tmp_path / "settings.json"
    s = bs.Store(path=p)
    s.set("a", 1)
    # Simulate another writer.
    p.write_text(json.dumps({"a": 2}), encoding="utf-8")
    assert s.get("a") == 1                # still cached
    s.reload()
    assert s.get("a") == 2


def test_atomic_write_uses_real_filename(tmp_path):
    p = tmp_path / "settings.json"
    s = bs.Store(path=p)
    s.set("k", "v")
    assert p.exists()
    assert not (tmp_path / "settings.json.tmp").exists()  # temp cleaned up


def test_named_store_lands_in_config_dir(tmp_path, monkeypatch):
    # name= resolves under the per-app config dir; redirect it to tmp_path.
    import bootstack._core.paths as paths

    monkeypatch.setattr(paths, "user_config_dir", lambda: tmp_path)
    s = bs.Store("prefs", app_name="MyApp")
    s.set("x", 1)
    expected = tmp_path / "MyApp" / "prefs.json"
    assert expected.exists()
    assert s.path == expected


def test_name_without_app_uses_bootstack(tmp_path, monkeypatch):
    import bootstack._core.paths as paths

    monkeypatch.setattr(paths, "user_config_dir", lambda: tmp_path)
    s = bs.Store("prefs")
    assert s.path == tmp_path / "bootstack" / "prefs.json"
