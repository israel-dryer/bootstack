from __future__ import annotations

from typing import Any

from bootstack.widgets._core.options import OptionRecord, record_to_dict, option_localize


class SelectionGroupMixin:
    """Shared item-management surface for the option-group widgets.

    Mixed into `RadioGroup` and `ToggleGroup`, which both wrap an internal
    composite exposing `keys()`, `configure_item()`, and `remove()`. Each class
    keeps its own `add()` (the option semantics differ) and its own value /
    change surface; only the value-keyed item operations live here.

    The internal composites store only each option's text and value, so the
    mixin keeps the normalized records here (the data bag) — keyed by the
    stringified value, matching the selection variable's coercion — so
    `selection` can hand back each option's full `{text, value, ...extras}`.
    """

    _internal: Any

    def _set_option_records(self, records: list[OptionRecord]) -> None:
        """Seed the option records from a normalized construction list."""
        self._option_records: dict[str, OptionRecord] = {
            str(rec.value): rec for rec in records
        }

    def _add_option_record(self, text: str, value: Any, extras: dict | None = None) -> None:
        """Register a record for an option added at runtime."""
        if not hasattr(self, "_option_records"):
            self._option_records = {}
        self._option_records[str(value)] = OptionRecord(text, value, extras or {})

    def _record_dict_for(self, value: Any) -> dict | None:
        """Return the `{text, value, ...extras}` dict for a value, or None."""
        if value is None or value == "":
            return None
        rec = getattr(self, "_option_records", {}).get(str(value))
        return record_to_dict(rec) if rec is not None else None

    @staticmethod
    def _option_render(icon: Any, disabled: bool, text: str | None = None) -> tuple[dict, dict]:
        """Map the `icon`/`disabled` hints to (internal-add kwargs, extras).

        The internal group forwards `icon`/`state` to each button primitive; the
        extras dict is what `selection` hands back. An icon with a blank `text`
        is inferred as icon-only (the button shows the glyph alone). Returns a
        pair so a single call seeds both the rendered button and the carried
        record.
        """
        add_kwargs: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        if icon is not None:
            add_kwargs["icon"] = icon
            extras["icon"] = icon
            if not (text or "").strip():
                add_kwargs["icon_only"] = True
        if disabled:
            add_kwargs["state"] = "disabled"
            extras["disabled"] = True
        return add_kwargs, extras

    def _resolve_localize(self, record: OptionRecord | None = None, override: Any = None) -> Any:
        """Resolve the effective `localize` for an option.

        Precedence: an explicit per-item `override` (from `add(localize=)`), then
        the option's own `localize` key (carried in its data bag), then the
        widget's group-level `localize=`. `None` at every level means defer to
        the app's `localize_mode`, so it is not forwarded to the item.

        Args:
            record: The option's normalized record, when adding from options.
            override: A per-call `localize` from `add()`.

        Returns:
            The resolved `localize` mode, or `None` to inherit the app default.
        """
        if override is not None:
            return override
        if record is not None:
            item = option_localize(record)
            if item is not None:
                return item
        return getattr(self, "_localize", None)

    def remove(self, value: Any) -> None:
        """Remove the option identified by `value`.

        Args:
            value: The value the option was added with.

        Raises:
            KeyError: If no option with that value exists.
        """
        self._internal.remove(value)
        getattr(self, "_option_records", {}).pop(str(value), None)

    def configure_item(
        self,
        value: Any,
        *,
        label: str | None = None,
        disabled: bool | None = None,
    ) -> None:
        """Update a single option in place, without rebuilding the group.

        Args:
            value: The option to update (the value it was added with).
            label: New display text, when given.
            disabled: When given, disable (`True`) or re-enable (`False`) just
                this option. A later group-level `disabled` change resets every
                option's state, so apply per-option states after it.

        Raises:
            KeyError: If no option with that value exists.
        """
        if label is not None:
            self._internal.configure_item(value, text=label)
        if disabled is not None:
            self._internal.configure_item(value, state="disabled" if disabled else "normal")

    def __len__(self) -> int:
        """The number of options in the group."""
        return len(self._internal.keys())

    def __contains__(self, value: Any) -> bool:
        """Whether an option with the given `value` is in the group."""
        return value in self._internal.keys()