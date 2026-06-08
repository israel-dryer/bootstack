"""Project a flat adjacency-list data source as a lazy Tree hierarchy.

A data-source-backed tree is "auto-generate the loader from a source": the
source stores flat records that each carry a `parent_field` pointing at their
parent's id (an adjacency list), and the binding projects that flat shape as a
hierarchy by issuing one indexed query per expanded node. Nothing about the flat
`DataSourceProtocol` changes — the hierarchy lives entirely in this binding, so
any source (SQLite, memory, a custom adapter) can back a tree.

Scale comes for free: only the children of *expanded* nodes are ever queried
(one `WHERE parent_field = ?` each), and a single batched existence query per
expand decides which of those children get a chevron.
"""

from __future__ import annotations

from typing import Any, Callable, List, Sequence

from bootstack.data.query import Condition, SortKey, col, normalize_sort_keys

__all__ = ["SourceBinding"]


def _key(value: Any) -> Any:
    """Normalize an identifier for cross-column comparison.

    A record's id and another record's `parent_field` may be stored with
    different types depending on the source — for instance a column whose sampled
    values are all NULL gets TEXT affinity, so its ids can come back as `'1'`
    while a sibling id column returns `1`. They are the same logical key, so
    compare them as strings (NULL stays distinct).
    """
    return None if value is None else str(value)


def _child_condition(parent_field: str, value: Any) -> Condition:
    """Match the rows whose `parent_field` equals `value`.

    A `value` of `None` means "the roots" and matches a NULL/absent parent.
    """
    column = col(parent_field)
    if value is None:
        return column.is_null()
    return column == value


class SourceBinding:
    """Binds a flat adjacency-list data source to a `Tree`.

    Holds the projection config and turns records into node specs, wiring each
    node that has children with a `loader` closure that re-queries on expand.
    """

    def __init__(
        self,
        source: Any,
        *,
        parent_field: str,
        root_value: Any,
        label_field: str,
        icon_field: str | None,
        node_builder: Callable[[dict], dict] | None,
        order: Any = None,
    ) -> None:
        self.source = source
        self.parent_field = parent_field
        self.root_value = root_value
        self.label_field = label_field
        self.icon_field = icon_field
        self.node_builder = node_builder
        self.sort_keys: List[SortKey] = self._normalize_order(order)

    @staticmethod
    def _normalize_order(order: Any) -> List[SortKey]:
        if order is None:
            return []
        keys: Sequence[Any]
        if isinstance(order, (list, tuple)):
            keys = order
        else:
            keys = (order,)
        return normalize_sort_keys(keys)

    # ----- spec building -----

    def _spec(self, record: Any, has_children: bool) -> dict:
        """Turn one raw record into a node spec dict."""
        public = self.source._public_record(record)
        if self.node_builder is not None:
            spec = dict(self.node_builder(public))
        else:
            if self.label_field not in public:
                raise KeyError(
                    f"Tree(data_source=...): no field {self.label_field!r} in the "
                    f"record {dict(public)!r}. Set label_field= to the column that "
                    f"holds the node label, or pass node_builder=."
                )
            spec = {"label": str(public.get(self.label_field, ""))}
            if self.icon_field and public.get(self.icon_field):
                spec["icon"] = public[self.icon_field]
        spec.setdefault("data", dict(public))
        if has_children:
            record_id = self.source._record_id(record)
            spec["loader"] = lambda _node, _pid=record_id: self._fetch(_pid)
        return spec

    def _fetch(self, parent_value: Any) -> List[dict]:
        """Fetch and build the child specs for one parent value."""
        records = self.source._query(
            _child_condition(self.parent_field, parent_value), self.sort_keys
        )
        if not records:
            return []
        ids = [self.source._record_id(r) for r in records]
        with_children = self._records_with_children(ids)
        return [
            self._spec(r, _key(self.source._record_id(r)) in with_children)
            for r in records
        ]

    def _records_with_children(self, ids: Sequence[Any]) -> set:
        """Return the subset of `ids` that are some row's `parent_field` value.

        One batched existence query decides chevrons for a whole sibling group,
        so the cost is O(1 query) per expand regardless of how many children the
        expanded node has.
        """
        ids = [i for i in ids if i is not None]
        if not ids:
            return set()
        rows = self.source._query(col(self.parent_field).is_in(ids), [])
        return {_key(r.get(self.parent_field)) for r in rows}

    def roots(self) -> List[dict]:
        """Build the specs for the top-level (root) nodes."""
        return self._fetch(self.root_value)
