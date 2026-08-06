"""Pytest plugin: move test_datatable.py's tests to the END of the shared-root leg.

The #417 behavioral test double-clicks a real row, so it needs that row mapped
and hit-testable in the shared root. In natural (alphabetical) order the file
runs at ~23%, while the root is still nearly empty. The handoff records that a
widget packed into an already-full shared root may never get mapped at all — the
failure mode being "passes alone, fails in the suite". Running the file last is
the adversarial case for that.
"""


def pytest_collection_modifyitems(session, config, items):
    late, rest = [], []
    for it in items:
        (late if "test_datatable.py" in str(it.fspath) else rest).append(it)
    items[:] = rest + late
